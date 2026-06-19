"""
Wake word module — openWakeWord integration.
Only used when config.WAKE_WORD_ENABLED = True.
"""

import pyaudio
import numpy as np
from openwakeword.model import Model
import config

CHUNK = 1280  # openWakeWord expects 80ms frames at 16kHz


class WakeWordDetector:
    def __init__(self):
        print(f"Loading wake word model '{config.WAKE_WORD_MODEL}'...")
        self.model = Model(wakeword_models=[config.WAKE_WORD_MODEL])
        self.audio = pyaudio.PyAudio()
        print("Wake word detector ready.")

    def wait_for_wake_word(self):
        """Block until the wake word is detected."""
        stream = self.audio.open(
            rate=config.AUDIO_SAMPLE_RATE,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=CHUNK,
        )

        print("Waiting for wake word...")
        try:
            while True:
                raw = stream.read(CHUNK, exception_on_overflow=False)
                audio_data = np.frombuffer(raw, dtype=np.int16)
                predictions = self.model.predict(audio_data)

                score = predictions.get(config.WAKE_WORD_MODEL, 0)
                if score >= config.WAKE_WORD_THRESHOLD:
                    print("Wake word detected!")
                    break
        finally:
            stream.stop_stream()
            stream.close()
