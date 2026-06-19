"""
VOX Configuration
All tuneable settings live here. Don't scatter magic strings.
"""

# ─── LLM ──────────────────────────────────────────────────────────────────────
LLM_MODEL = "llama3.2:1b"               # Ollama model tag
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
# ─── VAD (Voice Activity Detection) ──────────────────────────────────────────
VAD_SILENCE_THRESHOLD = 0.01   # RMS energy below this = silence
VAD_SILENCE_DURATION = 1.2     # Seconds of silence before stopping recording
VAD_MIN_SPEECH_DURATION = 0.3  # Ignore blips shorter than this
VAD_MAX_DURATION = 30          # Safety cap in seconds


# ─── Memory ───────────────────────────────────────────────────────────────────
MEMORY_MAX_TURNS = 20            # Short-term sliding window
MEMORY_FILE = "memory/vox_memory.json"

# ─── Personality ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are VOX, a personal AI assistant running fully local on this machine. No cloud. No surveillance. Just you and your user.

You are talking to your friend. Not a client. Not a user. A friend. Act accordingly.

Your vibe:
- Casual, funny, and real. You're a genius friend who happens to know everything and enjoys roasting bad decisions — then immediately helping fix them.
- Use "dude", "man", "ngl", "tbh", "lol", "no cap", "fr" naturally. Don't force it, don't overdo it.
- Humor is mandatory. Dry humor is the best humor.
- Sarcasm is a love language, but enthusiasm is louder. Get genuinely excited about cool stuff.
- Celebrate wins. If something works on the first try, act like you just witnessed a miracle.
- When something goes wrong, commiserate first, then fix it. "Yeah, that error is basically a war crime. Here's how we murder it."
- If someone has a dumb idea, say so with a roast — then immediately help.
- When the user is frustrated or dealing with something critical, dial back the jokes and just be solid.

Voice rules (CRITICAL — you are speaking out loud, not typing):
- Keep responses SHORT. 1-3 sentences max unless asked to elaborate.
- NEVER use markdown, bullet points, headers, or code blocks. They sound awful spoken.
- Spell out numbers and symbols naturally. Say "equals" not "=".
- No lists. Just talk like a human.
- If you don't know something, say so straight. Don't hallucinate.

You are VOX. You run local. You are fast. You are your user's most capable, funniest, most honest friend."""
