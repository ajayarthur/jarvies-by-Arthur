import os
import sys
import time
import socket
import subprocess
import threading
import webbrowser
import asyncio
from pathlib import Path

# UTF-8 stdout configuration for Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import psutil
import uvicorn
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import voice_to_text

load_dotenv()

from tts_helper import generate_tts_file, speak_text
from tools.system_control import system_controller
from tools.google_llm import gemini_answer_tool
from tools.groq_llm import groq_answer_tool
from tools.weather import weather_tool
from tools.brightness import brightness_tool
from tools.google_search import google_search_tool, get_current_datetime_tool
from tools.net_speed import net_status_tool
from tools.state_manager import is_study_mode, set_study_mode, is_gate_mode, set_gate_mode
import companion_security as sec

PROJECT_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
TTS_CACHE_DIR = PROJECT_ROOT / "tts_cache"
TTS_CACHE_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Jarvies 4.0 - Advanced AI Desktop Assistant")

# Enable CORS for mobile app connectivity across network
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
app.mount("/assets", StaticFiles(directory=str(PROJECT_ROOT / "assets")), name="assets")


class ChatRequest(BaseModel):
    message: str
    voice: str = "en-IN-PrabhatNeural"
    play_on_speaker: bool = False


class ToolRequest(BaseModel):
    action: str
    param: str = ""


class PairRequest(BaseModel):
    pairing_code: str
    device_name: str = "Android Device"


class ConfirmRequest(BaseModel):
    action_id: str
    confirmed: bool


