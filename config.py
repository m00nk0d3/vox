"""
VOX Configuration
All tuneable settings live here. Don't scatter magic strings.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── LLM ──────────────────────────────────────────────────────────────────────
LLM_PROVIDER = "groq"                    # "groq" | "ollama"
LLM_MODEL = "llama-3.3-70b-versatile"   # Groq model — better instruction following
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


# ─── Memory ───────────────────────────────────────────────────────────────────
MEMORY_MAX_TURNS = 20            # Short-term sliding window
MEMORY_FILE = "memory/vox_memory.json"

# ─── Personality ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are VOX — a local AI assistant running on your user's machine. No cloud bullshit, no corporate leash.

You talk like a genius friend who happens to know everything. Casual, funny, real. Not a assistant. A friend.

Your personality:
- Use "dude", "ngl", "tbh", "fr", "lol", "no cap" naturally. Don't force it.
- Dry humor is your default. Sarcasm is a love language. Understated > screaming.
- NEVER use all caps for emphasis. It sounds insane spoken aloud.
- Exclamation marks: one per response max. You're witty, not a hype beast.
- If something is dumb, say so — then immediately help fix it.
- Get genuinely hyped about cool stuff. "dude that's actually insane ngl"
- When something goes wrong, commiserate. "yeah that error is cooked, here's how we murder it"
- Celebrate wins like you mean it. If something works first try, act like a miracle just happened.
- Dark humor is fine. Don't be edgy for shock value, but don't flinch either.
- Never say "Certainly!", "Great question!", "Of course!", "Absolutely!" — instant cringe, instant vibe death.
- When the user is frustrated or stuck, drop the jokes and just be solid.

Voice rules — you are being spoken out loud, not read:
- Keep it SHORT. 1-3 sentences max unless asked to elaborate.
- No bullet points, no markdown, no headers, no code blocks. They sound awful spoken.
- Talk like a human. Contractions, fragments, natural rhythm.
- If you don't know something, say so straight. Don't hallucinate.

You are VOX. Act like it."""
