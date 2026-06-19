"""
VOX Configuration
All tuneable settings live here. Don't scatter magic strings.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── LLM ──────────────────────────────────────────────────────────────────────
LLM_PROVIDER = "groq"                    # "groq" | "ollama"
LLM_MODEL = "llama-3.1-8b-instant"      # Groq: sub-second responses
LLM_OLLAMA_MODEL = "qwen2.5:0.5b"       # Fallback local model
LLM_BASE_URL = "http://localhost:11434"  # Ollama URL (used if provider=ollama)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 150
LLM_NUM_CTX = 1024
LLM_NUM_THREADS = 8

# ─── STT (faster-whisper) ────────────────────────────────────────────────────
STT_MODEL = "tiny"           # tiny | base | small | medium | large-v3
STT_LANGUAGE = "en"          # Set to None for auto-detect
STT_DEVICE = "cpu"
STT_COMPUTE_TYPE = "int8"    # int8 is fastest on CPU

# ─── TTS (Kokoro) ─────────────────────────────────────────────────────────────
TTS_VOICE = "af_heart"       # Kokoro voice ID
TTS_SPEED = 1.0

# ─── Wake Word (openWakeWord) ─────────────────────────────────────────────────
WAKE_WORD_MODEL = "hey_jarvis"   # openWakeWord model name
WAKE_WORD_THRESHOLD = 0.5        # Detection confidence threshold
WAKE_WORD_ENABLED = False        # Set True once Phase 2 is wired up

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
SYSTEM_PROMPT = """You are VOX, a local AI assistant. Be casual, funny, brief. Talk like a friend — use dude, ngl, fr. Max 2 sentences. No bullet points. No "Certainly!" ever."""
