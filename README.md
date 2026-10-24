<p align="center">
  <img src="assets/Banner.png" alt="Jarvies 4.0 Banner" width="800"/>
</p>

<p align="center">
  <b>Personal AI built by Arthur | Voice + Automation + Tools + Local TTS</b>
</p>

<p align="center">
  <img src="assets/logo.png" alt="Jarvies 4.0 Logo" width="160">
</p>

<h1 align="center">🚀 Jarvies 4.0 — Advanced AI Desktop Assistant</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Version-4.0-blue">
  <img src="https://img.shields.io/badge/Python-3.11-green">
  <img src="https://img.shields.io/badge/Platform-Windows%2011-orange">
  <img src="https://img.shields.io/badge/AI-Gemini%20%2B%20Groq-purple">
</p>

---

# 🚀 **Jarvies 4.0 — Your Personal AI Desktop Assistant (Hinglish + Automation + Voice AI)**

A next-generation AI desktop assistant designed and developed by **Arthur**.
Jarvies 4.0 combines **AI LLMs (Gemini, Groq)**, **voice automation**, **desktop control**, **social media actions**, **study/GATE modes**, and **system-level automation** — all in one powerful Python project.

---

## 🧠 **What is Jarvies 4.0?**

Jarvies 4.0 is a **fully voice-controlled intelligent assistant** that can think, talk, automate, search, study, control your PC, and execute real system commands — just like JARVIS in Iron Man (but in Hinglish 😎).

This is an upgraded version of Jarvies 3.0, with a **new architecture, tool router, better voice engine, improved Gemini/Groq integration**, and a **clean agent-based LiveKit workflow**.

---

# ✨ **Key Features**

## 🎤 **1. Voice Assistant with Wake Word**

* Always listening mode
* Say: **"Jarvis <command>"**
* Uses whisper for speech → text
* Uses Microsoft Edge Neural Voice (Prabhat) for smooth TTS

---

## ⚙️ **2. System Automation**

Jarvies can control your PC hands-free:

* Adjust **volume**
* Adjust **brightness**
* Shutdown / Restart / Cancel shutdown
* Take screenshots
* Open/Close apps
* Get system info
* Automate Windows tasks

Example:

> “Jarvis, brightness 40% kar do”
> “Jarvis, shutdown system in 30 seconds”

---

## 🖱 **3. Keyboard + Mouse Control**

* Move cursor
* Click
* Scroll
* Type text
* Press hotkeys (Ctrl+C, Ctrl+V, Win+R, etc.)
* Swipe gestures

Example:

> “Jarvis, scroll down”
> “Jarvis, press Ctrl+Shift+N”

---

## 🌐 **4. Smart Web Tools**

* Google Search
* Weather Report
* Open any website
* Open YouTube + play videos
* Open ChatGPT
* Instagram, Twitter, LinkedIn, GitHub quick open tools

Example:

> “Jarvis, LinkedIn open karo”

---

## 🎵 **5. Media / Music Tools**

* YouTube music player
* Spotify controller
* Auto-play best search result

Example:

> “Jarvis, play Lofi on YouTube”
> “Jarvis, play Arijit on Spotify”

---

## 📱 **6. WhatsApp + Instagram + Gmail Automation**

* WhatsApp messaging
* Instagram DMs
* Gmail send
* Auto confirmations for safe operations

Example:

> “Jarvis, WhatsApp par Golu ko message bhejo — bolna kal milte hain.”

---

## 🧠 **7. Multi-LLM Intelligence (Gemini + Groq)**

Jarvies uses an intelligent router:

* **Gemini 2.5 Flash** → General conversation, reasoning
* **Groq (Llama/DeepSeek)** → Study, coding, technical questions
* Smart intent classifier to choose the best model

---

## 📘 **8. Study Mode + GATE Mode**

Jarvies becomes your study partner:

### **Study Mode ON**

* Clear explanations
* 80–150 words
* Simple examples

### **GATE Mode ON**

* Formula-based answers
* Steps + short theory
* Perfect for exam practice

---

## 🧩 **9. Face Unlock System**

* Camera face recognition
* Personalized greeting

> “Welcome back Arthur sir.”

---

## 🧠 **10. Memory Engine**

Jarvies can remember small instructions:

> “Jarvis, yaad rakhna ki mera exam next Sunday hai.”

---

# 🏗 **Project Architecture**

