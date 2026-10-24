from livekit.agents import function_tool
from .state_manager import set_study_mode, is_study_mode


@function_tool
async def study_mode_tool(mode: str) -> str:
    """
    Enables or disables study mode.
    Usage:
    - "on"
    - "off"
    """

    mode = mode.lower()

    if mode in ["on", "enable", "start"]:
        set_study_mode(True)
        return "📚 Study Mode ENABLED"

    if mode in ["off", "disable", "stop"]:
        set_study_mode(False)
        return "📚 Study Mode DISABLED"

    return "❌ Invalid value. Use: on / off"
