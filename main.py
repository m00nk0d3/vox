"""
VOX — Main entry point
Runs the voice conversation loop.
"""

import time
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

    # Pre-warm Ollama so first real response isn't cold-start slow
    print("Warming up Ollama...")
    _ = brain.think("hi", [])
    print("Warm-up done.")

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

            t0 = time.time()
            print("Listening...")
            user_text = transcriber.listen()
            t_stt = time.time()

            if not user_text:
                print("Didn't catch that.")
                continue

            print(f"You: {user_text}  [STT: {t_stt - t0:.1f}s]")

            history = memory.get_history()

            full_response = ""
            first = True
            t_llm_start = time.time()
            for sentence in brain.think_stream(user_text, history):
                if first:
                    print(f"VOX [LLM first token: {time.time() - t_llm_start:.1f}s]: ", end="", flush=True)
                    first = False
                print(sentence, end=" ", flush=True)
                speaker.speak(sentence)
                full_response += sentence + " "
            t_llm_end = time.time()
            print(f"  [LLM total: {t_llm_end - t_llm_start:.1f}s]")

            speaker.wait_until_done()
            full_response = full_response.strip()
            memory.add_turn(user_text, full_response)

        except KeyboardInterrupt:
            print("\nShutting down VOX. Later.")
            break


if __name__ == "__main__":
    main()
