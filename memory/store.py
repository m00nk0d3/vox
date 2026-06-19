"""
Memory module — Stores conversation history (short-term + long-term).
"""

import json
import os
import config


class MemoryStore:
    def __init__(self):
        self.history: list[dict] = []
        self._load_long_term()

    def add_turn(self, user_message: str, assistant_response: str):
        """Append a user/assistant turn and persist it."""
        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": assistant_response})

        # Trim to sliding window
        max_messages = config.MEMORY_MAX_TURNS * 2
        if len(self.history) > max_messages:
            self.history = self.history[-max_messages:]

        self._save_long_term()

    def get_history(self) -> list[dict]:
        """Return the current conversation history."""
        return list(self.history)

    def clear(self):
        """Wipe memory (useful for starting fresh sessions)."""
        self.history = []
        if os.path.exists(config.MEMORY_FILE):
            os.remove(config.MEMORY_FILE)

    def _save_long_term(self):
        os.makedirs(os.path.dirname(config.MEMORY_FILE), exist_ok=True)
        with open(config.MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2)

    def _load_long_term(self):
        if os.path.exists(config.MEMORY_FILE):
            with open(config.MEMORY_FILE, "r", encoding="utf-8") as f:
                self.history = json.load(f)
