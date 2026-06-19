"""
VOX — Main entry point
Runs the voice conversation loop.
"""

from stt.transcriber import Transcriber
from llm.brain import Brain
from tts.speaker import Speaker
from wake.detector import WakeWordDetector
from memory.store import MemoryStore
import config


def main():
    print("VOX is initializing...")

    transcriber = Transcriber()
    brain = Brain()
    speaker = Speaker()
    memory = MemoryStore()

    if config.WAKE_WORD_ENABLED:
        wake_detector = WakeWordDetector()
        print(f"Listening for wake word: '{config.WAKE_WORD_MODEL}'")
    else:
        print("Wake word disabled. Press Enter to start speaking.")

    speaker.speak("VOX online. How can I help?")

    while True:
        try:
            if config.WAKE_WORD_ENABLED:
                wake_detector.wait_for_wake_word()
            else:
                input("\n[Press Enter to speak] ")

            print("Listening...")
            user_text = transcriber.listen()

            if not user_text:
                print("Didn't catch that.")
                continue

            print(f"You: {user_text}")

            history = memory.get_history()
            response = brain.think(user_text, history)
            memory.add_turn(user_text, response)

            print(f"VOX: {response}")
            speaker.speak(response)

        except KeyboardInterrupt:
            print("\nShutting down VOX. Later.")
            break


if __name__ == "__main__":
    main()
