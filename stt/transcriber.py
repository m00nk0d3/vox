"""
STT module — Speech-to-text via faster-whisper.
Records until silence is detected (VAD), not a fixed duration.
"""

import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
import config

CHUNK_SECONDS = 0.1  # Process audio in 100ms chunks


class Transcriber:
    def __init__(self):
        print(f"Loading Whisper model '{config.STT_MODEL}'...")
        self.model = WhisperModel(
            config.STT_MODEL,
            device=config.STT_DEVICE,
            compute_type=config.STT_COMPUTE_TYPE,
        )
        print("Whisper ready.")

    def listen(self) -> str:
        """Record until silence, then transcribe."""
        audio = self._record_until_silence()
        if len(audio) == 0:
            return ""
        return self._transcribe(audio)

    def _record_until_silence(self) -> np.ndarray:
        """Stream mic input and stop after VAD_SILENCE_DURATION of quiet."""
        sample_rate = config.AUDIO_SAMPLE_RATE
        chunk_size = int(sample_rate * CHUNK_SECONDS)

        silence_chunks_needed = int(config.VAD_SILENCE_DURATION / CHUNK_SECONDS)
        max_chunks = int(config.VAD_MAX_DURATION / CHUNK_SECONDS)

        frames = []
        silence_chunks = 0
        speech_started = False

        print("Waiting for speech...")

        with sd.InputStream(samplerate=sample_rate, channels=1, dtype="float32") as stream:
            for _ in range(max_chunks):
                chunk, _ = stream.read(chunk_size)
                chunk_flat = chunk.flatten()
                rms = float(np.sqrt(np.mean(chunk_flat ** 2)))

                if rms > config.VAD_SILENCE_THRESHOLD:
                    if not speech_started:
                        print("Listening...")
                        speech_started = True
                    silence_chunks = 0
                    frames.append(chunk_flat)
                elif speech_started:
                    frames.append(chunk_flat)
                    silence_chunks += 1
                    if silence_chunks >= silence_chunks_needed:
                        break

        if not frames:
            return np.array([], dtype=np.float32)

        return np.concatenate(frames)

    def _transcribe(self, audio: np.ndarray) -> str:
        """Run Whisper inference on raw audio array."""
        segments, _ = self.model.transcribe(
            audio,
            language=config.STT_LANGUAGE,
            beam_size=5,
        )
        return " ".join(seg.text.strip() for seg in segments).strip()
