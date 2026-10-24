# Jarvis 4.0 - Architecture Audit & Repository Inspection

**Date:** 2026-10-24  
**Project:** Jarvies 4.0 (Advanced AI Desktop Assistant & Mobile Companion)  
**Author:** AI Systems Architect & Mobile Engineer  
**Workspace Path:** `e:\Project files\Jarvis\jarvies-4.0-main\jarvies-4.0-main`

---

## 1. Executive Summary

Jarvies 4.0 is an advanced multimodal AI assistant built primarily for Windows desktop environments. It provides conversational AI using Google Gemini (`gemini-3.5-flash`, `gemini-3.8-flash`) and Groq LLaMA models, edge-based neural speech synthesis (Microsoft Edge Neural TTS), and a wide variety of hardware control, web automation, and operating system tooling.

The project currently has two primary interfaces:
1. **Desktop Web & Holographic HUD:** A FastAPI server (`web_server.py`) serving a futuristic, sci-fi cybernetic web interface (`frontend/`) with live reactive audio visualizer, Web Speech API speech-to-text, and direct REST APIs.
2. **Interactive LiveKit / Console Agent:** A conversational agent loop (`agent.py`) supporting LiveKit WebRTC agent rooms, console input, and local Whisper speech-to-text.

To transform this system into a true Android mobile application, we must maintain its AI intelligence, neural voice, and tool execution while properly decoupling desktop-bound automation from mobile client operations.

---

## 2. Directory Structure & File Inventory

```
e:\Project files\Jarvis\jarvies-4.0-main\jarvies-4.0-main
├── .env.example                # Configuration template (Gemini, Groq, OpenWeather, LiveKit)
├── .github/
│   └── workflows/
│       └── build-apk.yml       # GitHub Actions workflow for building Android APKs
├── .gitignore                  # Git exclusion rules (.env, venv, cache, binaries)
├── Jarvis_prompts.py           # System prompts, persona definitions (Arthur's Jarvis)
├── LICENSE                     # MIT License
├── README.md                   # Project documentation, feature overview, setup guides
├── agent.py                    # LiveKit + Standalone console AI agent entrypoint
├── assets/                     # Branding, Banner.png, logo.png
├── client_secret.json          # OAuth client credentials (Google API integration)
├── cloudflared.exe             # 55MB Cloudflare Tunnel binary for public HTTPS routing
├── data/
│   └── memory.json             # Persistent key-value memory store for Jarvis
├── frontend/                   # Holographic HUD Web Application
│   ├── css/style.css           # Sci-fi holographic cybernetic styles, animations
│   ├── icons/                  # PWA icons (192x192, 512x512, favicon)
│   ├── index.html              # HTML5 single-page application with Canvas visualizer
│   ├── js/app.js               # Web Speech API, Web Audio API, Canvas HUD controller
│   ├── manifest.json           # Progressive Web App manifest
│   └── sw.js                   # Service Worker for offline asset caching
├── list_models.py              # Utility to query available Google Gemini API models
├── push to github.bat          # Wrapper batch script
├── push_to_github.bat          # Automated Git staging, conflict resolution & push tool
├── requirements.txt            # Python dependencies
├── run.bat                     # Windows batch launcher (starts FastAPI web_server.py)
├── tools/                      # Tool library (28 tool modules)
│   ├── __init__.py             # Unified package exports for all tools
│   ├── answer_router.py        # Smart query routing
│   ├── app_detector.py         # Detects active foreground application
│   ├── auto_modes.py           # Auto-mode trigger logic
│   ├── brightness.py           # Screen brightness control via screen_brightness_control
│   ├── file_indexer.py         # Fuzzy file search and indexing via fuzzywuzzy
│   ├── gate_mode.py            # GATE examination study mode state
│   ├── gmail_tool.py           # Google Gmail API OAuth sender
│   ├── google_llm.py           # REST-based Gemini client with candidate model fallback
│   ├── google_search.py        # Google search and datetime tools
│   ├── groq_llm.py             # Groq Mixtral-8x7b-32768 LLM tool
│   ├── instagram_dm.py         # Instagram automation helper
│   ├── intent_classifier.py    # Regex & keyword-based intent classifier (study, coding, general)
│   ├── keyboard_mouse_CTRL.py  # PyAutoGUI mouse/keyboard/hotkey controller
│   ├── macro_recorder.py       # User action macro recording
│   ├── memory.py               # JSON-based persistent memory tool
│   ├── net_speed.py            # Ping & network latency monitor
│   ├── profile_face_unlock.py  # OpenCV & face_recognition lock/unlock tool
│   ├── radio_spotify.py        # Spotify playback and playlist search
│   ├── social_media.py         # Social link manager and browser openers
│   ├── state_manager.py        # Shared in-memory boolean flags (Study Mode, GATE Mode)
│   ├── study_mode_tool.py      # Study mode switch tool
│   ├── system_control.py       # Windows OS controls: volume (pycaw/pyautogui), screenshot, shutdown, restart
│   ├── tool_router.py          # Intent + network speed multi-LLM router
│   ├── weather.py              # OpenWeatherMap API tool
│   ├── whatsapp.py             # Web WhatsApp automation tool
│   ├── window_ctrl.py          # Windows window manager (pygetwindow, pywin32)
│   └── youtube_player.py       # YouTube music search & playback tool
├── tts_cache/                  # Ephemeral generated TTS audio WAV files
├── tts_helper.py               # Edge-TTS speech generation (PrabhatNeural) + ffplay/winsound
├── voice_to_text.py            # Local OpenAI Whisper STT model loader & recorder
└── web_server.py               # FastAPI backend with HTTP endpoints, static serving, telemetry
```

---

