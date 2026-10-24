# tools/brightness.py
import platform
from livekit.agents import function_tool

@function_tool
async def brightness_tool(action: str, level: int = None) -> str:
    if platform.system().lower() != "windows":
        return "❌ Brightness control only implemented for Windows."
    try:
        import wmi
        w = wmi.WMI(namespace='wmi')
        methods = w.WmiMonitorBrightnessMethods()[0]
        if action == "set" and level is not None:
            methods.WmiSetBrightness(level, 0)
            return f"🔆 Brightness set to {level}%"
        elif action == "up":
            return await brightness_tool("set", min(100, (level or 50) + 10))
        elif action == "down":
            return await brightness_tool("set", max(0, (level or 50) - 10))
        else:
            return "❌ Invalid brightness action"
    except Exception as e:
        return f"❌ Brightness error: {e}"
