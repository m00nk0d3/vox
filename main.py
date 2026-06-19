"""
VOX — Main entry point.
Pygame face runs on main thread. Voice loop runs in a daemon thread.
"""

import threading
from stt.transcriber import Transcriber
from llm.brain import Brain
from tts.speaker import Speaker
from memory.store import MemoryStore
from ui.face import run_face
from ui.worker import voice_loop


def main():
    print("VOX is initializing...")
    transcriber = Transcriber()
    brain       = Brain()
    speaker     = Speaker()
    memory      = MemoryStore()

    state_ref = {"state": "idle", "text": "initializing..."}

    t = threading.Thread(
        target=voice_loop,
        args=(transcriber, brain, speaker, memory, state_ref),
        daemon=True,
    )
    t.start()

    speaker.speak("VOX online.")
    run_face(state_ref)   # blocks on main thread until Esc


if __name__ == "__main__":
    main()
