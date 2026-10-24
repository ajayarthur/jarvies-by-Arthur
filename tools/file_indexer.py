import os
import json
import time
from pathlib import Path
from fuzzywuzzy import process
from livekit.agents import function_tool

CACHE = Path(".file_index_cache.json")
DIRS = ["D:/", "C:/Users"]


def build_index():
    items = []
    for base in DIRS:
        if not os.path.exists(base):
            continue
        for root, dirs, files in os.walk(base):
            for f in files:
                items.append({"name": f, "path": os.path.join(root, f)})

    return items


def save_cache(data):
    CACHE.write_text(json.dumps({"ts": time.time(), "items": data}))


def load_cache(hours=24):
    if not CACHE.exists():
        return None
    data = json.loads(CACHE.read_text())
    if time.time() - data["ts"] > hours * 3600:
        return None
    return data["items"]


@function_tool
async def play_file_tool(name: str) -> str:
    items = load_cache() or build_index()

    if not load_cache():
        save_cache(items)

    names = [f["name"] for f in items]

    match, score = process.extractOne(name, names)

    if score < 60:
        return "❌ File not found"

    file = next(f for f in items if f["name"] == match)

    try:
        os.startfile(file["path"])
        return f"📂 Opening {match}"
    except Exception as e:
        return f"❌ Cannot open: {e}"


@function_tool
async def file_indexer_tool(refresh: bool = False) -> str:
    if refresh or not load_cache():
        data = build_index()
        save_cache(data)
        return f"Indexed {len(data)} files"
    return "Index already fresh"
