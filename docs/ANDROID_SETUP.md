# Jarvis 4.0 - Android Mobile App Setup & Connection Guide

This guide walks you through connecting your Android phone to your local Jarvis companion assistant running on your Windows computer.

---

## 1. Prerequisites

### On Your Computer (Windows)
- Python 3.10+ (Active runtime: Python 3.14)
- Node.js 18+ (Verified: v26.3.0) & npm
- Both your computer and Android phone connected to the **same Wi-Fi network**

### On Your Phone (Android)
- Any Android phone running Android 8.0 or higher.
- Install **Expo Go** from the Google Play Store (for instant development testing), OR install the generated standalone debug APK.

---

## 2. Step-by-Step PowerShell Setup Commands

Open Windows PowerShell (Run as Administrator or normal user) in the project directory:

```powershell
# 1. Navigate to the project root
cd "e:\Project files\Jarvis\jarvies-4.0-main\jarvies-4.0-main"

# 2. Install backend dependencies (if not already installed)
python -m pip install -r requirements.txt
python -m pip install pynput spotipy groq fuzzywuzzy python-Levenshtein

# 3. Start the Jarvis Companion Backend
python web_server.py
```

When Jarvis starts, note the information displayed in the console:
```
====================================================================
      🚀 JARVIES 4.0 - AI DESKTOP ASSISTANT & MOBILE COMPANION
====================================================================
[*] Local PC Dashboard:   http://127.0.0.1:7777
[*] Android Mobile URL:   http://192.168.1.X:7777
[*] Mobile Pairing Code:  749201
[*] Neural Voice Engine:  Microsoft Edge Neural (Prabhat)
[*] Multi-LLM Routing:    Gemini 3.5/3.8 Flash + Groq LLaMA
[*] Security & Policy:    Two-Phase Confirmation Gate Active
====================================================================
```

---

## 3. Launching the Android Mobile App

Open a second PowerShell terminal:

```powershell
# 1. Navigate to the mobile app directory
cd "e:\Project files\Jarvis\jarvies-4.0-main\jarvies-4.0-main\android_app"

# 2. Install mobile app dependencies
npm.cmd install

# 3. Start Expo development server
npx.cmd expo start
```

A QR code will appear in your PowerShell console.
1. Open the **Expo Go** app on your Android phone.
2. Tap **Scan QR code** and point your camera at the console QR code.
3. The Jarvis Holographic HUD will load immediately on your phone!

---

## 4. Pairing Your Phone with Your Computer

1. On your phone, tap **Setup** (gear icon in the top right).
2. Under **Companion Computer Link**, enter your computer's URL:
   ```
   http://192.168.1.X:7777
   ```
   *(Replace with the actual Android Mobile URL displayed when starting `web_server.py`)*
3. Tap **Test Connection** — the badge should turn green and show your PC's hostname.
4. Under **Device Pairing & Authentication**, enter the **6-digit pairing code** (e.g. `749201`).
5. Tap **Pair with Jarvis Core**.
6. The phone will receive and securely store an encrypted Bearer token.
7. Tap **Back to HUD**.

---

## 5. Voice Interaction & Commands

1. Tap the **Arc Reactor** in the center of the screen.
2. Grant microphone permissions when prompted.
3. Speak your command (e.g., *"What is the weather today?"*, *"Volume up"*, *"Take a screenshot"*).
4. Watch the live waveform animate as Jarvis processes your instruction.
5. Jarvis responds in Hinglish using Microsoft Edge Neural TTS voice.
6. For sensitive commands (e.g., *"Shut down PC"*), Jarvis presents the **Security Confirmation Gate** requiring your explicit authorization before executing.
