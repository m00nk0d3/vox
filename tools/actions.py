"""
Tools module — VOX actions (Phase 4).
PC control, web search, app launching, etc.
Stub for now — will be wired into Brain via function calling.
"""


def open_application(app_name: str) -> str:
    """Launch an application by name. (stub)"""
    raise NotImplementedError("Tool: open_application not yet implemented.")


def web_search(query: str) -> str:
    """Run a web search and return a summary. (stub)"""
    raise NotImplementedError("Tool: web_search not yet implemented.")


def run_script(script_path: str) -> str:
    """Execute a local Python script and return output. (stub)"""
    raise NotImplementedError("Tool: run_script not yet implemented.")


def set_timer(seconds: int, label: str = "") -> str:
    """Set a countdown timer. (stub)"""
    raise NotImplementedError("Tool: set_timer not yet implemented.")
