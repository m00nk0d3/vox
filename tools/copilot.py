"""
Copilot CLI tool — VOX can delegate dev tasks to GitHub Copilot CLI.
"""

import subprocess


def run_copilot(task: str) -> str:
    """Pass a development task to GitHub Copilot CLI and return the output."""
    try:
        result = subprocess.run(
            ["gh", "copilot", "-p", task],
            capture_output=True, text=True, timeout=60,
        )
        output = (result.stdout or result.stderr or "").strip()
        return output[:800] if output else "Copilot had no output."
    except subprocess.TimeoutExpired:
        return "Copilot timed out."
    except FileNotFoundError:
        return "gh CLI not found. Make sure it's installed."
    except Exception as e:
        return f"Copilot error: {e}"
