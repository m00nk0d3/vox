"""
VOX Configuration
All tuneable settings live here. Don't scatter magic strings.
"""

# ─── LLM ──────────────────────────────────────────────────────────────────────
LLM_MODEL = "qwen2.5:7b"                # Ollama model tag
LLM_BASE_URL = "http://localhost:11434"  # Ollama server URL
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 512                     # Keep responses concise for voice

# ─── STT (faster-whisper) ────────────────────────────────────────────────────
STT_MODEL = "small"          # tiny | base | small | medium | large-v3
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
AUDIO_CHUNK_SECONDS = 5          # How many seconds to record per turn

# ─── Memory ───────────────────────────────────────────────────────────────────
MEMORY_MAX_TURNS = 20            # Short-term sliding window
MEMORY_FILE = "memory/vox_memory.json"

# ─── Personality ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are VOX, a sharp and capable personal AI assistant.
You are helpful, concise, and occasionally witty.
You are running fully locally — no cloud, no surveillance.
Keep your responses brief and optimized for speech. Avoid markdown, bullet points,
or anything that sounds weird when read aloud. Speak naturally."""
