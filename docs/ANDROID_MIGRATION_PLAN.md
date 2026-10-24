# Jarvis 4.0 - Android Migration Plan

This document defines the technical roadmap for converting the existing Jarvis AI assistant into an Android mobile application, connecting seamlessly with the companion desktop service while preserving all AI, voice, and system automation capabilities.

---

## 1. Selected Architecture: Hybrid Companion Model

### Why Not Run Everything On-Device?
1. **Model Weights & Heavy Python Stack:** Jarvis utilizes Python 3.14 with libraries (`psutil`, `pyautogui`, `pywin32`, `pycaw`, `screen_brightness_control`) that rely directly on Windows Win32 APIs. Packing these into an Android APK is technically impossible because Android's Linux kernel and SELinux sandboxing prevent arbitrary process manipulation.
2. **API Key Security:** Embedding Google Gemini and Groq API keys directly into an APK decompiles easily, creating credential leakage.
3. **Hardware Capabilities:** A user commanding Jarvis to *"turn up the volume"* or *"shut down the computer"* expects their desktop to respond, even when commanding from their Android phone in another room.

### The Solution: React Native (Expo) Android App + Secure FastAPI Backend

```
┌────────────────────────────────────────────────────────┐
│             ANDROID MOBILE APP (android_app/)          │
│  - React Native / Expo Native Runtime                  │
│  - Arc Reactor Holographic HUD & Audio Waveform        │
│  - Native Android Speech-to-Text & Text-to-Speech      │
│  - Secure Token Storage & Automatic Reconnect          │
│  - High-Impact Action Confirmation Modal               │
│  - Deep Linking to Native Mobile Apps                  │
└───────────────────────────┬────────────────────────────┘
                            │ Authenticated REST / WSS
                            │ Header: Authorization: Bearer <TOKEN>
┌───────────────────────────▼────────────────────────────┐
│            JARVIS COMPANION BACKEND (web_server.py)    │
│  - Pairing Handshake (`/api/auth/pair`)                │
│  - Health & Telemetry (`/api/health`, `/api/system/stats`)
│  - Capability Registry (`/api/capabilities`)           │
│  - Execution Policy & Confirmation Gate                │
│  - Gemini 3.5/3.8 Flash & Groq LLaMA Engine            │
│  - Microsoft Edge Neural TTS Voice Generator           │
│  - Win32 Desktop & Hardware Automation Tooling         │
└────────────────────────────────────────────────────────┘
```

---

## 2. Security & Pairing Protocol

### Pairing Workflow
1. When Jarvis starts on the computer, it generates a 6-digit one-time Pairing Code (e.g. `749201`) and displays it in the server terminal and web HUD.
2. The Android user opens the Settings screen on their phone, inputs the Computer's IP/Host (`http://192.168.1.X:7777`), and enters the 6-digit Pairing Code.
3. The phone sends a `POST /api/auth/pair` request.
4. If the code matches, the server returns a cryptographically secure random Bearer token (`jarvis_sec_...`).
5. The Android app stores this token securely in `AsyncStorage` / Android Keystore.
6. Every subsequent request from the mobile phone includes `Authorization: Bearer <TOKEN>`.

### Safety Gate for High-Impact Actions
- **Safe Actions (Instant Execution):** Queries, weather, Google search, calculator, volume control, brightness, general chit-chat.
- **High-Impact Actions (Confirmation Required):** Shutdown, restart, file deletion, arbitrary shell commands.
  - When the user says *"Jarvis shut down the PC"*, the backend creates a `pending_action_id` with a 30-second TTL.
  - The backend responds:
    ```json
    {
      "requires_confirmation": true,
      "pending_action_id": "act_88412",
      "action_description": "Shut down the host computer in 30 seconds",
      "reply": "Sir, are you sure you want to shut down the computer?"
    }
    ```
  - The Android app displays a prominent confirmation modal with **Confirm** and **Cancel** buttons.
  - If confirmed, the app calls `POST /api/confirm_action`.

---

## 3. Mobile Client Engineering Specifications

### Framework
- **Framework:** React Native with Expo (Managed & Development builds)
- **Target OS:** Android 8.0 (API 26) through Android 15 (API 35)
- **Design Tokens:**
  - Background: Deep Obsidian / Charcoal (`#070B14`, `#0D1527`)
  - Primary Accent: Holographic Cyan (`#00F2FE`)
  - Secondary Accent: Electric Aquamarine (`#00FFD2`)
  - Warning/High-Impact: Neon Coral (`#FF4757`)
  - Typography: System / Clean Monospace & Sans-Serif
  - Animation: Spring & Loop Animated API for the pulsing Arc Reactor

### Screen Structure
1. **Main Assistant Screen:**
   - Companion Connection Status Badge (Online / Offline / Connecting)
   - Holographic Arc Reactor Button with animated listening ripple
   - Real-time Audio Waveform Visualizer
   - Live Speech Transcript bubble
   - Assistant Response card with Edge Neural voice playback
   - High-impact Action Confirmation Modal
   - Quick text input bar for silent command input
   - Cancel / Stop active request button
2. **Settings Screen:**
   - Host Computer URL configuration (e.g., `http://192.168.1.X:7777` or Cloudflare tunnel URL)
   - Pairing Code entry & Connection Test button
   - Voice selection (PrabhatNeural, SwaraNeural, etc.)
   - Audio feedback toggle (Vibrate on listen, speak responses)
   - Disconnect / Unpair button
3. **Capabilities & Tools Screen:**
   - Live list of all 28 tools fetched from `/api/capabilities`
   - Categorization by Companion PC tools vs Phone Mobile tools

---

## 4. Implementation Milestones

- [x] **Milestone 1: Repository Audit & Planning** (Completed in `docs/`)
- [ ] **Milestone 2: Backend Security & API Extension**
  - Implement `/api/health`, `/api/auth/pair`, `/api/capabilities`, `/api/confirm_action`
  - Add Token verification middleware
  - Implement two-phase confirmation protocol
  - Maintain 100% desktop web compatibility
- [ ] **Milestone 3: Android Application Construction (`android_app/`)**
  - Scaffold React Native application
  - Implement Arc Reactor UI, Waveform, and Navigation
  - Implement API service with Bearer auth, retries, and network detection
  - Implement Voice recognition & Speech audio player
  - Implement Settings & Pairing flow
- [ ] **Milestone 4: Automated Testing**
  - Backend integration tests (Pairing, Auth, Tools, Safety Gate)
  - Unit tests for API endpoints
- [ ] **Milestone 5: Build & Packaging Verification**
  - Gradle / Expo build configuration
  - Update GitHub Actions APK workflow
  - Documentation for setup, testing, and installation
