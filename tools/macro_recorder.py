from livekit.agents import function_tool
import json
from pathlib import Path
import time

MACRO = Path("macros.json")


@function_tool
async def macro_recorder_tool(action: str, name: str = "", duration: int = 5) -> str:
    if action == "record":
        # Real recording needs pynput → too risky without safety
        data = json.loads(MACRO.read_text()) if MACRO.exists() else {}
        macro_name = name or f"macro_{int(time.time())}"
        data[macro_name] = ["placeholder macro"]
        MACRO.write_text(json.dumps(data))
        return f"🔴 Macro '{macro_name}' recorded (placeholder)"

    if action == "list":
        data = json.loads(MACRO.read_text()) if MACRO.exists() else {}
        return "Available macros: " + ", ".join(data.keys())

    if action == "play":
        if not MACRO.exists():
            return "❌ No macros"
        data = json.loads(MACRO.read_text())
        if name not in data:
            return "❌ Macro not found"
        return f"▶ Playing macro {name} (placeholder)"

    return "❌ Invalid action"
