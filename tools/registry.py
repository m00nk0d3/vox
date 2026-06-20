"""
Tool registry — maps tool names to functions and their Groq JSON schemas.
"""

from tools.system import open_app, run_shell, get_datetime, search_web, get_clipboard, set_clipboard
from tools.copilot import run_copilot

# ── Executor ──────────────────────────────────────────────────────────────────

TOOL_FUNCTIONS = {
    "open_app":     lambda args: open_app(args["app_name"]),
    "run_shell":    lambda args: run_shell(args["command"]),
    "get_datetime": lambda args: get_datetime(),
    "search_web":   lambda args: search_web(args["query"]),
    "get_clipboard":lambda args: get_clipboard(),
    "set_clipboard":lambda args: set_clipboard(args["text"]),
    "run_copilot":  lambda args: run_copilot(args["task"]),
}


def execute_tool(name: str, args: dict) -> str:
    fn = TOOL_FUNCTIONS.get(name)
    if not fn:
        return f"Unknown tool: {name}"
    try:
        return fn(args)
    except Exception as e:
        return f"Tool {name} failed: {e}"


# ── Groq tool schemas ─────────────────────────────────────────────────────────

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "open_app",
            "description": "Open an application on the user's Windows computer. Use for requests like 'open Spotify', 'launch Chrome', 'start VSCode'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Name of the application to open (e.g. 'spotify', 'chrome', 'vscode')"}
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "Run a PowerShell command on the user's computer and return the output. Use for system tasks, file operations, or anything requiring a shell.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The PowerShell command to execute"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_datetime",
            "description": "Get the current date and time.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Open the user's browser and search Google for a query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_clipboard",
            "description": "Read the current text content of the user's clipboard.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_clipboard",
            "description": "Copy text to the user's clipboard.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text to copy to clipboard"}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_copilot",
            "description": "Delegate a software development task to GitHub Copilot CLI. Use when the user asks to write code, create files, fix bugs, run git commands, or anything dev-related.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "The development task description to pass to Copilot"}
                },
                "required": ["task"]
            }
        }
    },
]
