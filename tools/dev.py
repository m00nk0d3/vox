"""
Dev tools — VOX can find projects, read code, run git/gh commands, and
delegate tasks to GitHub Copilot CLI. All commands run in the active project context.
"""

import os
import subprocess
import json
from pathlib import Path

# ── Project context ───────────────────────────────────────────────────────────
_STATE_FILE = Path(__file__).parent.parent / "memory" / "dev_state.json"

def _load_state() -> dict:
    if _STATE_FILE.exists():
        try:
            return json.loads(_STATE_FILE.read_text())
        except Exception:
            pass
    return {}

def _save_state(state: dict):
    _STATE_FILE.parent.mkdir(exist_ok=True)
    _STATE_FILE.write_text(json.dumps(state, indent=2))

def get_project() -> str | None:
    return _load_state().get("project_path")

def set_project(path: str) -> str:
    state = _load_state()
    state["project_path"] = path
    _save_state(state)
    return f"Active project set to: {path}"


# ── Search ────────────────────────────────────────────────────────────────────

def _get_search_roots() -> list[str]:
    """Dynamically get all available drives + common project locations."""
    roots = []
    # All Windows drives
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            roots.append(drive)
    return roots


def find_project(name: str) -> str:
    """Search all drives for a project folder by name."""
    name_lower = name.lower()
    matches = []
    skip_dirs = {'.git', 'node_modules', '__pycache__', 'venv', '.venv',
                 'Windows', 'Program Files', 'Program Files (x86)', '$Recycle.Bin',
                 'System Volume Information', 'ProgramData'}

    for root in _get_search_roots():
        try:
            for dirpath, dirnames, _ in os.walk(root):
                # Prune noise dirs to keep search fast
                dirnames[:] = [d for d in dirnames
                                if d not in skip_dirs and not d.startswith('$')]
                for d in dirnames:
                    if name_lower in d.lower():
                        matches.append(os.path.join(dirpath, d))
                        if len(matches) >= 8:
                            break
                if len(matches) >= 8:
                    break
        except (PermissionError, OSError):
            continue

    if not matches:
        return f"No project matching '{name}' found on any drive."

    # Prefer matches that contain a .git folder (actual repos)
    git_repos = [m for m in matches if os.path.exists(os.path.join(m, ".git"))]
    best = git_repos[0] if git_repos else matches[0]

    set_project(best)
    if len(matches) == 1:
        return f"Found and set active project: {best}"

    result = f"Found {len(matches)} matches for '{name}':\n"
    result += "\n".join(f"  {i+1}. {p}" for i, p in enumerate(matches))
    result += f"\nActive project set to: {best}"
    return result


# ── File operations ───────────────────────────────────────────────────────────

def list_files(subpath: str = "") -> str:
    """List files in the active project (or a subdirectory)."""
    base = get_project()
    if not base:
        return "No active project. Say 'find project X' first."

    target = Path(base) / subpath if subpath else Path(base)
    if not target.exists():
        return f"Path not found: {target}"

    lines = []
    try:
        for root, dirs, files in os.walk(target):
            # Skip hidden and common noise dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in
                       {'node_modules', '__pycache__', '.git', 'venv', '.venv', 'dist', 'build'}]
            level = len(Path(root).relative_to(target).parts)
            if level > 2:
                continue
            indent = "  " * level
            lines.append(f"{indent}{Path(root).name}/")
            for f in files[:20]:  # cap files per dir
                lines.append(f"{indent}  {f}")
    except PermissionError:
        pass

    return "\n".join(lines[:60]) if lines else "Empty directory."


def read_file(file_path: str) -> str:
    """Read a file from the active project."""
    base = get_project()
    if not base:
        return "No active project. Say 'find project X' first."

    # Support both absolute and relative paths
    path = Path(file_path) if Path(file_path).is_absolute() else Path(base) / file_path
    if not path.exists():
        return f"File not found: {path}"

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        if len(content) > 2000:
            content = content[:2000] + "\n... (truncated)"
        return content
    except Exception as e:
        return f"Could not read file: {e}"


# ── Git & GitHub ──────────────────────────────────────────────────────────────

def _run(cmd: list[str], cwd: str | None = None) -> str:
    cwd = cwd or get_project()
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30, cwd=cwd,
            encoding="utf-8", errors="replace"
        )
        output = (result.stdout or result.stderr or "").strip()
        return output[:800] if output else "(no output)"
    except subprocess.TimeoutExpired:
        return "Command timed out."
    except Exception as e:
        return f"Error: {e}"


def _get_repo() -> str | None:
    """Auto-detect GitHub repo from active project's git remote."""
    cwd = get_project()
    if not cwd:
        return None
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True, text=True, cwd=cwd
        )
        url = result.stdout.strip()
        # Parse github.com/owner/repo from https or ssh URL
        import re
        m = re.search(r"github\.com[:/](.+?/[^/]+?)(?:\.git)?$", url)
        return m.group(1) if m else None
    except Exception:
        return None


def run_git(command: str) -> str:
    """Run a git command in the active project."""
    if not get_project():
        return "No active project. Say 'find project X' first."
    args = command.split()
    return _run(["git"] + args)


def run_gh(command: str) -> str:
    """Run a GitHub CLI command in the active project, auto-detecting the repo."""
    if not get_project():
        return "No active project. Say 'find project X' first."
    
    # Auto-inject --repo if not already specified
    repo = _get_repo()
    args = command.split()
    if repo and "--repo" not in command and "-R" not in command:
        # Insert --repo after the subcommand (e.g. 'issue list' -> 'issue list --repo owner/repo')
        args = args + ["--repo", repo]
    
    return _run(["gh"] + args)


def run_copilot(task: str) -> str:
    """Delegate a dev task to GitHub Copilot CLI in the active project.
    Streams output and returns a summary of what was done."""
    cwd = get_project()
    if not cwd:
        return "No active project. Say 'find project X' first."
    try:
        process = subprocess.Popen(
            ["gh", "copilot", "-p", task],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=cwd,
        )
        lines = []
        for line in process.stdout:
            line = line.rstrip()
            if line:
                print(f"[Copilot] {line}")  # Show in VOX terminal
                lines.append(line)

        process.wait(timeout=180)
        output = "\n".join(lines)

        if not output.strip():
            return "Copilot ran but produced no output."

        # Return last 800 chars — most relevant part is at the end
        summary = output[-800:] if len(output) > 800 else output
        return summary

    except subprocess.TimeoutExpired:
        process.kill()
        return "Copilot timed out after 3 minutes."
    except Exception as e:
        return f"Copilot error: {e}"
