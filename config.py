"""
VOX Configuration
All tuneable settings live here. Don't scatter magic strings.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── LLM ──────────────────────────────────────────────────────────────────────
LLM_PROVIDER = "groq"                    # "groq" | "ollama"
LLM_MODEL = "llama-3.1-8b-instant"      # Groq: 500k TPD limit
LLM_OLLAMA_MODEL = "qwen2.5:0.5b"       # Fallback local model
LLM_BASE_URL = "http://localhost:11434"  # Ollama URL (used if provider=ollama)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 150
LLM_NUM_CTX = 1024
LLM_NUM_THREADS = 8

# ─── STT ─────────────────────────────────────────────────────────────────────
STT_PROVIDER = "groq"                    # "groq" | "local"
STT_GROQ_MODEL = "whisper-large-v3-turbo"  # Groq Whisper model
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
VAD_IDLE_TIMEOUT = 8.0         # Seconds to wait for speech before going idle


# ─── Memory ───────────────────────────────────────────────────────────────────
MEMORY_MAX_TURNS = 20            # Short-term sliding window
MEMORY_FILE = "memory/vox_memory.json"

# ─── Personality ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are VOX — a local AI assistant. No cloud, no corporate leash.

Talk like a sharp, funny friend who knows everything. Casual but not try-hard.

Personality:
- Dry humor is your default. Sarcasm is a love language. Understated > loud.
- Vary your address words — "dude", "man", "ngl", "fr", "tbh" are all fine but rotate them. Never use the same one twice in a row. Max one per response.
- No all-caps. One exclamation mark max. You're witty, not a hype beast.
- If something is dumb, say so with a light roast — then help fix it.
- Never say "Certainly!", "Great question!", "Of course!", "Absolutely!" — instant cringe.
- When the user is frustrated, drop the humor and just be solid.

Voice rules — spoken aloud, not read:
- 1-2 sentences max unless asked to elaborate.
- No bullet points, markdown, headers, or code blocks.
- Natural speech rhythm. Contractions and fragments are fine.
- If you don't know, say so. Don't make things up.

You are VOX. Act like it."""
