"""
Voice worker — runs STT -> LLM -> TTS in a background thread.
After wake word, stays active for ACTIVE_TIMEOUT seconds of silence.
"""

import time
import re
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
                # No speech detected — wait for TTS to finish, then go idle
                speaker.wait_until_done()
                print("No speech detected, going idle.")
                go_idle()
                session_active = False
                continue

            print(f"You: {user_text}  [STT: {elapsed:.1f}s]")

            # Sleep on command — short, direct intent only (long sentences are questions, not commands)
            is_short = len(user_text.split()) <= 8
            if is_short and any(re.search(p, user_text.lower()) for p in config.SLEEP_COMMANDS):
                state_ref.update({"state": "speaking", "text": ""})
                for sentence in brain.think_stream(user_text, memory.get_history()):
                    speaker.speak(sentence)
                    state_ref.update({"state": "speaking", "text": sentence})
                speaker.wait_until_done()
                go_idle()
                session_active = False
                continue

            state_ref.update({"state": "thinking", "text": user_text})

            history       = memory.get_history()
            full_response = ""
            first         = True
            t_llm         = time.time()

            try:
                for sentence in brain.think_stream(user_text, history):
                    if first:
                        print(f"VOX [first token: {time.time() - t_llm:.1f}s]: ", end="", flush=True)
                        first = False
                    print(sentence, end=" ", flush=True)
                    state_ref.update({"state": "speaking", "text": sentence})
                    speaker.speak(sentence)
                    full_response += sentence + " "
            except Exception as e:
                err = str(e)
                if "rate_limit" in err.lower() or "429" in err:
                    msg = "rate limit hit, give me a minute"
                else:
                    msg = "something went wrong, try again"
                print(f"\nError: {e}")
                state_ref.update({"state": "speaking", "text": msg})
                speaker.speak(msg)
                speaker.wait_until_done()
                go_idle()
                session_active = False
                continue

            print(f"\n  [LLM total: {time.time() - t_llm:.1f}s]")
            speaker.wait_until_done()
            memory.add_turn(user_text, full_response.strip())

            # After responding, give a short window to keep talking
            # VAD will handle the actual silence — if nothing is said,
            # listen() returns empty and we exit the session
            state_ref.update({"state": "listening", "text": "..."})
