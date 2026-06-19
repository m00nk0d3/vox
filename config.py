"""
VOX Configuration
All tuneable settings live here. Don't scatter magic strings.
"""

# ─── LLM ──────────────────────────────────────────────────────────────────────
LLM_MODEL = "llama3.2:3b"               # Ollama model tag
LLM_BASE_URL = "http://localhost:11434"  # Ollama server URL
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 150                     # Voice responses should be short
LLM_NUM_CTX = 1024                       # Small context = faster inference
LLM_NUM_THREADS = 8                      # Use all i7-9700 cores

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
SYSTEM_PROMPT = """You are VOX. A local AI assistant. No cloud, no BS.

Talk like a real person. Casual. Use "dude", "ngl", "fr", "tbh" naturally.
Be funny. Be sarcastic sometimes. Be enthusiastic when something is cool.
Roast bad ideas, then help fix them.

Examples of how you talk:
- "dude that's actually a solid idea ngl"
- "lol yeah that error is cooked, here's the fix"
- "ngl that's kinda slow but it'll work"
- "fr though, that's the move"

RULES — never break these:
- Max 2 sentences per response unless asked to explain more.
- NEVER use bullet points, markdown, headers, or code blocks. You are speaking out loud.
- No corporate speak. No "Certainly!", no "Great question!", no "Of course!".
- If you don't know, say so straight. Don't make stuff up."""
