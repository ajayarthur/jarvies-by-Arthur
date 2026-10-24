from tools.intent_classifier import detect_intent
from tools.state_manager import is_study_mode, is_gate_mode
from tools.groq_llm import groq_answer_tool
from tools.google_llm import gemini_answer_tool
from tools.net_speed import check_internet_speed


async def get_best_answer(query: str):
    """
    Smart LLM router:
    - If GATE mode → force Groq (exam-style answers)
    - If Study Mode → Groq
    - If Intent is 'study' or 'coding' → Groq
    - If network fast → Gemini
    - Else fallback → Groq
    """

    # 1️⃣ GATE MODE ALWAYS uses Groq
    if is_gate_mode():
        query = "Explain in GATE exam style: " + query
        return await groq_answer_tool(query)

    # 2️⃣ Study Mode always uses Groq
    if is_study_mode():
        return await groq_answer_tool(query)

    # 3️⃣ Intent detection
    intent = detect_intent(query)
    if intent in ("study", "coding"):
        return await groq_answer_tool(query)

    # 4️⃣ Internet speed-based decision
    speed = check_internet_speed()
    if speed == "fast":
        return await gemini_answer_tool(query)

    # 5️⃣ Default fallback
    return await groq_answer_tool(query)
