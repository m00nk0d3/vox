"""
TTS module — Text-to-speech via Kokoro.
Uses a background thread + queue so generation and playback overlap.
"""

import queue
import threading
import sounddevice as sd
import numpy as np
from kokoro import KPipeline
import config


class Speaker:
    def __init__(self):
        print("Loading Kokoro TTS pipeline...")
        self.pipeline = KPipeline(lang_code="a")
        self._queue = queue.Queue()
        self._thread = threading.Thread(target=self._playback_worker, daemon=True)
        self._thread.start()
        print("Kokoro ready.")

    def speak(self, text: str):
        """Synthesize and queue audio — returns immediately, plays in background."""
        if not text:
            return
        audio = self._synthesize(text)
        if audio is not None:
            self._queue.put(audio)

    def wait_until_done(self):
        """Block until the playback queue is fully drained."""
        self._queue.join()

    def _synthesize(self, text: str) -> np.ndarray | None:
        chunks = []
        for _, _, audio in self.pipeline(
            text,
            voice=config.TTS_VOICE,
            speed=config.TTS_SPEED,
        ):
            chunks.append(audio)
        return np.concatenate(chunks) if chunks else None

    def _playback_worker(self):
        """Background thread: plays queued audio chunks in order."""
        while True:
            audio = self._queue.get()
            try:
                sd.play(audio, samplerate=24000)
                sd.wait()
            finally:
                self._queue.task_done()
