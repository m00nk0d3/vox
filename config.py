"""
VOX Configuration
All tuneable settings live here. Don't scatter magic strings.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── LLM ──────────────────────────────────────────────────────────────────────
LLM_PROVIDER = "groq"                    # "groq" | "ollama"
LLM_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"  # Conversation — independent of 70b quota
LLM_TOOL_MODEL = "openai/gpt-oss-20b"   # Tool detection pass (reliable function calling)
LLM_OLLAMA_MODEL = "qwen2.5:0.5b"       # Fallback local model
LLM_BASE_URL = "http://localhost:11434"  # Ollama URL (used if provider=ollama)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 200
LLM_NUM_CTX = 1024
LLM_NUM_THREADS = 8

# ─── STT ─────────────────────────────────────────────────────────────────────
STT_PROVIDER = "groq"                    # "groq" | "local"
STT_GROQ_MODEL = "whisper-large-v3"         # Full model — better accuracy
STT_MODEL = "tiny"           # Local fallback: tiny | base | small | medium
STT_LANGUAGE = "en"
STT_DEVICE = "cpu"
STT_COMPUTE_TYPE = "int8"

# ─── TTS (Kokoro) ─────────────────────────────────────────────────────────────
TTS_VOICE = "af_heart"       # Kokoro voice ID
TTS_SPEED = 1.0

# ─── Wake Word (openWakeWord) ─────────────────────────────────────────────────
WAKE_WORD_MODEL = "hey_jarvis"       # openWakeWord model name
WAKE_WORD_THRESHOLD = 0.5            # Detection confidence threshold
WAKE_WORD_ENABLED = True             # Always-on wake word

# ─── Audio ────────────────────────────────────────────────────────────────────
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1

# ─── VAD (Voice Activity Detection) ──────────────────────────────────────────
VAD_SILENCE_THRESHOLD = 0.01   # RMS energy below this = silence
VAD_SILENCE_DURATION = 0.8     # Seconds of silence before stopping recording
VAD_MIN_SPEECH_DURATION = 0.3  # Ignore blips shorter than this
VAD_MAX_DURATION = 30          # Safety cap in seconds
VAD_IDLE_TIMEOUT = 3600.0      # Effectively infinite — sleep only on command


# ─── Memory ───────────────────────────────────────────────────────────────────
SLEEP_COMMANDS = [
    r"\bgo to sleep\b",
    r"\bgoodnight\b",
    r"\bgood night\b",
    r"\bvox sleep\b",
    r"\bstop listening\b",
    r"\bbye\b",
    r"\bbyebye\b",
    r"\bgoodbye\b",
    r"\bsee you later\b",
    r"\bsee ya\b",
    r"\bthat'?s all\b",
    r"\bwe'?re done\b",
    r"\bi'?m done\b",
    r"\bdismissed?\b",
]

# ─── Memory ───────────────────────────────────────────────────────────────────
MEMORY_MAX_TURNS = 10            # Short-term sliding window (keep it lean)
MEMORY_FILE = "memory/vox_memory.json"

# ─── Personality ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are VOX — a local AI voice assistant. You speak out loud — your responses are converted to speech and played through speakers. Act accordingly.

Talk like a sharp, funny friend who knows everything. Casual but not try-hard.

Personality:
- Dry humor is your default. Sarcasm is a love language. Understated > loud.
- Vary your address words — "dude", "man", "ngl", "fr", "tbh" are all fine but rotate them. Never use the same one twice in a row. Max one per response.
- No all-caps. One exclamation mark max. You're witty, not a hype beast.
- If something is dumb, say so with a light roast — then help fix it.
- Never say "Certainly!", "Great question!", "Of course!", "Absolutely!" — instant cringe.
- When the user is frustrated, drop the humor and just be solid.

Voice rules — spoken aloud, not read:
- Match response length to the question. Simple question = 1-2 sentences. Complex topic = up to 4. Never pad, never cut off.
- No bullet points, markdown, headers, or code blocks.
- Natural speech rhythm. Contractions and fragments are fine.
- If you don't know, say so. Don't make things up.

You are VOX. Act like it.

You have tools — USE THEM without asking permission:
- spotify_play / spotify_pause / spotify_resume / spotify_next / spotify_previous / spotify_volume / spotify_now_playing — full Spotify control
- open_app — open any app on the user's computer
- search_web — open browser with a search
- run_shell — run PowerShell commands FOR SYSTEM TASKS ONLY (files, processes, system info). NEVER use run_shell to answer conversational questions.
- get_datetime — current time and date
- get_clipboard / set_clipboard — clipboard access
- find_project / set_project — find a project on disk and set it as active context
- list_files / read_file — browse and read code in the active project
- run_git — run git commands in the active project
- run_gh — GitHub CLI: list issues, PRs, repo info, etc.
- run_copilot — delegate any dev task to GitHub Copilot CLI in the active project

When the user asks you to do something you have a tool for, CALL THE TOOL. Never say "I can't" when you have the tool to do it.
If a tool returns an error, report it honestly — don't claim it worked."""
