import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from livekit.agents import function_tool

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

SCOPE = "user-read-playback-state user-modify-playback-state"


def get_spotify():
    try:
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET,
                redirect_uri=SPOTIFY_REDIRECT_URI,
                scope=SCOPE
            )
        )
        return sp
    except Exception as e:
        return None


@function_tool
async def spotify_play_tool(query: str) -> str:
    sp = get_spotify()
    if not sp:
        return "❌ Spotify credentials missing or invalid."

    try:
        result = sp.search(q=query, type="track", limit=1)
        items = result["tracks"]["items"]

        if not items:
            return "❌ Song not found."

        track = items[0]
        uri = track["uri"]

        sp.start_playback(uris=[uri])

        name = track["name"]
        artist = track["artists"][0]["name"]

        return f"🎵 Playing '{name}' by {artist} on Spotify."

    except Exception as e:
        return f"❌ Spotify playback error: {e}"
