"""
STT module — records via VAD, transcribes via Groq Whisper API or local faster-whisper.
"""

import io
import wave
import tempfile
import sounddevice as sd
import numpy as np
import config

CHUNK_SECONDS = 0.1


class Transcriber:
    def __init__(self):
        if config.STT_PROVIDER == "groq":
            from groq import Groq
            self.client = Groq(api_key=config.GROQ_API_KEY)
            print(f"STT using Groq Whisper ({config.STT_GROQ_MODEL}).")
        else:
            from faster_whisper import WhisperModel
            self.model = WhisperModel(
                config.STT_MODEL,
                device=config.STT_DEVICE,
                compute_type=config.STT_COMPUTE_TYPE,
            )
            print(f"STT using local Whisper ({config.STT_MODEL}).")

    def listen(self) -> str:
        audio = self._record_until_silence()
        if len(audio) == 0:
            return ""
        if config.STT_PROVIDER == "groq":
            return self._transcribe_groq(audio)
        return self._transcribe_local(audio)

    def _record_until_silence(self) -> np.ndarray:
        sample_rate = config.AUDIO_SAMPLE_RATE
        chunk_size  = int(sample_rate * CHUNK_SECONDS)
        silence_chunks_needed = int(config.VAD_SILENCE_DURATION / CHUNK_SECONDS)
        max_speech_chunks     = int(config.VAD_MAX_DURATION / CHUNK_SECONDS)

        frames         = []
        silence_chunks = 0
        speech_started = False

        print("Waiting for speech...")

        with sd.InputStream(samplerate=sample_rate, channels=1, dtype="float32") as stream:
            while True:
                chunk, _   = stream.read(chunk_size)
                chunk_flat = chunk.flatten()
                rms        = float(np.sqrt(np.mean(chunk_flat ** 2)))

                if rms > config.VAD_SILENCE_THRESHOLD:
                    if not speech_started:
                        print("Listening...")
                        speech_started = True
                    silence_chunks = 0
                    frames.append(chunk_flat)

                    # Cap recording at max duration
                    if len(frames) >= max_speech_chunks:
                        break

                elif speech_started:
                    frames.append(chunk_flat)
                    silence_chunks += 1
                    if silence_chunks >= silence_chunks_needed:
                        break
                # else: no speech yet — wait forever (sleep command controls idle)

        if not frames:
            return np.array([], dtype=np.float32)
        return np.concatenate(frames)

    def _transcribe_groq(self, audio: np.ndarray) -> str:
        """Send audio to Groq Whisper API."""
        pcm = (audio * 32767).astype(np.int16)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(config.AUDIO_SAMPLE_RATE)
            wf.writeframes(pcm.tobytes())
        buf.seek(0)

        result = self.client.audio.transcriptions.create(
            file=("audio.wav", buf, "audio/wav"),
            model=config.STT_GROQ_MODEL,
            language=config.STT_LANGUAGE,
        )
        return result.text.strip()

    def _transcribe_local(self, audio: np.ndarray) -> str:
        """Run local faster-whisper inference."""
        segments, _ = self.model.transcribe(
            audio,
            language=config.STT_LANGUAGE,
            beam_size=1,
        )
        return " ".join(seg.text.strip() for seg in segments).strip()
