# Jarvis 4.0 - Feature Compatibility Matrix

This document provides a comprehensive classification of every tool, capability, and subsystem in the Jarvis codebase, outlining how each function is preserved, adapted, or executed for the Android mobile application.

---

## Classification Categories

1. **Reusable without changes (RWC):** Runs identically on backend or client with zero code modifications.
2. **Reusable with an adapter (RWA):** Functionality is preserved, but requires an API bridge, serialization layer, or parameter normalization.
3. **Requires a backend (RAB):** Heavy AI, API keys, or machine learning model that must execute on the companion server.
4. **Requires an Android-native implementation (ANI):** Replaces browser or desktop APIs with Android-native OS capabilities.
5. **Not possible on Android without companion computer (NPC):** Low-level desktop operations (mouse clicks, PC window management) that can only be invoked on the computer companion via remote API.

---

## Detailed Capability Matrix

| Feature / Tool Name | Primary Source File | Classification | Execution Environment | Implementation & Safety Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Gemini LLM Reasoning** | `tools/google_llm.py` | **Requires a backend** | Companion Backend | REST API client executes on server; API keys stay secure. |
| **Groq LLaMA / Mixtral** | `tools/groq_llm.py` | **Requires a backend** | Companion Backend | Fast study inference executes on server without phone battery drain. |
| **Edge Neural TTS Voice** | `tts_helper.py` | **Requires a backend** | Companion Backend + Phone Audio | Backend generates neural WAV; phone streams/plays via native audio player. |
| **Android Speech Recognition** | `voice_to_text.py` | **Requires an Android-native implementation** | Android Phone | Native Android `SpeechRecognizer` / `@react-native-voice/voice` handles mic capture on phone. |
| **Fallback Whisper STT** | `voice_to_text.py` | **Requires a backend** | Companion Backend | Used for server-side audio transcription if phone STT is offline. |
| **OpenWeatherMap Tool** | `tools/weather.py` | **Requires a backend** | Companion Backend | Fetches live weather conditions via server using OpenWeather API. |
| **Google Search Tool** | `tools/google_search.py` | **Requires a backend** | Companion Backend | Web query scraping executes on companion server. |
| **Current DateTime Tool** | `tools/google_search.py` | **Reusable without changes** | Backend / Phone | Formats current time and date in ISO and localized human format. |
| **Persistent Memory** | `tools/memory.py` | **Requires a backend** | Companion Backend | Stored in `data/memory.json` on the server; accessible from both PC and phone. |
| **Study Mode & GATE Mode** | `tools/state_manager.py` | **Reusable with an adapter** | Backend State | State toggle via `/api/execute_tool` or `/api/chat`. |
| **Intent Classifier** | `tools/intent_classifier.py`| **Reusable without changes** | Companion Backend | Keyword pattern matcher routes queries automatically. |
| **Network Speed Monitor** | `tools/net_speed.py` | **Reusable with an adapter** | Companion Backend + Android NetInfo | Server reports companion ping; Android app monitors local Wi-Fi. |
| **System Screenshot** | `tools/system_control.py` | **Not possible on Android without companion computer** | Companion Computer | Captures Windows desktop screen; returned to mobile client as base64 image. |
| **PC Volume Control** | `tools/system_control.py` | **Not possible on Android without companion computer** | Companion Computer | Adjusts master volume of the host PC via PyAutoGUI/pycaw. |
| **PC Brightness Control** | `tools/brightness.py` | **Not possible on Android without companion computer** | Companion Computer | Adjusts monitor brightness of host PC via `screen_brightness_control`. |
| **PC Shutdown / Restart** | `tools/system_control.py` | **Not possible on Android without companion computer** | Companion Computer | **HIGH IMPACT:** Requires explicit mobile user confirmation before dispatching `shutdown /s`. |
| **Open Application on PC** | `tools/system_control.py` | **Not possible on Android without companion computer** | Companion Computer | Launches desktop apps (e.g. `calc.exe`, `notepad.exe`) on PC. |
| **Mobile App Deep Links** | `frontend/js/app.js` | **Requires an Android-native implementation** | Android Phone | Opens WhatsApp, YouTube, Spotify natively on Android using Android Intents (`android.intent.action.VIEW`). |
| **Keyboard & Mouse Control**| `tools/keyboard_mouse_CTRL.py`| **Not possible on Android without companion computer** | Companion Computer | PyAutoGUI cursor moves, typing, and clicks apply to the Windows desktop. |
| **Window Management** | `tools/window_ctrl.py` | **Not possible on Android without companion computer** | Companion Computer | Minimizes, maximizes, and restores Windows apps via `pygetwindow`. |
| **Gmail Sender Tool** | `tools/gmail_tool.py` | **Requires a backend** | Companion Backend | OAuth 2.0 authorized dispatch from server credentials. |
| **Spotify Control Tool** | `tools/radio_spotify.py` | **Reusable with an adapter** | Companion Backend + Mobile App | Opens Spotify Web/Client or triggers playback via Spotify API. |
| **Face Unlock System** | `tools/profile_face_unlock.py`| **Not possible on Android without companion computer** | Companion Computer | OpenCV camera stream unlocks Windows desktop session. |
| **File Indexer Search** | `tools/file_indexer.py` | **Not possible on Android without companion computer** | Companion Computer | Fuzzy search finds and launches files on the companion PC. |
| **Holographic Arc Reactor HUD**| `frontend/` | **Requires an Android-native implementation** | Android Phone | Recreated with React Native Animated API for mobile screens. |
| **Device Pairing & Auth** | *NEW API* | **Reusable with an adapter** | Backend + Phone | PIN-based pairing handshake with cryptographic Bearer token validation. |
| **Confirmation Safety Gate** | *NEW API* | **Requires an Android-native implementation** | Phone + Backend | Two-phase commit protocol prevents unauthorized or accidental destructive actions. |

---

## Architectural Decision Summary

1. **Heavy AI and Desktop Automation Stay on the Computer:** The companion server provides the processing power, API keys, and desktop hooks.
2. **Mobile Client Acts as the Remote HUD & Controller:** The Android phone captures voice, handles local device capabilities (opening mobile apps, vibrating, rendering the UI), and securely commands the companion assistant.
3. **No Compromise on Security:** Dangerous operations (PC shutdown, file modifications) require two-factor confirmation on the phone screen.
