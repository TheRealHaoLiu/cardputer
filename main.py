"""
Cardputer ADV Demo Launcher
===========================

This is the main entry point that provides a menu to launch demo apps.
It's designed as a learning reference for MicroPython on M5Stack hardware.

CONCEPTS COVERED:
-----------------
1. Hardware Initialization - How to set up LCD, keyboard on Cardputer ADV
2. Dynamic Module Loading - Import modules by name at runtime
3. Path Management - How sys.path works for imports
4. Event-Driven Input - Keyboard callbacks and event handling
5. Menu UI Pattern - Drawing scrollable menus on small screens

HOW THIS FILE WORKS:
--------------------
1. Initialize hardware (LCD, keyboard)
2. Load app classes from APP_REGISTRY
3. Draw a scrollable menu
4. Wait for keyboard input
5. When user selects an app, instantiate and run it
6. When app exits, restore the menu

RUNNING THIS FILE:
------------------
Development (files on your computer, mounted to device):
    uv run poe run
    # or: mpremote mount . + exec "exec(open('/remote/main.py').read())"

Standalone (files copied to device flash):
    uv run poe deploy
    # Device runs main.py on boot

KEYBOARD CONTROLS:
------------------
- ; (semicolon) = Navigate up
- . (period) = Navigate down
- Enter = Select/launch app
- ESC = Exit current app (handled by each app)

WHY THESE KEYS?
---------------
The Cardputer has a compact keyboard. Arrow keys require FN modifier which
is awkward for quick navigation. ; and . are on the home row and easy to hit.
"""

# =============================================================================
# IMPORTS
# =============================================================================
# Standard library imports first, then third-party/hardware imports.
# This is Python convention (PEP 8) for code organization.

import sys  # For sys.path manipulation (where Python looks for modules)
import time  # For sleep/delays

import M5  # M5Stack hardware abstraction layer
import machine  # MicroPython hardware access (I2C, GPIO pins, etc.)
from M5 import Lcd, Widgets  # LCD drawing and widget fonts

# =============================================================================
# PATH SETUP - Where Python Looks for Modules
# =============================================================================
# When you write `import my_module`, Python searches directories in sys.path.
# By default, MicroPython only looks in /flash/lib and built-in modules.
#
# We need to add our apps directory to sys.path so we can import them.
#
# TWO MODES OF OPERATION:
# -----------------------
# 1. Development Mode (mpremote mount):
#    - Your local files appear at /remote/ on the device
#    - Apps are at /remote/apps/
#    - Edit locally, run remotely - no copying needed!
#
# 2. Standalone Mode (deployed to flash):
#    - Files copied to /flash/ on the device
#    - Apps are at /flash/apps/
#    - Device runs independently, no computer needed
#
# We add BOTH paths. Python will find modules from whichever exists.
# /remote/apps is added LAST so it takes priority (first match wins in Python).

for apps_path in ["/flash/apps", "/remote/apps"]:
    if apps_path not in sys.path:
        sys.path.insert(0, apps_path)  # insert(0, ...) = add to front of list

# Detect which mode we're running in (for display purposes)
import os  # File system operations

try:
    # os.stat() gets file info. If file doesn't exist, raises OSError.
    os.stat("/remote/main.py")
    RUN_MODE = "remote"  # Running from mounted directory
except OSError:
    RUN_MODE = "flash"  # Running from device flash

# =============================================================================
# HARDWARE INITIALIZATION
# =============================================================================
# M5Stack devices need explicit initialization before using hardware.
# M5.begin() sets up the display, speaker, and other peripherals.

M5.begin()  # Initialize M5Stack hardware

# LCD SETUP
# ---------
# The Cardputer's LCD is 240x135 pixels.
# setRotation(1) = landscape mode (wider than tall)
# Rotation values: 0=portrait, 1=landscape, 2=portrait flipped, 3=landscape flipped

Lcd.setRotation(1)  # Landscape orientation
Lcd.setBrightness(40)  # 0-255, lower = dimmer = less battery drain
Lcd.fillScreen(0x000000)  # Clear to black (RGB565 format, explained below)
Lcd.setTextColor(0xFFFFFF, 0x000000)  # White text on black background

# COLOR FORMAT: RGB565
# --------------------
# Colors are 16-bit values: 5 bits red, 6 bits green, 5 bits blue.
# Common colors:
#   0x0000 = Black      0xFFFF = White
#   0xF800 = Red        0x07E0 = Green      0x001F = Blue
#   0xFFE0 = Yellow     0xF81F = Magenta    0x07FF = Cyan
#
# To convert RGB (0-255 each) to RGB565:
#   color = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)

# KEYBOARD SETUP
# --------------
# The Cardputer ADV uses an I2C keyboard controller (TCA8418 chip).
# This is DIFFERENT from the original Cardputer which uses GPIO matrix.
# Make sure you have the correct firmware for your hardware!
#
# I2C = Inter-Integrated Circuit, a two-wire communication protocol.
# - SCL (Serial Clock) = timing signal, pin 9
# - SDA (Serial Data) = data signal, pin 8
# - Interrupt pin = notifies when key is pressed, pin 11

