"""
Tool registry — maps tool names to functions and their Groq JSON schemas.
"""

from tools.system import open_app, run_shell, get_datetime, search_web, get_clipboard, set_clipboard
from tools.copilot import run_copilot as _run_copilot_legacy
from tools.spotify import spotify_play, spotify_pause, spotify_resume, spotify_next, spotify_previous, spotify_volume, spotify_now_playing
from tools.dev import find_project, set_project, list_files, read_file, run_git, run_gh, run_copilot, get_project

# ── Executor ──────────────────────────────────────────────────────────────────

TOOL_FUNCTIONS = {
    "open_app":          lambda args: open_app(args["app_name"]),
    "run_shell":         lambda args: run_shell(args["command"]),
    "get_datetime":      lambda args: get_datetime(),
    "search_web":        lambda args: search_web(args["query"]),
    "get_clipboard":     lambda args: get_clipboard(),
    "set_clipboard":     lambda args: set_clipboard(args["text"]),
    "spotify_play":      lambda args: spotify_play(args["query"]),
    "spotify_pause":     lambda args: spotify_pause(),
    "spotify_resume":    lambda args: spotify_resume(),
    "spotify_next":      lambda args: spotify_next(),
    "spotify_previous":  lambda args: spotify_previous(),
    "spotify_volume":    lambda args: spotify_volume(int(args["level"])),
    "spotify_now_playing": lambda args: spotify_now_playing(),
    "find_project":      lambda args: find_project(args["name"]),
    "set_project":       lambda args: set_project(args["path"]),
    "list_files":        lambda args: list_files(args.get("subpath", "")),
    "read_file":         lambda args: read_file(args["file_path"]),
    "run_git":           lambda args: run_git(args["command"]),
    "run_gh":            lambda args: run_gh(args["command"]),
    "run_copilot":       lambda args: run_copilot(args["task"]),
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
    {
        "type": "function",
        "function": {
            "name": "spotify_play",
            "description": "Search Spotify and play a track, artist, or playlist by name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Track name, artist, or playlist to search and play"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "spotify_pause",
            "description": "Pause Spotify playback.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "spotify_resume",
            "description": "Resume Spotify playback.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "spotify_next",
            "description": "Skip to the next track on Spotify.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "spotify_previous",
            "description": "Go back to the previous track on Spotify.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "spotify_volume",
            "description": "Set Spotify volume level.",
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {"type": "integer", "description": "Volume level from 0 to 100"}
                },
                "required": ["level"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "spotify_now_playing",
            "description": "Get what's currently playing on Spotify.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_project",
            "description": "Search the user's disks for a project folder by name and set it as the active project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Project name or partial name to search for"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_project",
            "description": "Set the active project to a specific path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Full path to the project directory"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and folders in the active project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subpath": {"type": "string", "description": "Optional subdirectory to list (relative to project root)"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file in the active project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "File path (relative to project root or absolute)"}
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_git",
            "description": "Run a git command in the active project (e.g. 'status', 'log --oneline -10', 'diff').",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Git subcommand and args (without the 'git' prefix)"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_gh",
            "description": "Run a GitHub CLI command in the active project (e.g. 'issue list', 'pr list', 'repo view').",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "gh subcommand and args (without the 'gh' prefix)"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_copilot",
            "description": "Delegate a software development task to GitHub Copilot CLI in the active project. Use for writing code, fixing bugs, creating files, git operations, or any dev task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "Natural language description of the dev task"}
                },
                "required": ["task"]
            }
        }
    },
]