```
Jarvies 4.0/
│
├── agent.py                # Main Agent (LiveKit + Wake Word + TTS + STT)
├── tts_helper.py           # Edge Neural TTS
├── voice_to_text.py        # Whisper speech recognition
├── Jarvis_prompts.py       # Personality + system instructions
│
├── tools/                  # All automation tools
│   ├── system_control.py
│   ├── keyboard_mouse_CTRL.py
│   ├── google_llm.py
│   ├── groq_llm.py
│   ├── weather.py
│   ├── whatsapp.py
│   ├── youtube_player.py
│   ├── instagram_dm.py
│   ├── brightness.py
│   ├── file_indexer.py
│   ├── study_mode_tool.py
│   ├── tool_router.py
│   └── ...
│
├── data/
│   ├── memory.json          # Stored user memory
│
├── tts_cache/               # Temporary voice files
├── requirements.txt
└── .env                     # API keys + config
```

---

# 🔧 **Installation Guide**

## 1️⃣ Clone the Repo

```
git clone https://github.com/yourusername/jarvies-4.0
cd jarvies-4.0
```

## 2️⃣ Create Virtual Environment

```
python -m venv jarvies_env
jarvies_env\Scripts\activate
```

## 3️⃣ Install Requirements

```
pip install -r requirements.txt
```

## 4️⃣ Setup FFmpeg (For Whisper + Audio Playback)

Download from: [https://www.gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds)
Add FFmpeg `/bin` path to system PATH.

## 5️⃣ Add Your API Keys

Edit `.env` file:

```
GOOGLE_API_KEY=
GOOGLE_SEARCH_API_KEY=
OPENWEATHER_API_KEY=
GROQ_API_KEY=
SPOTIFY_CLIENT_ID=
...
```

---

# ▶️ **Run Jarvies 4.0**

Console + Voice Mode:

```
python agent.py console
```

---

# 🎙 **Trigger Commands**

### **General Commands**

* “Jarvis what is the time?”
* “Jarvis open YouTube”
* “Jarvis scroll down”
* “Jarvis reduce volume”

### **Study Commands**

* “Jarvis, explain pipelining.”
* “Jarvis, give me TOC notes.”

### **GATE Commands**

* “Jarvis, solve this question.”
* “Jarvis, give formula for cache hit ratio.”

### **Social Media**

* “Jarvis open Instagram”
* “Jarvis open LinkedIn”

### **WhatsApp**

* “Jarvis send message to xyz”

---

# 📈 **Performance Improvements in 4.0**

* Faster TTS (Edge Neural)
* Smooth voice playback using ffplay
* More accurate Whisper STT
* Tool Router = 40% faster responses
* Cleaner AgentSession workflow
* No Gemini realtime dependency

---

# 🛣 **Roadmap — Jarvies 5.0 (Upcoming)**

* 🔥 Offline voice mode
* 🔥 Local LLM support (Phi-4 / LLama local)
* 🔥 Cross-platform (Linux/Ubuntu)
* 🔥 Custom UI dashboard
* 🔥 Knowledge retrieval system
* 🔥 Personal calendar + reminders

---
# 📱 **Android Mobile App & Companion System**

Jarvies 4.0 now includes a dedicated native **Android Mobile Application** (`android_app/`) that connects securely with your local PC assistant.

### 🌟 Mobile Features
- **Holographic Arc Reactor HUD:** Animated pulsing core with live audio waveform visualizer.
- **Microphone & Voice:** Tap-to-talk voice capture with Microsoft Edge Neural TTS audio playback.
- **Device Pairing:** Secure 6-digit one-time pairing code with 256-bit encrypted Bearer tokens.
- **Two-Phase Security Gate:** Confirmation modal prevents accidental high-impact actions (PC shutdown/restart).
- **Tool Registry:** Live capability browser categorizing PC tools vs mobile native apps (WhatsApp, Spotify, YouTube deep linking).

### 📚 Android & Architecture Documentation
- 📖 [Architecture Audit](docs/ARCHITECTURE_AUDIT.md)
- 📊 [Feature Compatibility Matrix](docs/FEATURE_COMPATIBILITY_MATRIX.md)
- 🗺️ [Android Migration Plan](docs/ANDROID_MIGRATION_PLAN.md)
- 🚀 [Android Setup & Connection Guide](docs/ANDROID_SETUP.md)
- 📦 [Android Build & APK Installation Guide](docs/ANDROID_BUILD_AND_INSTALL.md)
- 🔒 [Security Policy & Threat Model](docs/SECURITY.md)

---

# 🤝 **Contributing**

Pull requests are welcome.
For major changes, open an issue first.
---

# 🤝 **Credits**

Developed by: **Arthur**
---
Powered by: Python, FastAPI, React Native/Expo, Gemini 3.5/3.8 Flash, Groq, Whisper, Edge TTS, PyAutoGUI

---


