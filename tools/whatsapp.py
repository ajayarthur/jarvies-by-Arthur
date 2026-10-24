from livekit.agents import function_tool
import pyautogui
import time
import subprocess
import os

@function_tool
async def whatsapp_send_tool(name: str, message: str):
    """
    Opens WhatsApp Desktop → searches contact → types → sends message.
    """

    try:
        # 1. Open WhatsApp Desktop
        subprocess.Popen("whatsapp.exe", shell=True)
        time.sleep(3)

        # 2. Search box click (top left)
        pyautogui.click(150, 120)
        time.sleep(1)

        # 3. Type contact name
        pyautogui.write(name, interval=0.1)
        time.sleep(2)

        # 4. Press Enter to open chat
        pyautogui.press("enter")
        time.sleep(1)

        # 5. Type message
        pyautogui.write(message, interval=0.05)

        # 6. Send message
        pyautogui.press("enter")

        return f"💬 Message sent to {name}"

    except Exception as e:
        return f"❌ WhatsApp automation failed: {e}"
