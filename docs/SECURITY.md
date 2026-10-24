# Jarvis 4.0 - Security Architecture & Policy Specifications

This document outlines the security controls, authentication mechanisms, and execution safeguards governing communication between the Jarvis Android mobile app and the Windows companion computer.

---

## 1. Threat Model & Design Principles

An AI assistant that can manipulate operating system controls (volume, screenshots, processes, power state) poses severe risks if exposed over a network without authorization:
- **Unauthorized Network Access:** Anyone on the same Wi-Fi network could issue voice or API commands to manipulate the computer.
- **Accidental Execution:** Ambiguous LLM interpretation of voice input could unintentionally trigger destructive operations (e.g. system shutdown while editing documents).
- **Public Tunnel Exposure:** Utilizing tunnels like Cloudflare or ngrok exposes local REST endpoints to the public internet.

To mitigate these threats, Jarvis 4.0 implements **Defense in Depth**:
1. **Device Pairing & Cryptographic Token Authorization**
2. **Two-Phase Confirmation Gate for High-Impact Actions**
3. **Structured Audit Logging with Credential Redaction**
4. **Local Network & VPN Binding Preference**

---

## 2. Authentication & Device Pairing Handshake

```
┌──────────────────┐                               ┌───────────────────────────┐
│   Android Phone  │                               │    Windows PC Companion   │
└────────┬─────────┘                               └─────────────┬─────────────┘
         │                                                       │
         │  1. User reads 6-digit code on PC console (749201)   │
         │                                                       │
         │  2. POST /api/auth/pair                               │
         │     {"pairing_code": "749201", "device": "Pixel"}    │
         ├──────────────────────────────────────────────────────>│
         │                                                       │ 3. Validates code
         │                                                       │    Generates 256-bit
         │                                                       │    Bearer token
         │  4. HTTP 200 OK                                       │
         │     {"token": "jarvis_sec_K9x..."}                   │
         │<──────────────────────────────────────────────────────┤
         │                                                       │
         │  5. Encrypts and stores in AsyncStorage               │
         │                                                       │
         │  6. Subsequent protected calls:                       │
         │     Headers: Authorization: Bearer jarvis_sec_K9x...  │
         ├──────────────────────────────────────────────────────>│
```

- Local browser access originating from `127.0.0.1` / `localhost` is permitted to allow the desktop web HUD to function without friction.
- All non-local calls (including Wi-Fi devices, LAN IPs, and tunnel connections) **must present a valid Bearer token** or receive an immediate `401 Unauthorized`.

---

## 3. High-Impact Action Confirmation Gate

Operations are strictly divided into two security tiers:

### Tier 1: Safe Actions (Immediate Execution)
- Weather reports
- Google search and time/date queries
- General LLM reasoning and conversations
- Media playback (YouTube, Spotify)
- Hardware telemetry (CPU, RAM, Battery stats)
- PC volume and brightness adjustments

### Tier 2: High-Impact Operations (Mandatory Two-Phase Confirmation)
- Host computer shutdown (`system_shutdown`)
- Host computer reboot (`system_restart`)
- File modification or deletion
- Arbitrary shell executions

#### Protocol Flow:
1. When a user speaks a command containing a shutdown or reboot instruction, the backend **does not execute the command**.
2. Instead, it generates a cryptographically secure `pending_action_id` with a 45-second Time-To-Live (TTL).
3. The server responds with:
   ```json
   {
     "requires_confirmation": true,
     "pending_action_id": "act_a94f1c82",
     "action_type": "system_shutdown",
     "action_description": "Host PC Shutdown in 30 seconds",
     "reply": "Sir, this will shut down your computer. Please confirm on your mobile screen."
   }
   ```
4. The Android app intercepts this response and presents a prominent modal with **Authorize Action** and **Cancel** buttons.
5. The operation is dispatched to the operating system **only after the user explicitly presses Authorize Action**, which posts to `/api/confirm_action`.
6. If the user cancels or the 45-second timer expires, the action is purged from memory and cannot be executed.

---

## 4. Audit Logging & Redaction

The companion server logs all sensitive transactions via `sec.log_audit_event()`:
- Timestamp (ISO local time)
- Event type (`PAIR_ATTEMPT`, `PAIR_SUCCESS`, `ACTION_CONFIRMED`, `ACTION_CANCELLED`)
- Source IP address
- Action name and status

**Redaction Rule:** No tokens, passwords, private API keys, or raw voice audio blobs are ever written to stdout or log files.

---

## 5. Recommended Remote Access Configurations

When connecting your phone from outside your home Wi-Fi:
1. **Best: Tailscale / WireGuard VPN**
   - Install Tailscale on your PC and Android phone.
   - You receive an encrypted private IP (e.g. `100.x.y.z`) accessible only by your devices.
   - Enter your computer's Tailscale IP in the Android app setup screen.
2. **Alternative: Cloudflare Tunnel with Access Rules**
   - If using `cloudflared.exe`, configure Cloudflare Zero Trust to restrict access to authorized IP ranges or client certificates.
   - Never post your public tunnel URL on public forums or GitHub.
