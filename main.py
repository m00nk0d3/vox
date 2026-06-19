"""
VOX — Main entry point
Launches the Qt face UI and kicks off the voice worker thread.
"""

import sys
from PySide6.QtWidgets import QApplication

from stt.transcriber import Transcriber
from llm.brain import Brain
from tts.speaker import Speaker
from memory.store import MemoryStore
from ui.face import VoxWindow
from ui.worker import VoiceWorker
import config


def main():
    app = QApplication(sys.argv)

    print("VOX is initializing...")
    transcriber = Transcriber()
    brain       = Brain()
    speaker     = Speaker()
    memory      = MemoryStore()

    window = VoxWindow()
    window.show()

    worker = VoiceWorker(transcriber, brain, speaker, memory)
    worker.state_changed.connect(window.set_state)
    worker.log.connect(print)
    worker.start()

    speaker.speak("VOX online.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
