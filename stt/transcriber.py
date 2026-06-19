"""
STT module — Speech-to-text via faster-whisper.
"""

import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
import config


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
        """Record audio from mic and return transcribed text."""
        audio = self._record()
        return self._transcribe(audio)

    def _record(self) -> np.ndarray:
        """Record a fixed-length audio chunk from the default mic."""
        frames = int(config.AUDIO_SAMPLE_RATE * config.AUDIO_CHUNK_SECONDS)
        audio = sd.rec(
            frames,
            samplerate=config.AUDIO_SAMPLE_RATE,
            channels=config.AUDIO_CHANNELS,
            dtype="float32",
        )
        sd.wait()
        return audio.flatten()

    def _transcribe(self, audio: np.ndarray) -> str:
        """Run Whisper inference on raw audio array."""
        segments, _ = self.model.transcribe(
            audio,
            language=config.STT_LANGUAGE,
            beam_size=5,
        )
        return " ".join(seg.text.strip() for seg in segments).strip()
