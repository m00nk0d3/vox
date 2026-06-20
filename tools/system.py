"""
System tools — OS-level actions VOX can perform.
"""

import subprocess
import webbrowser
import datetime
import pyperclip


def open_app(app_name: str) -> str:
    """Open an application by name."""
    app_map = {
        "spotify":    "spotify",
        "chrome":     "chrome",
        "firefox":    "firefox",
        "vscode":     "code",
        "vs code":    "code",
        "notepad":    "notepad",
        "explorer":   "explorer",
        "calculator": "calc",
        "terminal":   "wt",
        "powershell": "pwsh",
        "discord":    "discord",
        "telegram":   "telegram",
        "whatsapp":   "whatsapp",
        "slack":      "slack",
        "steam":      "steam",
    }
    cmd = app_map.get(app_name.lower(), app_name)
    try:
        subprocess.Popen(cmd, shell=True)
        return f"Opened {app_name}."
    except Exception as e:
        return f"Couldn't open {app_name}: {e}"


def run_shell(command: str) -> str:
    """Run a PowerShell command and return its output."""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True, text=True, timeout=15
        )
        output = result.stdout.strip() or result.stderr.strip()
        return output[:500] if output else "Command ran with no output."
    except subprocess.TimeoutExpired:
        return "Command timed out."
    except Exception as e:
        return f"Shell error: {e}"


def get_datetime() -> str:
    """Return current date and time."""
    now = datetime.datetime.now()
    return now.strftime("It's %A, %B %d %Y, %I:%M %p.")


def search_web(query: str) -> str:
    """Open the browser with a web search."""
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Opened browser searching for: {query}"


def get_clipboard() -> str:
    """Return the current clipboard text."""
    try:
        text = pyperclip.paste()
        return text[:300] if text else "Clipboard is empty."
    except Exception as e:
        return f"Clipboard error: {e}"


def set_clipboard(text: str) -> str:
    """Copy text to clipboard."""
    try:
        pyperclip.copy(text)
        return "Copied to clipboard."
    except Exception as e:
        return f"Clipboard error: {e}"
