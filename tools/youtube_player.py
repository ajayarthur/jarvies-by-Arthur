from livekit.agents import function_tool
import webbrowser
import requests
from urllib.parse import quote_plus

YOUTUBE_SEARCH_URL = "https://www.youtube.com/results?search_query="

@function_tool
async def play_youtube_song_tool(song: str):
    """
    Searches YouTube and plays the 1st result.
    """
    query = quote_plus(song)
    search_url = YOUTUBE_SEARCH_URL + query

    # Scrape for first video ID
    html = requests.get(search_url).text

    # Extract first video id
    import re
    match = re.search(r"watch\?v=([a-zA-Z0-9_-]{11})", html)
    
    if not match:
        return "❌ Song not found"

    vid = match.group(1)
    url = f"https://www.youtube.com/watch?v={vid}"
    webbrowser.open(url)

    return f"🎵 Playing: {song}"
