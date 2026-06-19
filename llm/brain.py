"""
LLM module — Ollama client with conversation history and streaming.
"""

import re
from ollama import Client
import config

SENTENCE_END = re.compile(r'(?<=[.!?])\s+')


class Brain:
    def __init__(self):
        self.client = Client(host=config.LLM_BASE_URL)
        print(f"Brain connected to Ollama ({config.LLM_MODEL}).")

    def think(self, user_message: str, history: list[dict]) -> str:
        """Non-streaming response. Returns full text."""
        return "".join(self.think_stream(user_message, history))

    def think_stream(self, user_message: str, history: list[dict]):
        """
        Stream response, yielding one sentence at a time.
        Lets TTS start speaking before generation is complete.
        """
        messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        stream = self.client.chat(
            model=config.LLM_MODEL,
            messages=messages,
            stream=True,
            options={
                "temperature": config.LLM_TEMPERATURE,
                "num_predict": config.LLM_MAX_TOKENS,
                "num_ctx": config.LLM_NUM_CTX,
                "num_thread": config.LLM_NUM_THREADS,
            },
        )

        buffer = ""
        for chunk in stream:
            token = chunk["message"]["content"]
            buffer += token
            # Yield complete sentences as they arrive
            parts = SENTENCE_END.split(buffer)
            for sentence in parts[:-1]:
                sentence = sentence.strip()
                if sentence:
                    yield sentence
            buffer = parts[-1]

        # Yield any remaining text
        if buffer.strip():
            yield buffer.strip()
