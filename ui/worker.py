"""
Voice worker — runs STT -> LLM -> TTS in a background thread.
After wake word, stays active for ACTIVE_TIMEOUT seconds of silence.
"""

import time
import threading


def voice_loop(transcriber, brain, speaker, memory, state_ref: dict):
    import config

    if config.WAKE_WORD_ENABLED:
        from wake.detector import WakeWordDetector
        detector = WakeWordDetector()

    idle_text = "say hey jarvis" if config.WAKE_WORD_ENABLED else "press enter"

    def go_idle():
        state_ref.update({"state": "idle", "text": idle_text})

    go_idle()

    while True:
        # ── Wait for activation ───────────────────────────────────────────────
        if config.WAKE_WORD_ENABLED:
            detector.wait_for_wake_word()
        else:
            input("\n[Press Enter to speak] ")

        # ── Active conversation window ────────────────────────────────────────
        # Stay active until ACTIVE_TIMEOUT seconds of silence with no speech
        session_active = True
        while session_active:
            state_ref.update({"state": "listening", "text": ""})
            t0        = time.time()
            user_text = transcriber.listen()
            elapsed   = time.time() - t0

            if not user_text:
                # No speech detected — go idle, require wake word again
                print("No speech detected, going idle.")
                go_idle()
                session_active = False
                continue

            print(f"You: {user_text}  [STT: {elapsed:.1f}s]")
            state_ref.update({"state": "thinking", "text": user_text})

            history       = memory.get_history()
            full_response = ""
            first         = True
            t_llm         = time.time()

            for sentence in brain.think_stream(user_text, history):
                if first:
                    print(f"VOX [first token: {time.time() - t_llm:.1f}s]: ", end="", flush=True)
                    first = False
                print(sentence, end=" ", flush=True)
                state_ref.update({"state": "speaking", "text": sentence})
                speaker.speak(sentence)
                full_response += sentence + " "

            print(f"\n  [LLM total: {time.time() - t_llm:.1f}s]")
            speaker.wait_until_done()
            memory.add_turn(user_text, full_response.strip())

            # After responding, give a short window to keep talking
            # VAD will handle the actual silence — if nothing is said,
            # listen() returns empty and we exit the session
            state_ref.update({"state": "listening", "text": "..."})
