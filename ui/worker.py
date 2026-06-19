"""
Voice worker — runs STT -> LLM -> TTS in a background thread.
Writes state updates to a shared dict read by the pygame face loop.
"""

import time


def voice_loop(transcriber, brain, speaker, memory, state_ref: dict):
    """Run forever in a daemon thread. Updates state_ref for the UI."""
    import config

    if config.WAKE_WORD_ENABLED:
        from wake.detector import WakeWordDetector
        detector = WakeWordDetector()

    state_ref["state"] = "idle"
    state_ref["text"]  = "say hey jarvis" if config.WAKE_WORD_ENABLED else "press enter"

    while True:
        # ── Wait for activation ───────────────────────────────────────────────
        if config.WAKE_WORD_ENABLED:
            state_ref.update({"state": "idle", "text": "say hey jarvis"})
            detector.wait_for_wake_word()
        else:
            input("\n[Press Enter to speak] ")

        # ── Listen ────────────────────────────────────────────────────────────
        state_ref.update({"state": "listening", "text": ""})
        t0        = time.time()
        user_text = transcriber.listen()
        t_stt     = time.time() - t0

        if not user_text:
            state_ref.update({"state": "idle", "text": "didn'\''t catch that"})
            continue

        print(f"You: {user_text}  [STT: {t_stt:.1f}s]")
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
