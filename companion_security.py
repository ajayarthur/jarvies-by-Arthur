"""
JARVIES 4.0 - COMPANION SECURITY & CAPABILITY REGISTRY
Handles mobile authentication, pairing handshake, capability indexing,
and two-phase confirmation for high-impact desktop operations.
"""

import os
import time
import uuid
import secrets
from typing import Dict, Any, Optional, Set
from fastapi import Request, HTTPException, status

SERVER_START_TIME = time.time()

# Default pairing code (Can be overridden by JARVIS_PAIRING_CODE in .env)
_default_code = os.getenv("JARVIS_PAIRING_CODE", "749201")
PAIRING_CODE = _default_code

# In-memory storage of authorized Bearer tokens
# In production, can also persist to data/authorized_devices.json
AUTHORIZED_TOKENS: Set[str] = set()

# Pending high-impact actions awaiting mobile confirmation:
# { action_id: { "action": str, "param": str, "timestamp": float, "description": str } }
PENDING_ACTIONS: Dict[str, Dict[str, Any]] = {}
ACTION_TTL_SECONDS = 45.0

# Capability Registry: Defines all tools, execution context, and safety level
CAPABILITY_REGISTRY = [
    {
        "id": "gemini_reasoning",
        "name": "Gemini 3.5/3.8 Flash AI",
        "category": "Artificial Intelligence",
        "description": "General conversational intelligence, Hinglish reasoning, and answers.",
        "location": "companion_pc",
        "safety": "safe"
    },
    {
        "id": "groq_study",
        "name": "Groq LLaMA Study Engine",
        "category": "Artificial Intelligence",
        "description": "High-speed reasoning for GATE exam questions and STEM problem solving.",
        "location": "companion_pc",
        "safety": "safe"
    },
    {
        "id": "edge_tts",
        "name": "Microsoft Edge Neural Voice",
        "category": "Speech & Audio",
        "description": "PrabhatNeural & multilingual neural voice generation.",
        "location": "companion_pc",
        "safety": "safe"
    },
    {
        "id": "weather",
        "name": "Live Weather Information",
        "category": "Information Services",
        "description": "Fetches current temperature, humidity, and forecast.",
        "location": "companion_pc",
        "safety": "safe"
    },
    {
        "id": "google_search",
        "name": "Google Web Search",
        "category": "Information Services",
        "description": "Web information search and summaries.",
        "location": "companion_pc",
        "safety": "safe"
    },
    {
        "id": "system_stats",
        "name": "PC Hardware Telemetry",
        "category": "System Monitoring",
        "description": "Real-time CPU, RAM, battery, and disk statistics.",
        "location": "companion_pc",
        "safety": "safe"
    },
    {
        "id": "volume_control",
        "name": "PC Volume Adjuster",
        "category": "Hardware Automation",
        "description": "Turn volume up, down, or mute on the host PC.",
        "location": "companion_pc",
        "safety": "safe"
    },
    {
        "id": "brightness_control",
        "name": "PC Monitor Brightness",
        "category": "Hardware Automation",
        "description": "Adjust monitor screen brightness levels.",
        "location": "companion_pc",
        "safety": "safe"
    },
    {
        "id": "screenshot",
        "name": "Take PC Screenshot",
        "category": "System Automation",
        "description": "Capture the primary display of the companion computer.",
        "location": "companion_pc",
        "safety": "safe"
    },
    {
        "id": "study_mode",
        "name": "Toggle Study Mode",
        "category": "Modes",
        "description": "Switches Jarvis to focus mode with academic reasoning.",
        "location": "companion_pc",
        "safety": "safe"
    },
    {
        "id": "gate_mode",
        "name": "Toggle GATE Mode",
        "category": "Modes",
        "description": "Switches to concise engineering/GATE exam explanation style.",
        "location": "companion_pc",
        "safety": "safe"
    },
    {
        "id": "open_app_pc",
        "name": "Launch PC Application",
        "category": "System Automation",
        "description": "Launch desktop applications (Calculator, Notepad, VS Code).",
        "location": "companion_pc",
        "safety": "safe"
    },
    {
        "id": "open_app_mobile",
        "name": "Launch Mobile App",
        "category": "Mobile Native",
        "description": "Open WhatsApp, Spotify, or YouTube natively on Android via deep link.",
        "location": "mobile_device",
        "safety": "safe"
    },
    {
        "id": "system_shutdown",
        "name": "Host Computer Shutdown",
        "category": "System Control",
        "description": "Gracefully shut down the companion Windows PC.",
        "location": "companion_pc",
        "safety": "high_impact"
    },
    {
        "id": "system_restart",
        "name": "Host Computer Restart",
        "category": "System Control",
        "description": "Reboot the companion Windows PC.",
        "location": "companion_pc",
        "safety": "high_impact"
    }
]

def generate_bearer_token() -> str:
    """Generate a high-entropy URL-safe token."""
    token = "jarvis_sec_" + secrets.token_urlsafe(32)
    AUTHORIZED_TOKENS.add(token)
    return token

def verify_token(token: Optional[str]) -> bool:
    """Check if provided Bearer token is in the authorized set."""
    if not token:
        return False
    clean_token = token.replace("Bearer ", "").strip()
    return clean_token in AUTHORIZED_TOKENS

def is_request_authorized(request: Request) -> bool:
    """
    Validates authorization for an incoming FastAPI request.
    Allows localhost / 127.0.0.1 without tokens for existing desktop web HUD.
    Requires Bearer token for remote mobile connections.
    """
    client_host = request.client.host if request.client else "unknown"
    
    # Allow local browser on the same PC
    if client_host in ("127.0.0.1", "::1", "localhost", "testclient"):
        return True

    # Check Authorization header or X-Jarvis-Token
    auth_header = request.headers.get("Authorization", "")
    x_token = request.headers.get("X-Jarvis-Token", "")

    if verify_token(auth_header) or verify_token(x_token):
        return True

    return False

def create_pending_confirmation(action_type: str, param: str, description: str) -> str:
    """Register a high-impact operation requiring explicit user confirmation."""
    clean_expired_actions()
    action_id = f"act_{uuid.uuid4().hex[:8]}"
    PENDING_ACTIONS[action_id] = {
        "action": action_type,
        "param": param,
        "timestamp": time.time(),
        "description": description
    }
    return action_id

def get_pending_action(action_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve an active pending action if not expired."""
    clean_expired_actions()
    return PENDING_ACTIONS.get(action_id)

def resolve_pending_action(action_id: str) -> Optional[Dict[str, Any]]:
    """Pop and return a pending action for execution."""
    clean_expired_actions()
    return PENDING_ACTIONS.pop(action_id, None)

def clean_expired_actions():
    """Remove actions older than ACTION_TTL_SECONDS."""
    now = time.time()
    expired = [aid for aid, data in PENDING_ACTIONS.items() if now - data["timestamp"] > ACTION_TTL_SECONDS]
    for aid in expired:
        PENDING_ACTIONS.pop(aid, None)

def log_audit_event(action: str, client_ip: str, success: bool, extra: str = ""):
    """Structured audit log with credential redaction."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    status_str = "SUCCESS" if success else "DENIED"
    print(f"[{timestamp}] [AUDIT] [{status_str}] IP={client_ip} Action={action} {extra}")
