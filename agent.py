import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from tts_helper import speak_text
from voice_to_text import speech_to_text

import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

# ---------------- LIVEKIT IMPORTS ----------------
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, JobContext
from livekit.plugins import noise_cancellation

# ---------------- TOOL IMPORTS ----------------
from tools.google_search import google_search_tool, get_current_datetime_tool
from tools.weather import weather_tool
from tools.window_ctrl import open as open_app_tool, close as close_tool, folder_file as folder_file_tool
from tools.youtube_player import play_youtube_song_tool
from tools.whatsapp import whatsapp_send_tool
from tools.radio_spotify import spotify_play_tool
from tools.instagram_dm import instagram_dm_tool
from tools.gmail_tool import gmail_send_tool
from tools.profile_face_unlock import profile_face_unlock_tool
from tools.intent_classifier import classify_intent_tool
from tools.study_mode_tool import study_mode_tool
from tools.gate_mode import gate_mode_tool
from tools.google_llm import gemini_answer_tool
from tools.groq_llm import groq_answer_tool
from tools.memory import memory_get_tool, memory_set_tool
from tools.auto_modes import auto_modes_tool
from tools.brightness import brightness_tool
from tools.file_indexer import file_indexer_tool
from tools.net_speed import net_status_tool
from tools.tool_router import tool_router_get_answer
from tools.system_control import (
    volume_control_tool,
    take_screenshot_tool,
    system_shutdown_tool,
    system_restart_tool,
    cancel_shutdown_tool,
    open_website_tool,
    get_system_info_tool,
    open_application_tool,
    close_application_tool,
)

from tools.keyboard_mouse_CTRL import (
    move_cursor_tool,
    mouse_click_tool,
    scroll_cursor_tool,
    type_text_tool,
    press_key_tool,
    swipe_gesture_tool,
    press_hotkey_tool,
    control_volume_tool
)


# --------------------------------------------------------
# STARTUP VOICE (non-blocking)
# --------------------------------------------------------
async def jarvies_startup_speak():
    try:
        await speak_text(
            "I am Jarvies, created by my boss Himanshu.",
            voice="en-IN-PrabhatNeural"
        )
    except:
        pass


# --------------------------------------------------------
# Gemini text-based reply
# --------------------------------------------------------
async def jarvies_reply(user_text: str):
    prompt = (
        "You are Jarvies created by Himanshu sir. "
        "Reply in natural Hinglish, short and smart.\n\n"
        f"User: {user_text}\nJarvies:"
    )

    response = await gemini_answer_tool(prompt)
    reply = str(response).strip()

    try:
        await speak_text(reply, voice="en-IN-PrabhatNeural")
    except:
        pass

    return reply


# --------------------------------------------------------
# MAIN JARVIES AGENT
# --------------------------------------------------------
class Jarvies(Agent):
    def __init__(self):
        super().__init__(
            instructions=(
                "You are Jarvies created by Himanshu Sir. "
                "Speak in Hinglish politely and smartly. "
                "Use tools automatically whenever needed."
            ),
            tools=[
                google_search_tool,
                get_current_datetime_tool,
                weather_tool,
                open_app_tool,
                close_tool,
                folder_file_tool,
                play_youtube_song_tool,
                whatsapp_send_tool,
                spotify_play_tool,
                instagram_dm_tool,
                gmail_send_tool,
                profile_face_unlock_tool,
                classify_intent_tool,
                study_mode_tool,
                gate_mode_tool,
                groq_answer_tool,
                gemini_answer_tool,
                tool_router_get_answer,
                net_status_tool,
                auto_modes_tool,
                brightness_tool,
                move_cursor_tool,
                mouse_click_tool,
                scroll_cursor_tool,
                type_text_tool,
                press_key_tool,
                swipe_gesture_tool,
                press_hotkey_tool,
                control_volume_tool,
                volume_control_tool,
                take_screenshot_tool,
                system_shutdown_tool,
                system_restart_tool,
                cancel_shutdown_tool,
                open_website_tool,
                get_system_info_tool,
                open_application_tool,
                close_application_tool,
                file_indexer_tool,
                memory_get_tool,
                memory_set_tool,
            ]
        )


