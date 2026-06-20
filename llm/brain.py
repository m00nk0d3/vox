"""
LLM module — supports Groq (fast, free) and Ollama (local fallback).
Groq path supports function/tool calling.
"""

import re
import json
import config

SENTENCE_END = re.compile(r'(?<=[.!?])\s+')


class ToolCall:
    """Returned by think_stream when the LLM wants to call a tool."""
    def __init__(self, name: str, args: dict):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"ToolCall({self.name}, {self.args})"


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
        return "".join(
            s for s in self.think_stream(user_message, history)
            if isinstance(s, str)
        )

    def think_stream(self, user_message: str, history: list[dict], tool_result: str | None = None):
        """Yield sentences (str) or a single ToolCall if the LLM wants to use a tool.
        
        If tool_result is provided, appends it as a tool response and streams the final reply.
        """
        messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        if config.LLM_PROVIDER == "groq":
            from tools.registry import TOOLS_SCHEMA

            # ── First pass: detect tool calls (non-streaming) ────────────────
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
                temperature=config.LLM_TEMPERATURE,
                max_tokens=config.LLM_MAX_TOKENS,
            )
            msg = response.choices[0].message

            if msg.tool_calls:
                # Yield tool calls — worker will execute and call back
                for tc in msg.tool_calls:
                    yield ToolCall(
                        name=tc.function.name,
                        args=json.loads(tc.function.arguments),
                    )
                return

            # ── No tool call — stream the text response ───────────────────
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                temperature=config.LLM_TEMPERATURE,
                max_tokens=config.LLM_MAX_TOKENS,
            )
            yield from self._stream_sentences(stream)

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

    def think_with_tool_result(self, user_message: str, history: list[dict],
                                tool_name: str, tool_call_id: str, tool_result: str):
        """Stream a final response after a tool has been executed."""
        messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        messages.append({"role": "assistant", "content": None, "tool_calls": [{
            "id": tool_call_id,
            "type": "function",
            "function": {"name": tool_name, "arguments": "{}"}
        }]})
        messages.append({"role": "tool", "tool_call_id": tool_call_id, "content": tool_result})

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
            temperature=config.LLM_TEMPERATURE,
            max_tokens=config.LLM_MAX_TOKENS,
        )
        yield from self._stream_sentences(stream)

    def _stream_sentences(self, stream):
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
        if buffer.strip():
            yield buffer.strip()
