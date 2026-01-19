# Cardputer ADV Demo Launcher
# ============================
# This is the main entry point for the demo apps.
#
# Path Resolution:
# ----------------
# This file works in two modes:
#   1. Development (mpremote mount): Apps loaded from /remote/apps/
#   2. Standalone (deployed to flash): Apps loaded from /flash/apps/
#
# We add both paths to sys.path - Python's import system automatically
# finds modules from whichever path actually exists.
#
# App Registration:
# -----------------
# Apps are defined in APP_REGISTRY as (module_name, class_name, display_name).
# The launcher dynamically imports each module and instantiates the class.
#
# Navigation:
# -----------
# ; = Up, . = Down, Enter = Select, ESC = Exit app

import sys
import time

import M5
import machine
from M5 import Lcd, Widgets

# =============================================================================
# PATH SETUP
# =============================================================================
# Add both possible app locations to sys.path.
# When running via mpremote mount, /remote/apps exists.
# When running standalone from flash, /flash/apps exists.
# Python will import from whichever path contains the modules.

# Add /flash/apps first, then /remote/apps so /remote takes priority
for apps_path in ["/flash/apps", "/remote/apps"]:
    if apps_path not in sys.path:
        sys.path.insert(0, apps_path)

# Detect if running from remote mount or flash
import os

try:
    os.stat("/remote/main.py")
    RUN_MODE = "remote"
except OSError:
    RUN_MODE = "flash"

# =============================================================================
# HARDWARE INIT
# =============================================================================

M5.begin()
Lcd.setRotation(1)
Lcd.setBrightness(40)
Lcd.fillScreen(0x000000)
Lcd.setTextColor(0xFFFFFF, 0x000000)

# I2C keyboard for Cardputer ADV
from hardware import KeyboardI2C

i2c1 = machine.I2C(1, scl=machine.Pin(9), sda=machine.Pin(8), freq=400000)
intr_pin = machine.Pin(11, mode=machine.Pin.IN, pull=None)
kb = KeyboardI2C(i2c1, intr_pin=intr_pin, mode=KeyboardI2C.ASCII_MODE)

# =============================================================================
# APP REGISTRY
# =============================================================================
# Each entry: (module_name, class_name, display_name)
# The launcher dynamically imports module_name and gets class_name from it.

APP_REGISTRY = [
    ("hello_world", "HelloWorld", "Hello World"),
    ("notepad", "Notepad", "Notepad"),
    ("demo_anim", "AnimDemo", "Animation Demo"),
    ("demo_text", "TextDemo", "Text Demo"),
    ("demo_sound", "SoundDemo", "Sound Demo"),
    ("demo_keyboard", "KeyboardDemo", "Keyboard Demo"),
    ("demo_lcd", "LcdDemo", "LCD Demo"),
    ("demo_widgets", "WidgetsDemo", "Widgets Demo"),
    ("demo_nvs", "NvsDemo", "NVS Demo"),
]


def load_apps():
    """Dynamically import and instantiate app classes from APP_REGISTRY."""
    apps = []
    for module_name, class_name, display_name in APP_REGISTRY:
        # Force reimport for development (allows reloading after code changes)
        if module_name in sys.modules:
            del sys.modules[module_name]
        try:
            module = __import__(module_name)
            app_class = getattr(module, class_name)
            apps.append((display_name, app_class))
        except ImportError as e:
            print(f"Warning: Could not load {module_name}: {e}")
        except AttributeError as e:
            print(f"Warning: {module_name} has no class {class_name}: {e}")
    return apps


apps = load_apps()

# =============================================================================
# MENU STATE
# =============================================================================

selected = 0
scroll_offset = 0
launch_app = None

# Menu layout constants
MENU_START_Y = 22
MENU_ITEM_H = 22
VISIBLE_ITEMS = 4


# =============================================================================
# MENU DRAWING
# =============================================================================


def draw_menu():
    global scroll_offset

    # Adjust scroll to keep selection visible
    if selected < scroll_offset:
        scroll_offset = selected
    elif selected >= scroll_offset + VISIBLE_ITEMS:
        scroll_offset = selected - VISIBLE_ITEMS + 1

    Lcd.fillScreen(0x000000)
    Lcd.setFont(Widgets.FONTS.ASCII7)
    Lcd.setTextSize(2)
    Lcd.setTextColor(0xFFFFFF, 0x000000)
    Lcd.setCursor(0, 0)
    Lcd.print("Cardputer")
    # Show run mode indicator
    Lcd.setTextSize(1)
    if RUN_MODE == "remote":
        Lcd.setTextColor(0x07FF, 0x000000)  # Cyan for remote
    else:
        Lcd.setTextColor(0x07E0, 0x000000)  # Green for flash
    Lcd.setCursor(200, 5)
    Lcd.print(RUN_MODE)

    # Reset for menu items
    Lcd.setTextSize(2)
    Lcd.setTextColor(0xFFFFFF, 0x000000)

    # Draw visible menu items
    for i in range(VISIBLE_ITEMS):
        idx = scroll_offset + i
        if idx >= len(apps):
            break
        name, _ = apps[idx]
        Lcd.setCursor(10, MENU_START_Y + i * MENU_ITEM_H)
        prefix = "> " if idx == selected else "  "
        Lcd.print(f"{prefix}{name}")

    # Scroll indicators
    Lcd.setTextSize(1)
    if scroll_offset > 0:
        Lcd.setCursor(225, MENU_START_Y)
        Lcd.print("^")
    if scroll_offset + VISIBLE_ITEMS < len(apps):
        Lcd.setCursor(225, MENU_START_Y + (VISIBLE_ITEMS - 1) * MENU_ITEM_H + 10)
        Lcd.print("v")

    Lcd.setCursor(0, 125)
    Lcd.print("Enter=Select  ;/.=Nav")


# =============================================================================
# KEYBOARD HANDLER
# =============================================================================


def menu_key_handler(keyboard):
    global selected, launch_app

    while keyboard._keyevents:
        event = keyboard._keyevents.pop(0)
        key = event.keycode

        if key == 0 or key > 127:
            continue

        if key == 0x0D or key == 0x0A:  # Enter
            # Reimport module each time to pick up code changes during development
            module_name, class_name, _ = APP_REGISTRY[selected]
            if module_name in sys.modules:
                del sys.modules[module_name]
            try:
                module = __import__(module_name)
                app_class = getattr(module, class_name)
                launch_app = app_class(kb)
            except Exception as e:
                print(f"Error loading {module_name}: {e}")
        elif key == 59:  # ; = Up
            selected = (selected - 1) % len(apps)
            draw_menu()
        elif key == 46:  # . = Down
            selected = (selected + 1) % len(apps)
            draw_menu()


# =============================================================================
# MAIN LOOP
# =============================================================================

kb.set_keyevent_callback(menu_key_handler)
draw_menu()
print("Launcher ready")

while True:
    M5.update()

    # Launch app from main loop (not from callback)
    if launch_app:
        app = launch_app
        launch_app = None
        app.run()
        # App exited, restore menu
        kb.set_keyevent_callback(menu_key_handler)
        draw_menu()

    time.sleep_ms(10)
