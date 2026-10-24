from livekit.agents import function_tool
import re

STUDY_KEYWORDS = [
    "what is", "define", "explain", "derive", "gate", "pyq",
    "difference between", "short note", "notes", "theorem",
    "algorithm", "complexity", "formula", "concept", "theory"
]

CODING_KEYWORDS = [
    "dsa", "leet", "leetcode", "algo", "binary search",
    "dp", "dynamic programming", "linked list", 
    "tree", "graph", "stack", "queue"
]

def detect_intent(query: str):
    q = query.lower()

    # Study-related intent
    for k in STUDY_KEYWORDS:
        if k in q:
            return "study"

    # Coding intent
    for k in CODING_KEYWORDS:
        if k in q:
            return "coding"

    return "general"

@function_tool
async def classify_intent_tool(query: str):
    return detect_intent(query)
