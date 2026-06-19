"""
LLM module — supports Groq (fast, free) and Ollama (local fallback).
"""

import re
import config

SENTENCE_END = re.compile(r'(?<=[.!?])\s+')


class Brain:
    def __init__(self):
        if config.LLM_PROVIDER == "groq":
            from groq import Groq
            self.client = Groq(api_key=config.GROQ_API_KEY)
            self.model = config.LLM_MODEL
            print(f"Brain using Groq ({self.model}).")
        else:
            from ollama import Client
            self.client = Client(host=config.LLM_BASE_URL)
            self.model = config.LLM_OLLAMA_MODEL
            print(f"Brain using Ollama ({self.model}).")

    def think(self, user_message: str, history: list[dict]) -> str:
        return "".join(self.think_stream(user_message, history))

    def think_stream(self, user_message: str, history: list[dict]):
        messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        if config.LLM_PROVIDER == "groq":
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                temperature=config.LLM_TEMPERATURE,
                max_tokens=config.LLM_MAX_TOKENS,
            )
            buffer = ""
            for chunk in stream:
                token = chunk.choices[0].delta.content or ""
                buffer += token
                parts = SENTENCE_END.split(buffer)
                for sentence in parts[:-1]:
                    sentence = sentence.strip()
                    if sentence:
                        yield sentence
                buffer = parts[-1]
        else:
            stream = self.client.chat(
                model=self.model,
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
                parts = SENTENCE_END.split(buffer)
                for sentence in parts[:-1]:
                    sentence = sentence.strip()
                    if sentence:
                        yield sentence
                buffer = parts[-1]

        if buffer.strip():
            yield buffer.strip()