# --------------------------------------------------------
# ENTRYPOINT — NO REALTIME GEMINI (FIX)
# --------------------------------------------------------
async def entrypoint(ctx: JobContext):

    # ❌ NO REALTIME GEMINI
    session = AgentSession(llm=None)

    await session.start(
        room=ctx.room,
        agent=Jarvies(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
            video_enabled=False
        ),
    )

    await ctx.connect()

    # Play startup voice separately
    asyncio.create_task(jarvies_startup_speak())

    # ----------------------------------------------------
    # CONSOLE MODE LOOP
    # ----------------------------------------------------
    async def console_loop():
        print("\n💻 Console mode active:")
        print("🎧 Jarvies is listening for wakeword... say 'Jarvis <command>'")

        loop = asyncio.get_event_loop()
        while True:
            text = await loop.run_in_executor(None, input)
            text = text.strip()

            if not text:
                continue

            if text.lower() in ["exit", "quit"]:
                break

            reply = await jarvies_reply(text)
            print("Jarvies:", reply)

    asyncio.create_task(console_loop())

    # ----------------------------------------------------
    # VOICE WAKEWORD + COMMAND LOOP
    # ----------------------------------------------------
    async def voice_loop():
        print("🎙 Listening...")

        while True:
            voice_text = await asyncio.get_event_loop().run_in_executor(None, speech_to_text)

            if not voice_text.strip():
                continue

            print("🎤 Heard:", voice_text)

            # Wakeword detection
            if voice_text.lower().startswith("jarvis"):
                command = voice_text[len("jarvis"):].strip()

                if not command:
                    continue

                print("🟢 Command:", command)

                # Send to agent tools
                try:
                    await session.process_text(command)
                except:
                    pass

                # Speak Gemini response
                reply = await jarvies_reply(command)
                print("Jarvies:", reply)

    asyncio.create_task(voice_loop())


# --------------------------------------------------------
# STANDALONE LOCAL CONSOLE RUNNER
# --------------------------------------------------------
async def run_standalone_console():
    await jarvies_startup_speak()
    print("\n" + "=" * 60)
    print("        🚀 JARVIES 4.0 - AI DESKTOP ASSISTANT")
    print("=" * 60)
    print(" [*] Speech Engine: Microsoft Edge Neural (Prabhat)")
    print(" [*] Mode:          Interactive Local Console")
    print(" [*] Status:        Online & Ready")
    print(" [*] Instructions:  Type anything to chat, or 'exit' to quit.")
    print("=" * 60 + "\n")

    loop = asyncio.get_event_loop()
    while True:
        try:
            text = await loop.run_in_executor(None, input, "You: ")
            text = text.strip()
            if not text:
                continue
            if text.lower() in ["exit", "quit"]:
                print("Jarvies: Alvida sir, take care!")
                break
            reply = await jarvies_reply(text)
            print(f"Jarvies: {reply}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting Jarvies.")
            break


# --------------------------------------------------------
# RUN APP
# --------------------------------------------------------
if __name__ == "__main__":
    import sys
    livekit_key = os.getenv("LIVEKIT_API_KEY", "")
    livekit_secret = os.getenv("LIVEKIT_API_SECRET", "")
    has_livekit = bool(livekit_key and livekit_secret and "your_livekit" not in livekit_key.lower())

    # If LiveKit cloud credentials are not supplied or user specified local/console
    if not has_livekit or (len(sys.argv) > 1 and sys.argv[1] in ["local", "standalone"]):
        print("\n[*] Running in Standalone Console Mode (Edge Neural TTS + Local Router)")
        asyncio.run(run_standalone_console())
    else:
        agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))

