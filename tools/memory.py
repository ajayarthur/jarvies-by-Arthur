from livekit.agents import function_tool
import json
import os
from pathlib import Path

MEM_FILE = Path(os.getenv("MEMORY_FILE", "data/memory.json"))
MEM_FILE.parent.mkdir(parents=True, exist_ok=True)

if not MEM_FILE.exists():
    MEM_FILE.write_text("{}")


def load_mem():
    return json.loads(MEM_FILE.read_text())


def save_mem(data):
    MEM_FILE.write_text(json.dumps(data, indent=2))


@function_tool
async def memory_get_tool(key: str) -> str:
    data = load_mem()
    return data.get(key, "❌ Not found")


@function_tool
async def memory_set_tool(key: str, value: str) -> str:
    data = load_mem()
    data[key] = value
    save_mem(data)
    return f"💾 Saved: {key} = {value}"
