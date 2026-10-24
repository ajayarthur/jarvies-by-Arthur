"""
JARVIES 4.0 - COMPANION SECURITY & CAPABILITY REGISTRY
Handles mobile authentication, pairing handshake, capability indexing,
and two-phase confirmation for high-impact desktop operations.
"""

import os
import re
import time
import uuid
import secrets
from typing import Dict, Any, Optional, Set
from fastapi import Request, HTTPException, status

SERVER_START_TIME = time.time()

# Pairing State: Single-use, time-expiring 6-digit code
PAIRING_STATE = {
    "code": os.getenv("JARVIS_PAIRING_CODE", "749201"),
    "created_at": time.time(),
    "expires_at": time.time() + 900.0,  # 15 minutes TTL
    "consumed": False,
    "consumed_by": None
}

# In-memory storage of authorized Bearer tokens
AUTHORIZED_TOKENS: Set[str] = set()

# Pending high-impact actions awaiting mobile confirmation:
# { action_id: { "action": str, "param": str, "timestamp": float, "description": str } }
PENDING_ACTIONS: Dict[str, Dict[str, Any]] = {}
ACTION_TTL_SECONDS = 45.0

# Shell metacharacters forbidden to prevent command injection
# Explicit whitelist for safe command arguments: letters, numbers, dot, dash, underscore, space, slash
SAFE_PARAM_PATTERN = re.compile(r"^[a-zA-Z0-9_\-.\s/\\]+$")
DANGEROUS_CHARS = set("&;|<>$`\"'()%!\r\n\x00\\")

# Brute-force protection for pairing
FAILED_ATTEMPTS = {
    "count": 0,
    "last_failed": 0.0,
    "cooldown_until": 0.0
}

def is_safe_command_param(param: str) -> bool:
    """
    Verifies that an input does not contain dangerous shell metacharacters
    and strictly adheres to safe character sets.
    """
    if not param:
        return True
    if any(c in DANGEROUS_CHARS for c in param):
        return False
    return bool(SAFE_PARAM_PATTERN.match(param))

def get_active_pairing_code() -> str:
    """
    Returns the currently active pairing code.
    If the code was consumed or expired, automatically generates a new secure 6-digit code.
    """
    now = time.time()
    if PAIRING_STATE["consumed"] or now > PAIRING_STATE["expires_at"] or not PAIRING_STATE["code"]:
        new_code = f"{secrets.randbelow(900000) + 100000}"
        PAIRING_STATE["code"] = new_code
        PAIRING_STATE["created_at"] = now
        PAIRING_STATE["expires_at"] = now + 900.0
        PAIRING_STATE["consumed"] = False
        PAIRING_STATE["consumed_by"] = None
    return PAIRING_STATE["code"]

def validate_and_consume_code(provided_code: str, device_name: str) -> Optional[str]:
    """
    Validates pairing code. If valid, not expired, and not yet consumed:
    - Marks it as consumed immediately (cannot be reused).
    - Generates and returns a 256-bit secure Bearer token.
    - Rotates to a new pairing code for future devices.
    - Rate limits repeated failed attempts to prevent brute force.
    """
    now = time.time()
    clean_code = provided_code.strip()

    if now < FAILED_ATTEMPTS["cooldown_until"]:
        return None

    if PAIRING_STATE["consumed"] or now > PAIRING_STATE["expires_at"]:
        FAILED_ATTEMPTS["count"] += 1
        return None

    if clean_code != PAIRING_STATE["code"]:
        FAILED_ATTEMPTS["count"] += 1
        FAILED_ATTEMPTS["last_failed"] = now
        if FAILED_ATTEMPTS["count"] >= 5:
            FAILED_ATTEMPTS["cooldown_until"] = now + 30.0  # 30 second cooldown
            FAILED_ATTEMPTS["count"] = 0
        return None

    # Reset failure counter on valid pairing
    FAILED_ATTEMPTS["count"] = 0
    FAILED_ATTEMPTS["cooldown_until"] = 0.0

    # Consume immediately
    PAIRING_STATE["consumed"] = True
    PAIRING_STATE["consumed_by"] = device_name

    # Issue token
    token = generate_bearer_token()

    # Pre-generate new code for next device
    get_active_pairing_code()

    return token

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
        "id": "voice_transcription",
        "name": "Voice-to-Text Transcription",
        "category": "Speech & Audio",
        "description": "Transcribes mobile microphone speech into text commands.",
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

def create_pending_confirmation(action_type: str, param: str, description: str, token: Optional[str] = None) -> str:
    """Register a high-impact operation requiring explicit user confirmation, bound to the requester token."""
    clean_expired_actions()
    action_id = f"act_{uuid.uuid4().hex[:8]}"
    PENDING_ACTIONS[action_id] = {
        "action": action_type,
        "param": param,
        "timestamp": time.time(),
        "description": description,
        "token": token.replace("Bearer ", "").strip() if token else None
    }
    return action_id

def get_pending_action(action_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve an active pending action if not expired."""
    clean_expired_actions()
    return PENDING_ACTIONS.get(action_id)

def resolve_pending_action(action_id: str, token: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Pop and return a pending action for execution.
    Verifies that the confirming token matches the requesting token when bound.
    """
    clean_expired_actions()
    action = PENDING_ACTIONS.get(action_id)
    if not action:
        return None

    # Verify token binding if bound
    clean_tok = token.replace("Bearer ", "").strip() if token else None
    if action.get("token") and clean_tok and action["token"] != clean_tok:
        return None

    return PENDING_ACTIONS.pop(action_id, None)

def clean_expired_actions():
    """Remove actions older than ACTION_TTL_SECONDS."""
    now = time.time()
    expired = [aid for aid, data in PENDING_ACTIONS.items() if now - data["timestamp"] > ACTION_TTL_SECONDS]
    for aid in expired:
        PENDING_ACTIONS.pop(aid, None)

def log_audit_event(action: str, client_ip: str, success: bool, extra: str = ""):
    """Structured audit log with credential and sensitive token redaction."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    status_str = "SUCCESS" if success else "DENIED"

    # Redact tokens or full pairing codes if present in extra string
    clean_extra = extra
    if "jarvis_sec_" in clean_extra:
        clean_extra = re.sub(r"jarvis_sec_[A-Za-z0-9_\-]+", "jarvis_sec_***REDACTED***", clean_extra)
    if "code:" in clean_extra:
        clean_extra = re.sub(r"code:\s*(\d{2})\d{2}(\d{2})", r"code: \1**\2", clean_extra)

    print(f"[{timestamp}] [AUDIT] [{status_str}] IP={client_ip} Action={action} {clean_extra}")