from hardware import KeyboardI2C  # M5Stack's keyboard driver

# Create I2C bus instance
# - Bus 1 (ESP32-S3 has two I2C buses, we use bus 1)
# - SCL on GPIO 9, SDA on GPIO 8
# - 400kHz is "fast mode" I2C speed
i2c1 = machine.I2C(1, scl=machine.Pin(9), sda=machine.Pin(8), freq=400000)

# Interrupt pin - keyboard sets this LOW when there's a key event
# - mode=IN = we're reading this pin, not writing
# - pull=None = no internal pull-up/down resistor (external on board)
intr_pin = machine.Pin(11, mode=machine.Pin.IN, pull=None)

# Create keyboard instance
# - ASCII_MODE = convert key matrix positions to ASCII codes
# - The alternative is RAW_MODE which gives matrix row/column
kb = KeyboardI2C(i2c1, intr_pin=intr_pin, mode=KeyboardI2C.ASCII_MODE)

# =============================================================================
# APP REGISTRY - What Apps Are Available
# =============================================================================
# Each entry: (module_name, class_name, display_name)
#
# - module_name: The .py file name without extension (e.g., "hello_world")
# - class_name: The class inside that file to instantiate (e.g., "HelloWorld")
# - display_name: What to show in the menu (e.g., "Hello World")
#
# The launcher dynamically imports each module and gets the class from it.
# This allows adding new apps by just editing this list!
#
# HOW DYNAMIC IMPORT WORKS:
# -------------------------
# module = __import__("hello_world")  # Same as: import hello_world
# cls = getattr(module, "HelloWorld")  # Same as: module.HelloWorld
# app = cls(kb)                        # Same as: HelloWorld(kb)
# app.run()                            # Run the app

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
    """
    Dynamically import and instantiate app classes from APP_REGISTRY.

    Returns a list of (display_name, app_class) tuples.

    WHY DYNAMIC LOADING?
    --------------------
    1. Apps are separate files - easy to add/remove
    2. Errors in one app don't break the launcher
    3. Can reload apps during development without restarting

    THE del sys.modules TRICK:
    --------------------------
    Python caches imported modules in sys.modules dictionary.
    Deleting a module from this cache forces Python to re-read the file
    on next import. This is useful during development - edit your app,
    and changes take effect on next launch without rebooting the device.
    """
    apps = []
    for module_name, class_name, display_name in APP_REGISTRY:
        # Force reimport for development (allows reloading after code changes)
        if module_name in sys.modules:
            del sys.modules[module_name]
        try:
            # __import__ is the function behind the `import` statement
            module = __import__(module_name)
            # getattr gets an attribute by name - here, the class
            app_class = getattr(module, class_name)
            apps.append((display_name, app_class))
        except ImportError as e:
            # Module file not found or has syntax errors
            print(f"Warning: Could not load {module_name}: {e}")
        except AttributeError as e:
            # Module loaded but class not found in it
            print(f"Warning: {module_name} has no class {class_name}: {e}")
    return apps


# Load all apps at startup
apps = load_apps()

# =============================================================================
# MENU STATE - Variables That Track Current Menu State
# =============================================================================
# These are module-level (global) variables that the menu functions modify.
# In a larger app you might use a class, but globals work fine for simple menus.

selected = 0  # Index of currently highlighted menu item
scroll_offset = 0  # First visible item index (for scrolling)
launch_app = None  # Set to an app instance when user selects one

# MENU LAYOUT CONSTANTS
# ---------------------
# These define the visual layout of the menu.
# Changing these adjusts how many items are visible and where they appear.

MENU_START_Y = 22  # Y position where menu items start (below title)
MENU_ITEM_H = 22  # Height of each menu item in pixels
VISIBLE_ITEMS = 4  # How many items fit on screen at once


# =============================================================================
# MENU DRAWING
# =============================================================================


