"""
STT module — records via WebRTC VAD (speech-only), transcribes via Groq Whisper API or local faster-whisper.
WebRTC VAD ignores music/noise and only triggers on human voice.
"""

import io
import wave
import webrtcvad
import sounddevice as sd
import numpy as np
import config

# WebRTC VAD requires 10ms, 20ms, or 30ms frames at 16kHz
FRAME_MS    = 30                              # ms per frame
FRAME_SIZE  = int(config.AUDIO_SAMPLE_RATE * FRAME_MS / 1000)  # samples per frame
VAD_AGGRESSIVENESS = 3                        # 0–3, higher = stricter speech detection
VAD_SPEECH_CONFIRM_FRAMES = 8                 # Consecutive speech frames needed (8 × 30ms = 240ms)
VAD_SPEECH_RMS_GATE = 0.02                    # Minimum RMS energy — filters quiet music bleed


# Known Whisper hallucinations — discard these silently
HALLUCINATIONS = {
    "thank you", "thank you.", "thanks for watching", "thanks for watching.",
    "you", "you.", "bye", "bye.", ".", "..", "...", "thanks", "thanks.",
    "thank you so much", "thank you very much", "please subscribe",
    "subtitles by", "transcribed by", "translated by",
}


class Transcriber:
    def __init__(self):
        self.vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)

        if config.STT_PROVIDER == "groq":
            from groq import Groq
            self.client = Groq(api_key=config.GROQ_API_KEY)
            print(f"STT using Groq Whisper ({config.STT_GROQ_MODEL}).")
        else:
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
        text = self._transcribe_groq(audio) if config.STT_PROVIDER == "groq" else self._transcribe_local(audio)
        if text.lower().strip() in HALLUCINATIONS:
            print(f"[STT] Hallucination filtered: {repr(text)}")
            return ""
        return text

    def _is_speech(self, frame: np.ndarray) -> bool:
        """Return True if frame passes RMS gate AND WebRTC VAD detects speech."""
        rms = float(np.sqrt(np.mean(frame ** 2)))
        if rms < VAD_SPEECH_RMS_GATE:
            return False  # Too quiet — music bleed or silence
        pcm = (frame * 32767).astype(np.int16).tobytes()
        try:
            return self.vad.is_speech(pcm, config.AUDIO_SAMPLE_RATE)
        except Exception:
            return False

    def _record_until_silence(self, on_speech_start=None) -> np.ndarray:
        silence_frames_needed = int(config.VAD_SILENCE_DURATION * 1000 / FRAME_MS)
        max_speech_frames     = int(config.VAD_MAX_DURATION * 1000 / FRAME_MS)

        frames              = []
        silence_frames      = 0
        speech_started      = False
        consecutive_speech  = 0  # Must hit this before declaring speech started

        print("Waiting for speech...")

        with sd.InputStream(samplerate=config.AUDIO_SAMPLE_RATE, channels=1, dtype="float32") as stream:
            while True:
                chunk, _ = stream.read(FRAME_SIZE)
                frame    = chunk.flatten()

                is_speech = self._is_speech(frame)

                if is_speech:
                    consecutive_speech += 1
                    if not speech_started:
                        if consecutive_speech >= VAD_SPEECH_CONFIRM_FRAMES:
                            print("Listening...")
                            speech_started = True
                            if on_speech_start:
                                on_speech_start()
                        else:
                            # Still accumulating confirmation frames
                            frames.append(frame)
                            continue
                    silence_frames = 0
                    frames.append(frame)

                    if len(frames) >= max_speech_frames:
                        break

                else:
                    consecutive_speech = 0
                    if speech_started:
                        frames.append(frame)
                        silence_frames += 1
                        if silence_frames >= silence_frames_needed:
                            break
                    else:
                        frames = []  # Discard pre-confirmation frames on silence

        if not frames:
            return np.array([], dtype=np.float32)

        # Require at least 0.5s of actual speech frames before sending to Whisper
        speech_seconds = len(frames) * FRAME_MS / 1000
        if speech_seconds < 0.5:
            return np.array([], dtype=np.float32)

        return np.concatenate(frames)

    def _transcribe_groq(self, audio: np.ndarray) -> str:
        """Send audio to Groq Whisper API."""
        pcm = (audio * 32767).astype(np.int16)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(config.AUDIO_SAMPLE_RATE)
            wf.writeframes(pcm.tobytes())
        buf.seek(0)

        result = self.client.audio.transcriptions.create(
            file=("audio.wav", buf, "audio/wav"),
            model=config.STT_GROQ_MODEL,
            language=config.STT_LANGUAGE,
        )
        return result.text.strip()

    def _transcribe_local(self, audio: np.ndarray) -> str:
        """Run local faster-whisper inference."""
        segments, _ = self.model.transcribe(
            audio,
            language=config.STT_LANGUAGE,
            beam_size=1,
        )
        return " ".join(seg.text.strip() for seg in segments).strip()
