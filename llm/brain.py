"""
LLM module — uses Ollama for all inference.
"""

import json
import re

import config

SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


class ToolCall:
    """Returned by think_stream when the LLM wants to call a tool."""

    def __init__(self, name: str, args: dict):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"ToolCall({self.name}, {self.args})"


class Brain:
    def __init__(self):
        from ollama import Client

        self.client = Client(host=config.LLM_BASE_URL)
        print(f"Brain using Ollama ({config.LLM_MODEL}).")

    def think(self, user_message: str, history: list[dict]) -> str:
        return "".join(
            s for s in self.think_stream(user_message, history) if isinstance(s, str)
        )

    def think_stream(
        self, user_message: str, history: list[dict], tool_result: str | None = None
    ):
        """Yield sentences (str) or a single ToolCall if the LLM wants to use a tool.

        If tool_result is provided, appends it as a tool response and streams the final reply.
        """
        messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        from tools.registry import TOOLS_SCHEMA

        # Single call — tool detection + conversation in one shot.
        response = self.client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=messages,
            tools=TOOLS_SCHEMA,
            stream=True,
            options={
                "temperature": config.LLM_TEMPERATURE,
                "num_predict": config.LLM_MAX_TOKENS,
                "num_ctx": config.LLM_NUM_CTX,
                "num_thread": config.LLM_NUM_THREADS,
            },
        )

        for chunk in response:
            msg = chunk.choices[0].message

            if msg.tool_calls:
                for tc in msg.tool_calls:
                    yield ToolCall(
                        name=tc.function.name,
                        args=json.loads(tc.function.arguments),
                    )
                continue

            # No tool call — yield the text content directly
            if msg.content:
                text_tool = self._parse_text_tool_call(msg.content)
                if text_tool:
                    yield text_tool
                    return
                yield from self._split_sentences(msg.content)
        else:
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
                parts = SENTENCE_END.split(buffer)
                for sentence in parts[:-1]:
                    sentence = sentence.strip()
                    if sentence:
                        yield sentence
                buffer = parts[-1]
            if buffer.strip():
                yield buffer.strip()

    def think_with_tool_result(
        self,
        user_message: str,
        history: list[dict],
        tool_name: str,
        tool_call_id: str,
        tool_result: str,
    ):
        """Stream a short spoken confirmation after a tool has been executed.
        Keep it brief and grounded — only say what the tool result confirms."""
        messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        messages.append(
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": tool_call_id,
                        "type": "function",
                        "function": {"name": tool_name, "arguments": "{}"},
                    }
                ],
            }
        )
        messages.append(
            {"role": "tool", "tool_call_id": tool_call_id, "content": tool_result}
        )
        messages.append(
            {
                "role": "system",
                "content": "Give a single short spoken sentence confirming what just happened. "
                "Only say what the tool result actually confirms. Never claim something "
                "worked if the result doesn't say so. No filler, no promises.",
            }
        )

        stream = self.client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=messages,
            stream=True,
            temperature=0.5,
            max_tokens=40,  # short confirmation only
        )
        yield from self._stream_sentences(stream)

    def _parse_text_tool_call(self, text: str) -> "ToolCall | None":
        """Detect when a model outputs a tool call as plain text like run_copilot('task')."""
        import re

        from tools.registry import TOOL_FUNCTIONS

        # Match: tool_name("args") or tool_name({'key': 'value'})
        m = re.match(
            r'^(\w+)\s*\(\s*["\']?(.+?)["\']?\s*\)\s*$', text.strip(), re.DOTALL
        )
        if m:
            name, arg = m.group(1), m.group(2)
            if name in TOOL_FUNCTIONS:
                # Build args dict based on tool — use generic 'task'/'query'/'command' keys
                arg_keys = {
                    "run_copilot": "task",
                    "run_gh": "command",
                    "run_git": "command",
                    "search_web": "query",
                    "open_app": "app_name",
                    "run_shell": "command",
                    "find_project": "name",
                    "spotify_play": "query",
                }
                key = arg_keys.get(name, "task")
                return ToolCall(name=name, args={key: arg})
        return None

    def _split_sentences(self, text: str):
        """Split a complete text string into sentences for TTS."""
        parts = SENTENCE_END.split(text)
        for sentence in parts:
            sentence = sentence.strip()
            if sentence:
                yield sentence

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
