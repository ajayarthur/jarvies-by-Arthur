# tools/app_detector.py
import os, shutil
from pathlib import Path
from livekit.agents import function_tool

COMMON_EXECUTABLES = {
    "chrome": ["chrome.exe", "msedge.exe"],
    "vscode": ["Code.exe", "code.exe"],
    "vlc": ["vlc.exe"],
    "postman": ["Postman.exe"]
}

def find_executable(exec_name):
    # Try PATH
    p = shutil.which(exec_name)
    if p:
        return p
    # try program files
    for base in [os.environ.get("PROGRAMFILES"), os.environ.get("PROGRAMFILES(X86)"), os.environ.get("LOCALAPPDATA")]:
        if not base: continue
        for root, _, files in os.walk(base):
            if exec_name in files:
                return os.path.join(root, exec_name)
    return None

@function_tool
async def detect_app_path(app_key: str) -> str:
    app_key = app_key.lower()
    candidates = COMMON_EXECUTABLES.get(app_key, [app_key + ".exe"])
    for c in candidates:
        p = find_executable(c)
        if p:
            return p
    return ""
