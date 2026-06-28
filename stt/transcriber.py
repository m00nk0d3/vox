"""
STT module — records via WebRTC VAD (speech-only), transcribes locally with faster-whisper.
WebRTC VAD ignores music/noise and only triggers on human voice.
"""

import io
import wave

import numpy as np
import sounddevice as sd
import webrtcvad

import config

# WebRTC VAD requires 10ms, 20ms, or 30ms frames at 16kHz
FRAME_MS = 30  # ms per frame
FRAME_SIZE = int(config.AUDIO_SAMPLE_RATE * FRAME_MS / 1000)  # samples per frame
VAD_AGGRESSIVENESS = 3  # 0–3, higher = stricter speech detection


# Known Whisper hallucinations — discard these silently
HALLUCINATIONS = {
    "thank you",
    "thank you.",
    "thanks for watching",
    "thanks for watching.",
    "you",
    "you.",
    "bye",
    "bye.",
    ".",
    "..",
    "...",
    "thanks",
    "thanks.",
    "thank you so much",
    "thank you very much",
    "please subscribe",
    "subtitles by",
    "transcribed by",
    "translated by",
}


class Transcriber:
    def __init__(self):
        self.vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)

        from faster_whisper import WhisperModel

        self.model = WhisperModel(
            config.STT_MODEL,
            device=config.STT_DEVICE,
            compute_type=config.STT_COMPUTE_TYPE,
        )
        print(f"STT using local Whisper ({config.STT_MODEL}).")

    def listen(self, on_speech_start=None) -> str:
        audio = self._record_until_silence(on_speech_start=on_speech_start)
        if len(audio) == 0:
            return ""
        text = self._transcribe_local(audio)
        if text.lower().strip() in HALLUCINATIONS:
            print(f"[STT] Hallucination filtered: {repr(text)}")
            return ""
        return text

    def _is_speech(self, frame: np.ndarray) -> bool:
        """Return True if WebRTC VAD detects human speech in this frame."""
        pcm = (frame * 32767).astype(np.int16).tobytes()
        try:
            return self.vad.is_speech(pcm, config.AUDIO_SAMPLE_RATE)
        except Exception:
            return False

    def _record_until_silence(self, on_speech_start=None) -> np.ndarray:
        silence_frames_needed = int(config.VAD_SILENCE_DURATION * 1000 / FRAME_MS)
        max_speech_frames = int(config.VAD_MAX_DURATION * 1000 / FRAME_MS)

        frames = []
        silence_frames = 0
        speech_started = False

        print("Waiting for speech...")

        with sd.InputStream(
            samplerate=config.AUDIO_SAMPLE_RATE, channels=1, dtype="float32"
        ) as stream:
            while True:
                chunk, _ = stream.read(FRAME_SIZE)
                frame = chunk.flatten()

                is_speech = self._is_speech(frame)

                if is_speech:
                    if not speech_started:
                        print("Listening...")
                        speech_started = True
                        if on_speech_start:
                            on_speech_start()
                    silence_frames = 0
                    frames.append(frame)

                    if len(frames) >= max_speech_frames:
                        break

                elif speech_started:
                    frames.append(frame)
                    silence_frames += 1
                    if silence_frames >= silence_frames_needed:
                        break
                # else: no speech yet — wait forever

        if not frames:
            return np.array([], dtype=np.float32)

        # Require at least 0.5s of actual speech frames before sending to Whisper
        speech_seconds = len(frames) * FRAME_MS / 1000
        if speech_seconds < 0.5:
            return np.array([], dtype=np.float32)

        return np.concatenate(frames)

    def _transcribe_local(self, audio: np.ndarray) -> str:
        """Run local faster-whisper inference."""
        segments, _ = self.model.transcribe(
            audio,
            language=config.STT_LANGUAGE,
            beam_size=1,
        )
        return " ".join(seg.text.strip() for seg in segments).strip()
