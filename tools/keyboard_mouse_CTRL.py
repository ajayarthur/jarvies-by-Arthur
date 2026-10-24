import os
import asyncio
import time
import pyautogui
from datetime import datetime
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
from livekit.agents import function_tool

# Read activation token
ACTIVATION_TOKEN = os.getenv("ACTIVATION_TOKEN", "my_secret_token")


# ---------------------------------------
# SAFE CONTROLLER CLASS
# ---------------------------------------
class SafeController:
    def __init__(self):
        self.active = False
        self.activation_time = None
        self.keyboard = KeyboardController()
        self.mouse = MouseController()

    def activate(self, token=None):
        if token != ACTIVATION_TOKEN:
            return "❌ Invalid activation token."
        self.active = True
        self.activation_time = time.time()
        return "✔ Controller activated"

    def deactivate(self):
        self.active = False
        return "✔ Controller deactivated"

    def is_active(self):
        # Auto deactivate after 6 seconds
        if self.active and (time.time() - self.activation_time > 6):
            self.active = False
        return self.active


controller = SafeController()


# ---------------------------------------
# HELPER for temporary activation
# ---------------------------------------
async def temp_activate(fn, *args, **kwargs):
    controller.activate(ACTIVATION_TOKEN)
    result = await fn(*args, **kwargs)
    await asyncio.sleep(1)
    controller.deactivate()
    return result


# ---------------------------------------
# MOUSE MOVE
# ---------------------------------------
@function_tool
async def move_cursor_tool(direction: str, distance: int = 100) -> str:
    if not controller.is_active():
        controller.activate(ACTIVATION_TOKEN)

    x, y = controller.mouse.position

    if direction == "up":
        controller.mouse.position = (x, y - distance)
    elif direction == "down":
        controller.mouse.position = (x, y + distance)
    elif direction == "left":
        controller.mouse.position = (x - distance, y)
    elif direction == "right":
        controller.mouse.position = (x + distance, y)
    else:
        return "❌ Invalid direction"

    await asyncio.sleep(0.2)
    return f"🖱️ Mouse moved {direction}"


# ---------------------------------------
# MOUSE CLICK
# ---------------------------------------
@function_tool
async def mouse_click_tool(button: str = "left") -> str:
    if not controller.is_active():
        controller.activate(ACTIVATION_TOKEN)

    if button == "left":
        controller.mouse.click(Button.left, 1)
    elif button == "right":
        controller.mouse.click(Button.right, 1)
    elif button == "double":
        controller.mouse.click(Button.left, 2)
    else:
        return "❌ Invalid button"

    await asyncio.sleep(0.2)
    return f"🖱️ {button.capitalize()} click performed"


# ---------------------------------------
# SCROLL
# ---------------------------------------
@function_tool
async def scroll_cursor_tool(direction: str, amount: int = 10) -> str:
    if not controller.is_active():
        controller.activate(ACTIVATION_TOKEN)

    if direction == "up":
        controller.mouse.scroll(0, amount)
    elif direction == "down":
        controller.mouse.scroll(0, -amount)
    else:
        return "❌ Invalid scroll direction"

    await asyncio.sleep(0.2)
    return f"🖱️ Scrolled {direction}"


# ---------------------------------------
# TYPE TEXT
# ---------------------------------------
@function_tool
async def type_text_tool(text: str) -> str:
    if not controller.is_active():
        controller.activate(ACTIVATION_TOKEN)

    for c in text:
        controller.keyboard.press(c)
        controller.keyboard.release(c)
        await asyncio.sleep(0.04)

    return f"⌨️ Typed: {text}"


# ---------------------------------------
# PRESS SINGLE KEY
# ---------------------------------------
@function_tool
async def press_key_tool(key: str) -> str:
    if not controller.is_active():
        controller.activate(ACTIVATION_TOKEN)

    try:
        controller.keyboard.press(key)
        controller.keyboard.release(key)
        return f"⌨️ Key pressed: {key}"
    except:
        return f"❌ Invalid key: {key}"


# ---------------------------------------
# PRESS HOTKEYS
# ---------------------------------------
@function_tool
async def press_hotkey_tool(keys: list) -> str:
    if not controller.is_active():
        controller.activate(ACTIVATION_TOKEN)

    # Press all keys
    for k in keys:
        controller.keyboard.press(k)

    # Release all in reverse
    for k in reversed(keys):
        controller.keyboard.release(k)

    return f"⌨️ Hotkey pressed: {' + '.join(keys)}"


# ---------------------------------------
# CONTROL VOLUME
# ---------------------------------------
@function_tool
async def control_volume_tool(action: str) -> str:
    if action == "up":
        pyautogui.press("volumeup")
    elif action == "down":
        pyautogui.press("volumedown")
    elif action == "mute":
        pyautogui.press("volumemute")
    else:
        return "❌ Invalid volume action"

    return f"🔊 Volume {action}"


# ---------------------------------------
# SWIPE GESTURE
# ---------------------------------------
@function_tool
async def swipe_gesture_tool(direction: str) -> str:
    screen_width, screen_height = pyautogui.size()
    x, y = screen_width // 2, screen_height // 2

    if direction == "left":
        pyautogui.moveTo(x+200, y)
        pyautogui.dragTo(x-200, y, duration=0.3)
    elif direction == "right":
        pyautogui.moveTo(x-200, y)
        pyautogui.dragTo(x+200, y, duration=0.3)
    elif direction == "up":
        pyautogui.moveTo(x, y+200)
        pyautogui.dragTo(x, y-200, duration=0.3)
    elif direction == "down":
        pyautogui.moveTo(x, y-200)
        pyautogui.dragTo(x, y+200, duration=0.3)
    else:
        return "❌ Invalid swipe direction"

    return f"🖱️ Swipe gesture: {direction}"
