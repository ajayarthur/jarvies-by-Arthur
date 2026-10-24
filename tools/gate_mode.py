from livekit.agents import function_tool
from .state_manager import set_gate_mode, is_gate_mode

@function_tool
async def gate_mode_tool(mode: str) -> str:
    mode = mode.lower()

    if mode in ["on", "enable", "start"]:
        set_gate_mode(True)
        return "🎓 GATE Mode ENABLED"

    if mode in ["off", "disable", "stop"]:
        set_gate_mode(False)
        return "🎓 GATE Mode DISABLED"

    return "❌ Use: on / off"
