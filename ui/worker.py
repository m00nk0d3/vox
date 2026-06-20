"""
Voice worker — runs STT -> LLM -> TTS in a background thread.
After wake word, stays active for ACTIVE_TIMEOUT seconds of silence.
"""

import time
import re
import threading


def voice_loop(transcriber, brain, speaker, memory, state_ref: dict):
    import config

    if config.WAKE_WORD_ENABLED:
        from wake.detector import WakeWordDetector
        detector = WakeWordDetector()

    # Spotify handle for pause/resume around listening
    try:
        from tools.spotify import _client as spotify_client, _active_device_id
        _spotify_available = True
    except Exception:
        _spotify_available = False

    def spotify_pause_if_playing():
        if not _spotify_available:
            return False
        try:
            sp = spotify_client()
            pb = sp.current_playback()
            if pb and pb.get("is_playing"):
                device_id = _active_device_id()
                sp.pause_playback(device_id=device_id)
                return True
        except Exception:
            pass
        return False

    def spotify_resume_if_was_playing(was_playing: bool):
        if not _spotify_available or not was_playing:
            return
        try:
            device_id = _active_device_id()
            spotify_client().start_playback(device_id=device_id)
        except Exception:
            pass

    idle_text = "say hey jarvis" if config.WAKE_WORD_ENABLED else "press enter"

    def go_idle():
        state_ref.update({"state": "idle", "text": idle_text})

    go_idle()

    while True:
        # ── Wait for activation ───────────────────────────────────────────────
        if config.WAKE_WORD_ENABLED:
            detector.wait_for_wake_word()
        else:
            input("\n[Press Enter to speak] ")

        # ── Active conversation window ────────────────────────────────────────
        # Stay active until ACTIVE_TIMEOUT seconds of silence with no speech
        session_active = True
        while session_active:
            state_ref.update({"state": "listening", "text": ""})

            # Only pause Spotify the moment speech is actually detected
            was_playing = False
            def on_speech_start():
                nonlocal was_playing
                was_playing = spotify_pause_if_playing()

            t0        = time.time()
            user_text = transcriber.listen(on_speech_start=on_speech_start)
            elapsed   = time.time() - t0

            if not user_text:
                # If speech was detected but filtered (hallucination), stay in session
                if elapsed > 0.5:
                    spotify_resume_if_was_playing(was_playing)
                    continue  # Keep listening, don't go idle
                # True silence — go idle
                speaker.wait_until_done()
                print("No speech detected, going idle.")
                go_idle()
                session_active = False
                continue

            print(f"You: {user_text}  [STT: {elapsed:.1f}s]")

            # Sleep on command — short, direct intent only (long sentences are questions, not commands)
            is_short = len(user_text.split()) <= 8
            if is_short and any(re.search(p, user_text.lower()) for p in config.SLEEP_COMMANDS):
                state_ref.update({"state": "speaking", "text": ""})
                for sentence in brain.think_stream(user_text, memory.get_history()):
                    speaker.speak(sentence)
                    state_ref.update({"state": "speaking", "text": sentence})
                speaker.wait_until_done()
                go_idle()
                session_active = False
                continue

            state_ref.update({"state": "thinking", "text": user_text})

            history       = memory.get_history()
            full_response = ""
            first         = True
            t_llm         = time.time()

            try:
                from llm.brain import ToolCall
                from tools.registry import execute_tool

                tool_call_id = "call_0"
                pending_tool = None

                for item in brain.think_stream(user_text, history):
                    if isinstance(item, ToolCall):
                        pending_tool = item
                        continue
                    if first:
                        print(f"VOX [first token: {time.time() - t_llm:.1f}s]: ", end="", flush=True)
                        first = False
                    print(item, end=" ", flush=True)
                    state_ref.update({"state": "speaking", "text": item})
                    speaker.speak(item)
                    full_response += item + " "

                # Execute tool and get spoken follow-up
                if pending_tool:
                    print(f"\n[Tool] {pending_tool.name}({pending_tool.args})")

                    # Speak a heads-up for slow tools
                    slow_tools = {"run_copilot", "find_project", "run_git", "run_gh", "run_shell"}
                    if pending_tool.name in slow_tools:
                        headsup = {
                            "run_copilot": "on it, passing this to Copilot now",
                            "find_project": "searching your drives for that project",
                            "run_git": "checking git",
                            "run_gh": "hitting GitHub",
                            "run_shell": "running that",
                        }.get(pending_tool.name, "working on it")
                        speaker.speak(headsup)
                        state_ref.update({"state": "thinking", "text": headsup})
                        speaker.wait_until_done()

                    state_ref.update({"state": "thinking", "text": f"running {pending_tool.name}…"})
                    result = execute_tool(pending_tool.name, pending_tool.args)
                    print(f"[Tool result] {result}")

                    for sentence in brain.think_with_tool_result(
                        user_text, history, pending_tool.name, tool_call_id, result
                    ):
                        if first:
                            print(f"VOX [tool reply: {time.time() - t_llm:.1f}s]: ", end="", flush=True)
                            first = False
                        print(sentence, end=" ", flush=True)
                        state_ref.update({"state": "speaking", "text": sentence})
                        speaker.speak(sentence)
                        full_response += sentence + " "

            except Exception as e:
                err = str(e)
                if "rate_limit" in err.lower() or "429" in err:
                    msg = "rate limit hit, give me a minute"
                else:
                    msg = "something went wrong, try again"
                print(f"\nError: {e}")
                state_ref.update({"state": "speaking", "text": msg})
                speaker.speak(msg)
                speaker.wait_until_done()
                go_idle()
                session_active = False
                continue

            print(f"\n  [LLM total: {time.time() - t_llm:.1f}s]")

            # Fallback if model returned nothing
            if not full_response.strip():
                fallback = "I got nothing on that one."
                speaker.speak(fallback)
                full_response = fallback

            speaker.wait_until_done()
            memory.add_turn(user_text, full_response.strip())

            # Resume Spotify if it was playing before we interrupted
            spotify_resume_if_was_playing(was_playing)

            state_ref.update({"state": "listening", "text": "..."})
