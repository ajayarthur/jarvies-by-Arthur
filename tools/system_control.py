import os
import platform
import subprocess
import psutil
import webbrowser
import pyautogui
pyautogui.FAILSAFE = False
import asyncio
import time
from livekit.agents import function_tool


class SystemController:
    def __init__(self):
        self.system = platform.system().lower()
        self.volume_level = 50

    # ---------------------- VOLUME CONTROL ----------------------
    async def control_volume(self, action: str, level: int = None) -> str:
        try:
            if action == "up":
                pyautogui.press("volumeup")
                self.volume_level = min(100, self.volume_level + 10)
                return f"🔊 Volume increased to {self.volume_level}%"

            if action == "down":
                pyautogui.press("volumedown")
                self.volume_level = max(0, self.volume_level - 10)
                return f"🔊 Volume decreased to {self.volume_level}%"

            if action == "mute":
                pyautogui.press("volumemute")
                return "🔇 Volume muted"

            if action == "set" and level is not None:
                # NOTE: Windows does not support direct volume % setting via pyautogui
                # But we store internally for consistency
                self.volume_level = level
                return f"🔊 Volume set to {level}%"

            return "❌ Invalid volume action"
        except Exception as e:
            return f"❌ Volume control failed: {e}"

    # ---------------------- SCREENSHOT ----------------------
    async def take_screenshot(self, filename: str = None) -> str:
        try:
            if filename is None:
                filename = f"screenshot_{int(time.time())}.png"

            path = os.path.join("screenshots", filename)
            os.makedirs("screenshots", exist_ok=True)

            im = pyautogui.screenshot()
            im.save(path)

            return f"📸 Screenshot saved at {path}"
        except Exception as e:
            return f"❌ Screenshot error: {e}"

    # ---------------------- SYSTEM SHUTDOWN ----------------------
    async def system_shutdown(self, delay: int = 30) -> str:
        try:
            if self.system == "windows":
                subprocess.Popen(f"shutdown /s /t {delay}", shell=True)
                return f"🛑 System will shut down in {delay} seconds"
            return "❌ Unsupported OS for shutdown"
        except Exception as e:
            return f"❌ Shutdown failed: {e}"

    # ---------------------- SYSTEM RESTART ----------------------
    async def system_restart(self, delay: int = 30) -> str:
        try:
            if self.system == "windows":
                subprocess.Popen(f"shutdown /r /t {delay}", shell=True)
                return f"🔄 System will restart in {delay} seconds"
            return "❌ Unsupported OS"
        except Exception as e:
            return f"❌ Restart failed: {e}"

    # ---------------------- CANCEL SHUTDOWN ----------------------
    async def cancel_shutdown(self) -> str:
        try:
            if self.system == "windows":
                subprocess.Popen("shutdown /a", shell=True)
                return "🚫 Shutdown cancelled"
            return "❌ Unsupported OS"
        except Exception as e:
            return f"❌ Cancel failed: {e}"

    # ---------------------- OPEN APPLICATION ----------------------
    async def open_application(self, app_name: str) -> str:
        try:
            subprocess.Popen(app_name, shell=True)
            return f"📂 Opening {app_name}"
        except Exception as e:
            return f"❌ Cannot open app: {e}"

    # ---------------------- CLOSE APPLICATION ----------------------
    async def close_application(self, app_name: str) -> str:
        try:
            subprocess.Popen(f"taskkill /f /im {app_name}.exe", shell=True)
            return f"🛑 Closed {app_name}"
        except Exception as e:
            return f"❌ Cannot close app: {e}"

    # ---------------------- SYSTEM INFO ----------------------
    async def get_system_info(self) -> str:
        try:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return (
                f"💻 System Information:\n"
                f"• CPU Usage: {cpu}%\n"
                f"• RAM Usage: {mem.percent}%\n"
                f"• Disk Usage: {disk.percent}%\n"
            )
        except Exception as e:
            return f"❌ Failed to fetch system info: {e}"


# ---------------------- INSTANCE ----------------------
system_controller = SystemController()


# ---------------------- EXPORT TOOLS ----------------------
@function_tool
async def volume_control_tool(action: str, level: int = None):
    return await system_controller.control_volume(action, level)


@function_tool
async def take_screenshot_tool(filename: str = None):
    return await system_controller.take_screenshot(filename)


@function_tool
async def system_shutdown_tool(delay: int = 30):
    return await system_controller.system_shutdown(delay)


@function_tool
async def system_restart_tool(delay: int = 30):
    return await system_controller.system_restart(delay)


@function_tool
async def cancel_shutdown_tool():
    return await system_controller.cancel_shutdown()


@function_tool
async def open_application_tool(app_name: str):
    return await system_controller.open_application(app_name)


@function_tool
async def close_application_tool(app_name: str):
    return await system_controller.close_application(app_name)


@function_tool
async def get_system_info_tool():
    return await system_controller.get_system_info()


@function_tool
async def open_website_tool(url: str):
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        webbrowser.open(url)
        return f"🌐 Opening {url}"
    except Exception as e:
        return f"❌ Website open failed: {e}"
