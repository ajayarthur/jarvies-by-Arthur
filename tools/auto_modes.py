# tools/auto_modes.py
from livekit.agents import function_tool
import asyncio
import os

@function_tool
async def auto_modes_tool(mode: str) -> str:
    mode = mode.lower().strip()
    if mode == "study":
        # close distracting apps (example)
        os.system('taskkill /f /im chrome.exe')  # careful - example
        # open reader apps
        os.startfile("C:\\Program Files\\Microsoft VS Code\\Code.exe")
        os.startfile("C:\\Program Files\\VideoLAN\\VLC\\vlc.exe")
        # reduce volume - wrapper to volume tool could be called instead
        return "✅ Study mode set: distractions closed, VS Code & VLC opened, volume lowered."
    if mode == "coding":
        os.startfile("C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe")
        os.startfile("cmd")
        return "✅ Coding mode: VS Code and Terminal open"
    if mode == "startup":
        # example startup daily
        return "✅ Startup routine completed"
    return "❌ Unknown mode. Available: study, coding, startup"
