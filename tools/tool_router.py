from livekit.agents import function_tool
from .intent_classifier import detect_intent
from .state_manager import is_study_mode, is_gate_mode
from .net_speed import check_internet_speed
from .groq_llm import groq_answer_tool
from .google_llm import gemini_answer_tool


@function_tool
async def tool_router_get_answer(query: str) -> str:
    intent = detect_intent(query)

    # GATE MODE
    if is_gate_mode():
        query = "Explain in GATE exam style: " + query
        return await groq_answer_tool(query)

    # Study Mode
    if is_study_mode():
        return await groq_answer_tool(query)

    # Intent based routing
    if intent in ("study", "coding"):
        return await groq_answer_tool(query)

    # Internet speed check
    speed = check_internet_speed()

    if speed == "fast":
        return await gemini_answer_tool(query)

    return await groq_answer_tool(query)
