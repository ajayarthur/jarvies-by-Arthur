import os
import socket
import httpx
from dotenv import load_dotenv

# Ensure socket queries prefer IPv4 to bypass broken ISP IPv6 routes
_orig_getaddrinfo = socket.getaddrinfo

def _ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    try:
        return _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
    except Exception:
        return _orig_getaddrinfo(host, port, family, type, proto, flags)

socket.getaddrinfo = _ipv4_getaddrinfo

try:
    from livekit.agents import function_tool
except Exception:
    def function_tool(func):
        return func

load_dotenv()

# Active, high-speed Gemini models verified on this API key
CANDIDATE_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.8-flash",
    "gemini-flash-latest",
]

@function_tool
async def gemini_answer_tool(prompt: str) -> str:
    """
    Fast and stable Gemini text answer for Jarvies using official REST API.
    """
    load_dotenv(override=False)
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Gemini error: GOOGLE_API_KEY or GEMINI_API_KEY is not set."

    last_error = None
    async with httpx.AsyncClient(timeout=12.0) as client:
        for model_name in CANDIDATE_MODELS:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {"text": prompt}
                            ]
                        }
                    ]
                }
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"].strip()
                elif response.status_code == 404:
                    # Model not found or deprecated, try next candidate
                    last_error = f"Model {model_name} not available (404)"
                    continue
                elif response.status_code == 503:
                    # Model temporarily overloaded, try next candidate
                    last_error = f"Model {model_name} busy (503)"
                    continue
                else:
                    last_error = f"API error {response.status_code}: {response.text[:200]}"
            except Exception as e:
                last_error = str(e)
                continue

    return f"Gemini error: {last_error}"


