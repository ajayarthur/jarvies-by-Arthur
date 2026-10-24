import os
import requests
from dotenv import load_dotenv
from livekit.agents import function_tool
from datetime import datetime

load_dotenv()

@function_tool
async def google_search_tool(query: str) -> str:
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    search_engine_id = os.getenv("SEARCH_ENGINE_ID")

    if not api_key or not search_engine_id:
        return "Google Search API keys missing."

    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": api_key, "cx": search_engine_id, "q": query, "num": 3}

    r = requests.get(url, params=params)
    if r.status_code != 200:
        return f"Google API Error: {r.status_code}"

    data = r.json()
    items = data.get("items", [])
    if not items:
        return "No results found."

    output = ""
    for i, it in enumerate(items, 1):
        output += f"{i}. {it.get('title')}\n{it.get('link')}\n{it.get('snippet')}\n\n"

    return output.strip()


@function_tool
async def get_current_datetime_tool() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
