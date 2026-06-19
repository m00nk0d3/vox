"""
Voice worker — runs the STT → LLM → TTS loop in a QThread
so the Qt UI stays responsive on the main thread.
"""

import time
from PySide6.QtCore import QThread, Signal


class VoiceWorker(QThread):
    state_changed = Signal(str, str)   # (state, subtitle_text)
    log = Signal(str)                  # debug/timing messages

    def __init__(self, transcriber, brain, speaker, memory):
        super().__init__()
        self.transcriber = transcriber
        self.brain       = brain
        self.speaker     = speaker
        self.memory      = memory

    def run(self):
        self.state_changed.emit("idle", "press enter to speak")

        while True:
            input("\n[Press Enter to speak] ")

            # ── Listen ────────────────────────────────────────────────────────
            self.state_changed.emit("listening", "")
            t0 = time.time()
            user_text = self.transcriber.listen()
            t_stt = time.time() - t0

            if not user_text:
                self.state_changed.emit("idle", "didn't catch that")
                continue

            self.log.emit(f"You: {user_text}  [STT: {t_stt:.1f}s]")
            self.state_changed.emit("thinking", user_text)

            # ── Think ─────────────────────────────────────────────────────────
            history      = self.memory.get_history()
            full_response = ""
            first        = True
            t_llm        = time.time()

            for sentence in self.brain.think_stream(user_text, history):
                elapsed = time.time() - t_llm
                if first:
                    self.log.emit(f"VOX [first token: {elapsed:.1f}s]: ")
                    first = False
                self.log.emit(sentence)
                self.state_changed.emit("speaking", sentence)
                self.speaker.speak(sentence)
                full_response += sentence + " "

            self.log.emit(f"  [LLM total: {time.time() - t_llm:.1f}s]")

            # ── Wait for audio, save memory ───────────────────────────────────
            self.speaker.wait_until_done()
            self.memory.add_turn(user_text, full_response.strip())
            self.state_changed.emit("idle", "press enter to speak")