## 3. Technology Stack & Dependencies

### Backend & Language
- **Language:** Python 3.10 - 3.14 (Active runtime: Python 3.14.3 on Windows 64-bit)
- **Web Framework:** FastAPI 0.143.0 with Starlette and Uvicorn 0.54.0 (ASGI server)
- **Data Serialization:** Pydantic 2.13.4

### AI & Language Models
- **Google Gemini:** Direct HTTP API client in `tools/google_llm.py` via `httpx` (targeting `gemini-3.5-flash-lite`, `gemini-3.5-flash`, `gemini-3.8-flash`)
- **Groq AI:** Groq Python SDK with `mixtral-8x7b-32768` (fast inference for Study and GATE modes)
- **LiveKit Agents:** Optional real-time WebRTC room agent orchestrator

### Speech & Audio Systems
- **Speech-to-Text (Desktop Local):** `voice_to_text.py` using `openai-whisper` ("small"/"tiny" model) with `sounddevice` and `scipy.io.wavfile`
- **Speech-to-Text (Web HUD):** HTML5 Web Speech API (`webkitSpeechRecognition`) with `en-IN` / Hinglish language support
- **Text-to-Speech:** Microsoft Edge Neural TTS (`edge-tts` 7.3.1) producing realistic voice (`en-IN-PrabhatNeural`), saved to WAV files in `tts_cache/`

### Operating System & Hardware Automation (Windows-Specific)
- **UI & Input Simulation:** `PyAutoGUI` 0.9.54, `pynput`
- **Window Management:** `PyGetWindow` 0.0.9, `pywin32`
- **Display Brightness:** `screen_brightness_control` 0.27.2
- **Audio Control:** `pycaw`, `winsound`, `pyautogui` volume keys
- **Hardware Telemetry:** `psutil` (CPU%, RAM used/total, Disk usage, Battery percentage & charging state)
- **Computer Vision:** `opencv-python-headless`, `face_recognition`

---

## 4. End-to-End Execution Flow

### A. Web / Holographic HUD Pipeline (`web_server.py` + `frontend/`)
1. **User Action:** User clicks the Arc Reactor button or presses the microphone button in the web dashboard.
2. **Audio Capture & STT:** Browser `webkitSpeechRecognition` captures microphone input and outputs a text string (e.g. *"What is the weather today"* or *"volume up"*).
3. **HTTP Dispatch:** Browser sends a `POST` request to `/api/chat` with JSON body:
   ```json
   {
     "message": "...",
     "voice": "en-IN-PrabhatNeural",
     "play_on_speaker": false
   }
   ```
4. **Command Routing & Execution:**
   - **Step 4a (Hardware & Keyword Parser):** `web_server.py` checks keyword patterns:
     - Volume control (`volume up`, `volume down`, `mute`) -> `system_controller.control_volume()`
     - Screenshot -> `system_controller.take_screenshot()`
     - Brightness -> `brightness_tool()`
     - App launcher -> `webbrowser.open()` or `subprocess.Popen()`
     - Modes -> `set_study_mode()`, `set_gate_mode()`
   - **Step 4b (Intelligent LLM Fallback):** If not a hardcoded command, routes to:
     - Groq LLaMA if in GATE/Study mode
     - Google Gemini 3.5/3.8 Flash with Hinglish persona
5. **Speech Synthesis:** `edge_tts.Communicate` generates a WAV audio file in `tts_cache/web_tts_<timestamp>.wav`.
6. **Response Delivery:** Server returns:
   ```json
   {
     "reply": "Aaj mausam saaf hai sir...",
     "audio_url": "/api/audio/web_tts_171928374.wav",
     "tool_executed": "weather",
     "success": true
   }
   ```
7. **Client Presentation:** The client renders the reply in the chat log, streams the audio via `<audio>`, and triggers the Canvas audio visualizer to pulsate reactively.

---

## 5. Security & Network Posture

1. **Current Binding:** `web_server.py` binds to `0.0.0.0:7777`. This allows incoming connections from any device on the local Wi-Fi network.
2. **Current Authentication:** **None.** All endpoints (`/api/chat`, `/api/execute_tool`, `/api/system/stats`) currently execute requests without API tokens, pairing codes, or session tokens.
3. **Public Exposure Vulnerability:** `web_server.py` contains a helper `launch_cloudflare_tunnel()` which creates a public Cloudflare tunnel. Exposing unauthenticated endpoints (like `take_screenshot` or `shutdown`) to the public internet is a major security hazard.
4. **Conclusion for Mobile Architecture:** We MUST introduce:
   - An authenticated device pairing handshake (`/api/auth/pair`).
   - A cryptographically random Bearer token validated on all protected endpoints.
   - A Security Policy Engine with explicit confirmation required for high-impact actions (shutdown, restart, command execution).

---

## 6. Compatibility & Reusability Assessment

| Component | Status | Mobile Treatment |
| :--- | :--- | :--- |
| **FastAPI Backend Core** | Fully Reusable | Keep on computer as the Jarvis Companion Server. |
| **Google Gemini LLM** | Fully Reusable | Executed on backend; zero phone CPU load. |
| **Groq LLaMA LLM** | Fully Reusable | Executed on backend; zero phone CPU load. |
| **Edge Neural TTS** | Fully Reusable | Backend generates audio stream/WAV; phone plays it. |
| **System Controls (`pyautogui`, `psutil`)** | Computer-Bound | Remote execution via authenticated API; cannot run natively on Android sandbox. |
| **Web Speech API STT** | Web-Only | Implement Native Android Speech Recognition on mobile client. |
| **Holographic HUD UI** | Adaptable | Recreate as a React Native mobile UI with Arc Reactor animation, visualizer, and dark theme. |