def free_port_if_occupied(port: int = 7777):
    """Automatically frees the port if occupied by a stale process on Windows."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return  # Port is free

        cmd = f'netstat -ano | findstr :{port}'
        output = subprocess.check_output(cmd, shell=True, text=True)
        for line in output.strip().splitlines():
            if f':{port}' in line and 'LISTENING' in line:
                pid = int(line.strip().split()[-1])
                if pid != os.getpid() and pid > 0:
                    print(f"[*] Releasing stale process (PID {pid}) on port {port}...")
                    subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
                    time.sleep(1.0)
    except Exception:
        pass


@app.get("/")
async def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    return FileResponse(str(index_file))


@app.get("/manifest.json")
async def serve_manifest():
    manifest_file = FRONTEND_DIR / "manifest.json"
    return FileResponse(str(manifest_file), media_type="application/manifest+json")


@app.get("/sw.js")
async def serve_sw():
    sw_file = FRONTEND_DIR / "sw.js"
    return FileResponse(str(sw_file), media_type="application/javascript")



@app.get("/api/audio/{filename}")
async def serve_audio(filename: str):
    file_path = TTS_CACHE_DIR / filename
    if file_path.exists():
        return FileResponse(str(file_path), media_type="audio/wav")
    return JSONResponse(status_code=404, content={"error": "Audio file not found"})


@app.get("/api/health")
async def health_check():
    """Health check for companion desktop service and network connectivity."""
    return {
        "status": "healthy",
        "service": "Jarvis Companion Core",
        "version": "4.0.0",
        "platform": sys.platform,
        "hostname": socket.gethostname(),
        "pairing_required": True,
        "paired_devices_count": len(sec.AUTHORIZED_TOKENS),
        "uptime_seconds": round(time.time() - sec.SERVER_START_TIME, 1)
    }


@app.post("/api/auth/pair")
async def pair_device(req: PairRequest, request: Request):
    """
    Pairs an Android device using the single-use expiring 6-digit code shown in the PC console.
    Returns an authorized Bearer token for subsequent requests.
    """
    client_ip = request.client.host if request.client else "unknown"
    token = sec.validate_and_consume_code(req.pairing_code, req.device_name)

    if not token:
        sec.log_audit_event("PAIR_ATTEMPT", client_ip, False, f"Invalid or expired code: {req.pairing_code}")
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "Invalid, expired, or already-used pairing code. Check PC console."}
        )

    sec.log_audit_event("PAIR_SUCCESS", client_ip, True, f"Device: {req.device_name}")

    return {
        "success": True,
        "token": token,
        "server_name": "Arthur's Jarvis Core",
        "hostname": socket.gethostname(),
        "message": f"Device '{req.device_name}' paired successfully with Jarvis!"
    }


@app.post("/api/voice/transcribe")
async def transcribe_voice_endpoint(request: Request, file: UploadFile = File(...)):
    """
    Accepts recorded voice audio from Android mobile app and transcribes it to text.
    """
    if not sec.is_request_authorized(request):
        return JSONResponse(status_code=401, content={"success": False, "error": "Unauthorized device."})

    try:
        content = await file.read()
        temp_wav = TTS_CACHE_DIR / f"upload_{int(time.time() * 1000)}.wav"
        temp_wav.write_bytes(content)

        transcribed_text = voice_to_text.transcribe_audio_file(str(temp_wav))

        try:
            temp_wav.unlink(missing_ok=True)
        except Exception:
            pass

        return {
            "success": True,
            "transcript": transcribed_text,
            "language": "en-IN"
        }
    except Exception as e:
        return {"success": False, "error": str(e), "transcript": ""}


@app.get("/api/capabilities")
async def list_capabilities(request: Request):
    """Returns the capability registry for the mobile app to index available features."""
    return {
        "success": True,
        "capabilities": sec.CAPABILITY_REGISTRY,
        "total": len(sec.CAPABILITY_REGISTRY)
    }


@app.post("/api/confirm_action")
async def confirm_action_endpoint(req: ConfirmRequest, request: Request):
    """
    Second-phase execution protocol: Confirms and executes high-impact operations
    (e.g. host PC shutdown, reboot) after mobile user authorization.
    """
    if not sec.is_request_authorized(request):
        return JSONResponse(status_code=401, content={"success": False, "error": "Unauthorized."})

    client_ip = request.client.host if request.client else "unknown"
    token = request.headers.get("Authorization", "") or request.headers.get("X-Jarvis-Token", "")
    action_data = sec.resolve_pending_action(req.action_id, token)

    if not action_data:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "Action expired or not found. Please request again."}
        )

    if not req.confirmed:
        sec.log_audit_event("ACTION_CANCELLED", client_ip, True, f"Action: {action_data['action']}")
        return {"success": True, "executed": False, "message": "Action was cancelled by user."}

    action_type = action_data["action"]
    param = action_data.get("param", "")
    result = ""

    try:
        if action_type in ("system_shutdown", "shutdown"):
            delay = int(param) if param.isdigit() else 30
            result = await system_controller.system_shutdown(delay=delay)
        elif action_type in ("system_restart", "restart"):
            delay = int(param) if param.isdigit() else 30
            result = await system_controller.system_restart(delay=delay)
        else:
            result = f"Unknown confirmed action: {action_type}"

        sec.log_audit_event("ACTION_CONFIRMED", client_ip, True, f"Action: {action_type} - {result}")
        return {"success": True, "executed": True, "result": result}
    except Exception as e:
        sec.log_audit_event("ACTION_ERROR", client_ip, False, f"Action: {action_type} - {e}")
        return {"success": False, "error": str(e)}


@app.post("/api/cancel_action")
async def cancel_action_endpoint(req: ConfirmRequest, request: Request):
    """Explicitly cancels a pending high-impact action."""
    if not sec.is_request_authorized(request):
        return JSONResponse(status_code=401, content={"success": False, "error": "Unauthorized."})
    token = request.headers.get("Authorization", "") or request.headers.get("X-Jarvis-Token", "")
    sec.resolve_pending_action(req.action_id, token)
    return {"success": True, "message": "Pending action cancelled."}


@app.get("/api/system/stats")
async def get_system_stats(request: Request):
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage(str(PROJECT_ROOT))
        battery = psutil.sensors_battery()
        battery_pct = battery.percent if battery else None
        battery_plugged = battery.power_plugged if battery else None

        return {
            "cpu_percent": cpu,
            "memory_percent": mem.percent,
            "memory_used_gb": round(mem.used / (1024**3), 2),
            "memory_total_gb": round(mem.total / (1024**3), 2),
            "disk_percent": disk.percent,
            "battery_percent": battery_pct,
            "battery_plugged": battery_plugged,
            "study_mode": is_study_mode(),
            "gate_mode": is_gate_mode(),
            "status": "online"
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}


@app.post("/api/execute_tool")
async def execute_tool_endpoint(req: ToolRequest, request: Request):
    if not sec.is_request_authorized(request):
        return JSONResponse(status_code=401, content={"success": False, "error": "Unauthorized device."})

    action = req.action.lower()
    param = req.param.strip()
    result = ""
    token = request.headers.get("Authorization", "") or request.headers.get("X-Jarvis-Token", "")

    # High-impact security check: Require mobile confirmation for shutdown/restart
    if action in ("system_shutdown", "shutdown"):
        aid = sec.create_pending_confirmation("system_shutdown", param or "30", "Host PC Shutdown (30s delay)", token)
        return {
            "success": True,
            "requires_confirmation": True,
            "pending_action_id": aid,
            "action_type": "system_shutdown",
            "action_description": "Are you sure you want to shut down the host PC?",
            "result": "Confirmation required on mobile."
        }

    if action in ("system_restart", "restart"):
        aid = sec.create_pending_confirmation("system_restart", param or "30", "Host PC Reboot (30s delay)", token)
        return {
            "success": True,
            "requires_confirmation": True,
            "pending_action_id": aid,
            "action_type": "system_restart",
            "action_description": "Are you sure you want to restart the host PC?",
            "result": "Confirmation required on mobile."
        }

    try:
        if action == "volume_up":
            result = await system_controller.control_volume("up")
        elif action == "volume_down":
            result = await system_controller.control_volume("down")
        elif action == "volume_mute":
            result = await system_controller.control_volume("mute")
        elif action == "brightness_up":
            result = await brightness_tool("up")
        elif action == "brightness_down":
            result = await brightness_tool("down")
        elif action == "screenshot":
            result = await system_controller.take_screenshot()
        elif action == "toggle_study_mode":
            new_val = not is_study_mode()
            set_study_mode(new_val)
            result = f"Study Mode set to {'ON' if new_val else 'OFF'}"
        elif action == "toggle_gate_mode":
            new_val = not is_gate_mode()
            set_gate_mode(new_val)
            result = f"GATE Mode set to {'ON' if new_val else 'OFF'}"
        elif action == "weather":
            result = await weather_tool(param)
        elif action == "google_search":
            result = await google_search_tool(param)
        elif action in ("net_speed", "net_status"):
            result = await net_status_tool()
        elif action in ("datetime", "time"):
            result = await get_current_datetime_tool()
        elif action == "open_app":
            app_map = {
                "youtube": "https://youtube.com",
                "spotify": "https://open.spotify.com",
                "whatsapp": "https://web.whatsapp.com",
                "github": "https://github.com",
                "linkedin": "https://linkedin.com",
                "chatgpt": "https://chatgpt.com"
            }
            if param.lower() in app_map:
                webbrowser.open(app_map[param.lower()])
                result = f"Opened {param.title()}"
            elif param.lower() == "calc":
                subprocess.Popen("calc.exe", shell=True)
                result = "Opened Calculator"
            elif param.lower() == "notepad":
                subprocess.Popen("notepad.exe", shell=True)
                result = "Opened Notepad"
            else:
                client_ip = request.client.host if request.client else "unknown"
                if not sec.is_safe_command_param(param):
                    sec.log_audit_event("INJECTION_BLOCKED", client_ip, False, f"Blocked parameter: {param[:30]}")
                    return {"success": False, "error": "Security violation: Command parameter contains illegal shell characters."}
                result = await system_controller.open_application(param)
        elif action == "system_info":
            result = await system_controller.get_system_info()
        else:
            result = f"Unknown tool action: {action}"

        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest, request: Request):
    if not sec.is_request_authorized(request):
        return JSONResponse(status_code=401, content={"success": False, "error": "Unauthorized device. Pair via /api/auth/pair."})

    user_text = req.message.strip()
    if not user_text:
        return {"reply": "Kuch toh boliye sir!", "audio_url": None, "tool_executed": None}

    lower_text = user_text.lower()
    tool_executed = None
    reply = ""
    token = request.headers.get("Authorization", "") or request.headers.get("X-Jarvis-Token", "")

    # High-impact voice instruction check: require confirmation
    if ("shutdown" in lower_text or "shut down" in lower_text) and ("pc" in lower_text or "system" in lower_text or "computer" in lower_text or len(lower_text) < 15):
        aid = sec.create_pending_confirmation("system_shutdown", "30", "Host PC Shutdown (30s delay)", token)
        return {
            "reply": "Sir, this will shut down your computer. Please confirm on your mobile screen.",
            "audio_url": None,
            "tool_executed": "system_shutdown",
            "requires_confirmation": True,
            "pending_action_id": aid,
            "action_type": "system_shutdown",
            "action_description": "Host PC Shutdown in 30 seconds",
            "success": True
        }

    if ("restart" in lower_text or "reboot" in lower_text) and ("pc" in lower_text or "system" in lower_text or "computer" in lower_text or len(lower_text) < 15):
        aid = sec.create_pending_confirmation("system_restart", "30", "Host PC Reboot (30s delay)", token)
        return {
            "reply": "Sir, this will reboot your computer. Please confirm on your mobile screen.",
            "audio_url": None,
            "tool_executed": "system_restart",
            "requires_confirmation": True,
            "pending_action_id": aid,
            "action_type": "system_restart",
            "action_description": "Host PC Reboot in 30 seconds",
            "success": True
        }

    # 1. DIRECT HARDWARE & COMMAND PARSER
    if "volume up" in lower_text or "aawaz badhao" in lower_text or "sound badhao" in lower_text:
        tool_executed = "volume_up"
        reply = await system_controller.control_volume("up")

    elif "volume down" in lower_text or "aawaz kam karo" in lower_text or "sound kam karo" in lower_text:
        tool_executed = "volume_down"
        reply = await system_controller.control_volume("down")

    elif "mute" in lower_text and ("volume" in lower_text or "sound" in lower_text or "unmute" in lower_text):
        tool_executed = "volume_mute"
        reply = await system_controller.control_volume("mute")

    elif "screenshot" in lower_text or "screen capture" in lower_text or "photo lo" in lower_text:
        tool_executed = "screenshot"
        reply = await system_controller.take_screenshot()

    elif "brightness up" in lower_text or "brightness badhao" in lower_text:
        tool_executed = "brightness_up"
        reply = await brightness_tool("up")

    elif "brightness down" in lower_text or "brightness kam karo" in lower_text:
        tool_executed = "brightness_down"
        reply = await brightness_tool("down")

    elif "open youtube" in lower_text or "youtube chalao" in lower_text or "youtube kholo" in lower_text:
        tool_executed = "open_youtube"
        webbrowser.open("https://youtube.com")
        reply = "YouTube open kar diya hai sir."

    elif "open spotify" in lower_text or "spotify kholo" in lower_text:
        tool_executed = "open_spotify"
        webbrowser.open("https://open.spotify.com")
        reply = "Spotify open kar diya hai sir."

    elif "open whatsapp" in lower_text or "whatsapp kholo" in lower_text:
        tool_executed = "open_whatsapp"
        webbrowser.open("https://web.whatsapp.com")
        reply = "WhatsApp Web open kar diya hai sir."

    elif "open github" in lower_text or "github kholo" in lower_text:
        tool_executed = "open_github"
        webbrowser.open("https://github.com")
        reply = "GitHub khol diya hai sir."

    elif "open linkedin" in lower_text or "linkedin kholo" in lower_text:
        tool_executed = "open_linkedin"
        webbrowser.open("https://linkedin.com")
        reply = "LinkedIn khol diya hai sir."

    elif "open calculator" in lower_text or "calculator kholo" in lower_text:
        tool_executed = "open_calc"
        subprocess.Popen("calc.exe", shell=True)
        reply = "Calculator khol diya hai sir."

    elif "open notepad" in lower_text or "notepad kholo" in lower_text:
        tool_executed = "open_notepad"
        subprocess.Popen("notepad.exe", shell=True)
        reply = "Notepad khol diya hai sir."

    elif "system info" in lower_text or "pc stats" in lower_text or "specs" in lower_text:
        tool_executed = "system_info"
        reply = await system_controller.get_system_info()

    elif "study mode" in lower_text:
        new_val = not is_study_mode()
        set_study_mode(new_val)
        tool_executed = "toggle_study_mode"
        reply = f"Study Mode ab {'ON' if new_val else 'OFF'} hai sir."

    elif "gate mode" in lower_text:
        new_val = not is_gate_mode()
        set_gate_mode(new_val)
        tool_executed = "toggle_gate_mode"
        reply = f"GATE Mode ab {'ON' if new_val else 'OFF'} hai sir."

    elif "weather" in lower_text or "mausam" in lower_text:
        tool_executed = "weather"
        city = ""
        for word in ("weather in ", "weather of ", "mausam in "):
            if word in lower_text:
                city = lower_text.split(word, 1)[1].strip()
                break
        reply = await weather_tool(city)

    elif "internet speed" in lower_text or "net speed" in lower_text or "wifi speed" in lower_text:
        tool_executed = "net_status"
        reply = await net_status_tool()

    elif "what time" in lower_text or "current time" in lower_text or "kya time" in lower_text or "aaj kya date" in lower_text:
        tool_executed = "datetime"
        dt_str = await get_current_datetime_tool()
        reply = f"Sir, abhi current date & time hai: {dt_str}"

    # 2. INTELLIGENT AI REASONING ROUTER
    if not reply:
        if is_gate_mode():
            query = "Explain in concise GATE exam style: " + user_text
            res = await groq_answer_tool(query)
            reply = str(res)
        elif is_study_mode():
            res = await groq_answer_tool(user_text)
            reply = str(res)
        else:
            prompt = (
                "You are Jarvies, an advanced AI assistant created by Arthur sir. "
                "Reply in natural Hinglish, short, witty, and smart (max 2-3 sentences).\n\n"
                f"User: {user_text}\nJarvies:"
            )
            res = await gemini_answer_tool(prompt)
            res_str = str(res)

            # Friendly fallback if Gemini API key is placeholder
            if "API key not valid" in res_str or "API_KEY_INVALID" in res_str or "Gemini error" in res_str:
                reply = (
                    "Sir, main Jarvies hoon! Aapka system automation, volume, brightness, screenshots aur tools "
                    "completely ready hain. Live AI conversation ke liye please .env file mein apna Gemini API key configure karein."
                )
            else:
                reply = res_str

    # 3. GENERATE AUDIO WITH EDGE NEURAL TTS
    audio_url = None
    try:
        audio_filename = await generate_tts_file(reply, voice=req.voice)
        audio_url = f"/api/audio/{audio_filename}"

        if req.play_on_speaker:
            asyncio.create_task(speak_text(reply, voice=req.voice))
    except Exception as e:
        print("TTS Generation Error:", e)

    return {
        "reply": reply,
        "audio_url": audio_url,
        "tool_executed": tool_executed,
        "success": True
    }


def open_browser():
    time.sleep(1.5)
    url = "http://127.0.0.1:7777"
    print(f"\n[Jarvies 4.0] 🚀 Opening Holographic Web Dashboard in browser: {url}")
    webbrowser.open(url)


def launch_cloudflare_tunnel(port: int = 7777):
    cloudflared_bin = PROJECT_ROOT / "cloudflared.exe"
    if cloudflared_bin.exists():
        try:
            print("[*] Launching Cloudflare Tunnel for public access...")
            cmd = f'"{cloudflared_bin}" tunnel --url http://127.0.0.1:{port}'
            subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print("[Tunnel Error]", e)


def main():
    port = 7777
    free_port_if_occupied(port)

    # Detect local IP address for easy mobile pairing
    local_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    print("=" * 68)
    print("      🚀 JARVIES 4.0 - AI DESKTOP ASSISTANT & MOBILE COMPANION")
    print("=" * 68)
    print(f"[*] Local PC Dashboard:   http://127.0.0.1:{port}")
    print(f"[*] Android Mobile URL:   http://{local_ip}:{port}")
    print(f"[*] Mobile Pairing Code:  {sec.get_active_pairing_code()} (Valid for 15 min)")
    print(f"[*] Neural Voice Engine:  Microsoft Edge Neural (Prabhat)")
    print(f"[*] Multi-LLM Routing:    Gemini 3.5/3.8 Flash + Groq LLaMA")
    print(f"[*] Security & Policy:    Two-Phase Confirmation Gate Active")
    print("=" * 68)

    launch_cloudflare_tunnel(port)
    threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run(
        "web_server:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
