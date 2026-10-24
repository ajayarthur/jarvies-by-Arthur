import os
import subprocess
import asyncio
import logging
from fuzzywuzzy import process

try:
    import pygetwindow as gw
except:
    gw = None

try:
    import win32gui
    import win32con
except:
    win32gui = None
    win32con = None

from livekit.agents import function_tool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------------------- FOCUS WINDOW ----------------------
async def focus_window(keyword: str) -> bool:
    if not gw:
        return False

    await asyncio.sleep(1)

    keyword = keyword.lower().strip()

    for w in gw.getAllWindows():
        if keyword in w.title.lower():
            if w.isMinimized:
                w.restore()
            w.activate()
            return True

    return False


# ---------------------- OPEN APP ----------------------
@function_tool
async def open(app_name: str) -> str:
    """
    Opens an application using Windows shell.
    """
    try:
        subprocess.Popen(f"start \"\" \"{app_name}\"", shell=True)

        ok = await focus_window(app_name)
        if ok:
            return f"🚀 '{app_name}' opened and focused."
        else:
            return f"🚀 '{app_name}' opened (focus failed)."
    except Exception as e:
        return f"❌ Failed to open '{app_name}': {e}"


# ---------------------- CLOSE WINDOW ----------------------
@function_tool
async def close(title_keyword: str) -> str:
    """
    Close a window matching title keyword.
    """
    if not win32gui:
        return "❌ Win32GUI not installed."

    def _enum(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title_keyword.lower() in title.lower():
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

    win32gui.EnumWindows(_enum, None)
    return f"🛑 Close signal sent to '{title_keyword}'"


# ---------------------- FILE/FOLDER OPEN ----------------------
@function_tool
async def folder_file(path: str) -> str:
    """
    Opens a file or folder by exact path.
    """
    path = path.strip()

    if not os.path.exists(path):
        return "❌ Path not found."

    try:
        os.startfile(path)
        return f"📂 Opened: {path}"
    except Exception as e:
        return f"❌ Cannot open: {e}"
