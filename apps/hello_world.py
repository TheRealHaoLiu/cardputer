# Hello World - App Template for Cardputer ADV
# =============================================
# This is a minimal app template showing the required structure.
# Copy this file to create new apps.
#
# Required:
# ---------
# 1. A class with __init__(self, keyboard) and run(self) methods
# 2. Register in main.py APP_REGISTRY: ("module_name", "ClassName", "Display Name")
#
# App Lifecycle:
# --------------
# 1. __init__(keyboard) - Store keyboard reference, initialize state
# 2. run() - Main app logic, return self when done
# 3. Launcher restores menu after run() returns
#
# Keyboard Handling:
# ------------------
# - Set callback with: self.kb.set_keyevent_callback(handler_func)
# - IMPORTANT: Never do blocking operations in callback!
# - Use flags in callback, check flags in main loop
# - ESC (0x1B) should exit the app
#
# Common Key Codes:
# -----------------
# ESC = 0x1B (27)
# Enter = 0x0D (13) or 0x0A (10)
# Backspace = 0x08 (8)
# Space = 0x20 (32)
# Printable ASCII = 0x20-0x7E (32-126)

import time

import M5
from M5 import Lcd, Widgets

# Screen dimensions for Cardputer ADV
SCREEN_W = 240
SCREEN_H = 135


class HelloWorld:
    """
    Minimal app template.

    To create a new app:
    1. Copy this file to apps/my_app.py
    2. Rename the class to MyApp
    3. Add to APP_REGISTRY in main.py: ("my_app", "MyApp", "My App")
    """

    def __init__(self, keyboard):
        """
        Initialize the app.

        Args:
            keyboard: KeyboardI2C instance from the launcher
        """
        self.kb = keyboard
        self.running = False

    def run(self):
        """
        Main app entry point. Called by launcher when app is selected.

        Returns:
            self - Must return self for launcher compatibility
        """
        self.running = True

        # =====================================================================
        # KEYBOARD SETUP
        # =====================================================================
        # Use flags to communicate between callback and main loop.
        # Never do blocking operations (Lcd drawing, time.sleep) in callback!

        exit_flag = False

        def on_key(keyboard):
            nonlocal exit_flag
            while keyboard._keyevents:
                event = keyboard._keyevents.pop(0)
                if event.keycode == 0x1B:  # ESC = exit
                    exit_flag = True
                # Handle other keys here...

        self.kb.set_keyevent_callback(on_key)

        # =====================================================================
        # DRAW UI
        # =====================================================================

        Lcd.fillScreen(0x0000)

        # Title
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(0x07E0, 0x0000)  # Green
        Lcd.drawCenterString("Hello World!", SCREEN_W // 2, 40)

        # Instructions
        Lcd.setFont(Widgets.FONTS.DejaVu12)
        Lcd.setTextColor(0xFFFF, 0x0000)  # White
        Lcd.drawCenterString("This is an app template", SCREEN_W // 2, 70)

        # Footer
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextColor(0x07E0, 0x0000)
        Lcd.setCursor(0, SCREEN_H - 10)
        Lcd.print("ESC=Exit")

        # =====================================================================
        # MAIN LOOP
        # =====================================================================
        # Every app needs a main loop that:
        # 1. Calls M5.update() to process events
        # 2. Checks flags set by keyboard callback
        # 3. Sleeps briefly to avoid busy-waiting

        while not exit_flag:
            M5.update()
            # Do app logic here...
            time.sleep(0.02)

        # =====================================================================
        # CLEANUP
        # =====================================================================
        # Optional: Clean up resources before returning to launcher

        self.running = False
        print("Hello World exited")
        return self
