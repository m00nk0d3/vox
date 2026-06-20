"""
Spotify tools — VOX can search, play, pause, skip, and control volume.
Uses spotipy with OAuth (browser auth on first run, token cached after).
"""

import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

SCOPES = " ".join([
    "user-modify-playback-state",
    "user-read-playback-state",
    "user-read-currently-playing",
    "streaming",
])

_sp = None


def _client() -> spotipy.Spotify:
    global _sp
    if _sp is None:
        _sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
            scope=SCOPES,
            cache_path=".spotify_cache",
            open_browser=True,
        ))
    return _sp


def _active_device_id() -> str | None:
    """Return the first active device ID, or None."""
    devices = _client().devices()
    devs = devices.get("devices", [])
    # Prefer active device
    for d in devs:
        if d["is_active"]:
            return d["id"]
    # Fall back to first available
    return devs[0]["id"] if devs else None


def spotify_play(query: str) -> str:
    """Search Spotify and play the best match (track, artist, or playlist)."""
    sp = _client()
    device_id = _active_device_id()
    if not device_id:
        return "No active Spotify device found. Open Spotify on any device first."

    # Try track first, then artist
    results = sp.search(q=query, limit=1, type="track,artist,playlist")

    track = results["tracks"]["items"][0] if results["tracks"]["items"] else None
    artist = results["artists"]["items"][0] if results["artists"]["items"] else None
    playlist = results["playlists"]["items"][0] if results["playlists"]["items"] else None

    if track:
        sp.start_playback(device_id=device_id, uris=[track["uri"]])
        return f"Playing '{track['name']}' by {track['artists'][0]['name']}."
    elif artist:
        sp.start_playback(device_id=device_id, context_uri=artist["uri"])
        return f"Playing top tracks by {artist['name']}."
    elif playlist:
        sp.start_playback(device_id=device_id, context_uri=playlist["uri"])
        return f"Playing playlist '{playlist['name']}'."
    else:
        return f"Nothing found for '{query}' on Spotify."


def spotify_pause() -> str:
    """Pause Spotify playback."""
    try:
        _client().pause_playback()
        return "Paused."
    except Exception as e:
        return f"Couldn't pause: {e}"


def spotify_resume() -> str:
    """Resume Spotify playback."""
    try:
        _client().start_playback()
        return "Resumed."
    except Exception as e:
        return f"Couldn't resume: {e}"


def spotify_next() -> str:
    """Skip to the next track."""
    try:
        _client().next_track()
        return "Skipped to next track."
    except Exception as e:
        return f"Couldn't skip: {e}"


def spotify_previous() -> str:
    """Go back to the previous track."""
    try:
        _client().previous_track()
        return "Going back."
    except Exception as e:
        return f"Couldn't go back: {e}"


def spotify_volume(level: int) -> str:
    """Set Spotify volume (0–100)."""
    level = max(0, min(100, level))
    try:
        device_id = _active_device_id()
        _client().volume(level, device_id=device_id)
        return f"Volume set to {level}%."
    except Exception as e:
        return f"Couldn't set volume: {e}"


def spotify_now_playing() -> str:
    """Return what's currently playing."""
    current = _client().current_playback()
    if not current or not current.get("item"):
        return "Nothing is playing right now."
    item = current["item"]
    artist = item["artists"][0]["name"]
    track = item["name"]
    return f"Currently playing '{track}' by {artist}."