def draw_menu():
    """
    Draw the menu on screen.

    SCROLLING LOGIC:
    ----------------
    When you have more items than fit on screen, you need scrolling.
    scroll_offset tracks which item is at the top of the visible area.

    Example with 9 items, 4 visible:
    - scroll_offset=0: items 0,1,2,3 visible
    - scroll_offset=3: items 3,4,5,6 visible
    - scroll_offset=5: items 5,6,7,8 visible

    We adjust scroll_offset to keep the selected item visible:
    - If selected < scroll_offset: scroll up
    - If selected >= scroll_offset + VISIBLE_ITEMS: scroll down
    """
    global scroll_offset

    # Keep selection visible by adjusting scroll
    if selected < scroll_offset:
        scroll_offset = selected
    elif selected >= scroll_offset + VISIBLE_ITEMS:
        scroll_offset = selected - VISIBLE_ITEMS + 1

    # Clear screen and draw title
    Lcd.fillScreen(0x000000)
    Lcd.setFont(Widgets.FONTS.ASCII7)  # Monospace font, 6x9 pixels base size
    Lcd.setTextSize(2)  # 2x scale = 12x18 pixels per character
    Lcd.setTextColor(0xFFFFFF, 0x000000)
    Lcd.setCursor(0, 0)
    Lcd.print("Cardputer")

    # Show run mode indicator (remote=cyan, flash=green)
    # This helps you know if you're running mounted files or deployed files
    Lcd.setTextSize(1)
    if RUN_MODE == "remote":
        Lcd.setTextColor(0x07FF, 0x000000)  # Cyan for remote/development
    else:
        Lcd.setTextColor(0x07E0, 0x000000)  # Green for flash/standalone
    Lcd.setCursor(200, 5)
    Lcd.print(RUN_MODE)

    # Reset text settings for menu items
    Lcd.setTextSize(2)
    Lcd.setTextColor(0xFFFFFF, 0x000000)

    # Draw visible menu items
    for i in range(VISIBLE_ITEMS):
        idx = scroll_offset + i  # Actual index in apps list
        if idx >= len(apps):
            break  # No more items to draw
        name, _ = apps[idx]
        Lcd.setCursor(10, MENU_START_Y + i * MENU_ITEM_H)
        # Add ">" prefix to selected item for visual indicator
        prefix = "> " if idx == selected else "  "
        Lcd.print(f"{prefix}{name}")

    # Draw scroll indicators if there are items above/below visible area
    Lcd.setTextSize(1)
    if scroll_offset > 0:
        Lcd.setCursor(225, MENU_START_Y)
        Lcd.print("^")  # Items above
    if scroll_offset + VISIBLE_ITEMS < len(apps):
        Lcd.setCursor(225, MENU_START_Y + (VISIBLE_ITEMS - 1) * MENU_ITEM_H + 10)
        Lcd.print("v")  # Items below

    # Draw key hint at bottom
    Lcd.setCursor(0, 125)
    Lcd.print("Enter=Select  ;/.=Nav")


# =============================================================================
# KEYBOARD HANDLER
# =============================================================================


def menu_key_handler(keyboard):
    """
    Handle keyboard events for menu navigation.

    CALLBACK-BASED INPUT:
    ---------------------
    Instead of polling the keyboard in a loop, we register this function
    as a callback. The keyboard driver calls it whenever a key is pressed.

    keyboard._keyevents is a list of pending key events.
    Each event has:
    - keycode: ASCII code of the key (or special code for arrows, etc.)
    - state: True=pressed, False=released
    - row, col: Matrix position (for raw mode)
    - modifier_mask: Which modifier keys were held (Ctrl, Shift, etc.)

    IMPORTANT: Never do slow operations in callbacks!
    The callback runs in an interrupt context. Long operations here
    can cause timing issues. Instead, set flags and handle in main loop.

    KEY CODES:
    ----------
    - 0x0D (13) or 0x0A (10) = Enter
    - 0x1B (27) = Escape
    - 59 = semicolon (;) - we use this for "up"
    - 46 = period (.) - we use this for "down"
    """
    global selected, launch_app

    # Process all pending key events
    while keyboard._keyevents:
        event = keyboard._keyevents.pop(0)  # Get and remove first event
        key = event.keycode

        # Skip invalid/modifier-only events
        if key == 0 or key > 127:
            continue

        if key == 0x0D or key == 0x0A:  # Enter key
            # User selected an app - load it
            # We reload the module here to pick up any code changes
            module_name, class_name, _ = APP_REGISTRY[selected]
            if module_name in sys.modules:
                del sys.modules[module_name]  # Force reimport
            try:
                module = __import__(module_name)
                app_class = getattr(module, class_name)
                # Create app instance, passing keyboard so app can use it
                launch_app = app_class(kb)
            except Exception as e:
                print(f"Error loading {module_name}: {e}")

        elif key == 59:  # Semicolon = Up
            # Move selection up, wrap around to bottom if at top
            selected = (selected - 1) % len(apps)
            draw_menu()

        elif key == 46:  # Period = Down
            # Move selection down, wrap around to top if at bottom
            selected = (selected + 1) % len(apps)
            draw_menu()


# =============================================================================
# MAIN LOOP
# =============================================================================
# This is where the program spends most of its time.
# The pattern is:
# 1. Register keyboard callback
# 2. Draw initial UI
# 3. Loop forever, calling M5.update() to process events
# 4. Check for actions triggered by callbacks (like launch_app)

# Register our keyboard handler
kb.set_keyevent_callback(menu_key_handler)

# Draw the initial menu
draw_menu()
print("Launcher ready")

# Main event loop
while True:
    # M5.update() is REQUIRED - it processes hardware events
    # This triggers keyboard callbacks, updates the screen, etc.
    M5.update()

    # Check if user selected an app to launch
    if launch_app:
        app = launch_app
        launch_app = None  # Clear so we don't re-launch

        # Run the app - this blocks until app's run() returns
        app.run()

        # App exited - restore menu
        # Re-register our keyboard handler (app may have changed it)
        kb.set_keyevent_callback(menu_key_handler)
        draw_menu()

    # Small delay to prevent busy-waiting
    # 10ms = 100 updates per second, plenty responsive
    time.sleep_ms(10)
