"""
Wake word detector — openWakeWord with onnxruntime backend.
Streams mic in 80ms chunks and blocks until "hey jarvis" is detected.
"""

import numpy as np
import pyaudio
from openwakeword.model import Model
import config

CHUNK = 1280   # 80ms at 16kHz — required by openWakeWord


class WakeWordDetector:
    def __init__(self):
        print(f"Loading wake word model '{config.WAKE_WORD_MODEL}'...")
        self.model = Model(
            wakeword_models=[config.WAKE_WORD_MODEL],
            inference_framework="onnx",
        )
        self.audio = pyaudio.PyAudio()
        print("Wake word ready. Say 'hey Jarvis' to activate VOX.")

    def wait_for_wake_word(self, cooldown: float = 2.0):
        """Block until the wake word is detected above threshold.
        
        cooldown: seconds to drain stale audio before listening (prevents
        TTS bleed from immediately re-triggering detection).
        """
        # Reset model state so previous audio scores don't carry over
        self.model.reset()

        stream = self.audio.open(
            rate=config.AUDIO_SAMPLE_RATE,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=CHUNK,
        )
        try:
            # Drain stale mic buffer during cooldown without scoring
            drain_chunks = int(cooldown * config.AUDIO_SAMPLE_RATE / CHUNK)
            for _ in range(drain_chunks):
                stream.read(CHUNK, exception_on_overflow=False)

            while True:
                raw  = stream.read(CHUNK, exception_on_overflow=False)
                data = np.frombuffer(raw, dtype=np.int16)
                preds = self.model.predict(data)
                score = preds.get(config.WAKE_WORD_MODEL, 0)
                if score >= config.WAKE_WORD_THRESHOLD:
                    print(f"Wake word detected! (score: {score:.2f})")
                    return
        finally:
            stream.stop_stream()
            stream.close()
