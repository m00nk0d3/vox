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

    def listen(self) -> str:
        audio = self._record_until_silence()
        if len(audio) == 0:
            return ""
        if config.STT_PROVIDER == "groq":
            return self._transcribe_groq(audio)
        return self._transcribe_local(audio)

    def _is_speech(self, frame: np.ndarray) -> bool:
        """Return True if WebRTC VAD detects human speech in this frame."""
        pcm = (frame * 32767).astype(np.int16).tobytes()
        try:
            return self.vad.is_speech(pcm, config.AUDIO_SAMPLE_RATE)
        except Exception:
            return False

    def _record_until_silence(self) -> np.ndarray:
        silence_frames_needed = int(config.VAD_SILENCE_DURATION * 1000 / FRAME_MS)
        max_speech_frames     = int(config.VAD_MAX_DURATION * 1000 / FRAME_MS)

        frames         = []
        silence_frames = 0
        speech_started = False

        print("Waiting for speech...")

        with sd.InputStream(samplerate=config.AUDIO_SAMPLE_RATE, channels=1, dtype="float32") as stream:
            while True:
                chunk, _ = stream.read(FRAME_SIZE)
                frame    = chunk.flatten()

                is_speech = self._is_speech(frame)

                if is_speech:
                    if not speech_started:
                        print("Listening...")
                        speech_started = True
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
