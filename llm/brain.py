"""
LLM module — Ollama client with conversation history.
"""

from ollama import Client
import config


class Brain:
    def __init__(self):
        self.client = Client(host=config.LLM_BASE_URL)
        print(f"Brain connected to Ollama ({config.LLM_MODEL}).")

    def think(self, user_message: str, history: list[dict]) -> str:
        """
        Send user message + conversation history to the LLM.
        Returns the assistant's response as plain text.
        """
        messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        response = self.client.chat(
            model=config.LLM_MODEL,
            messages=messages,
            options={
                "temperature": config.LLM_TEMPERATURE,
                "num_predict": config.LLM_MAX_TOKENS,
            },
        )

        return response["message"]["content"].strip()
