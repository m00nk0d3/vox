"""
TTS module — Text-to-speech via Kokoro.
"""

import sounddevice as sd
import numpy as np
from kokoro import KPipeline
import config


class Speaker:
    def __init__(self):
        print("Loading Kokoro TTS pipeline...")
        self.pipeline = KPipeline(lang_code="a")  # 'a' = American English
        print("Kokoro ready.")

    def speak(self, text: str):
        """Synthesize text and play it through the default speaker."""
        if not text:
            return

        audio_chunks = []
        for _, _, audio in self.pipeline(
            text,
            voice=config.TTS_VOICE,
            speed=config.TTS_SPEED,
        ):
            audio_chunks.append(audio)

        if audio_chunks:
            full_audio = np.concatenate(audio_chunks)
            sd.play(full_audio, samplerate=24000)
            sd.wait()
