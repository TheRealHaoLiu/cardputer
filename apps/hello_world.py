"""
Hello World - AppBase Template
==============================

Minimal app template demonstrating the AppBase lifecycle.
Use this as a starting point for new apps.

HOW APPS WORK:
--------------
Apps inherit from AppBase and override lifecycle methods.
The framework calls these methods at the right times:

1. on_view()  - Called when app starts. Draw your UI here.
2. on_run()   - Async background task. Runs continuously while app is active.
3. on_exit()  - Called when app stops. Clean up resources here.

KEYBOARD INPUT:
---------------
To handle keyboard input, add this method to your app:

    async def _kb_event_handler(self, event, fw):
        key = event.key  # The key code
        # Handle your keys here...
        # DON'T set event.status = True for ESC, or you can't exit!

ESC key is handled by the framework - it returns to launcher automatically.

RUNNING THIS APP:
-----------------
This app is registered in main.py. The launcher shows it in the menu.
Select it and press Enter to launch.
"""

import asyncio

# =============================================================================
# PATH SETUP FOR IMPORTS
# =============================================================================
# When running as an app, we need to ensure lib/ is in the import path.
# This allows us to import from lib.app_base even when the app is
# loaded dynamically by the framework.
import sys

# =============================================================================
# IMPORTS
# =============================================================================
# M5 module provides access to LCD display and hardware
# Widgets provides fonts for text rendering
from M5 import Lcd, Widgets

# Path setup for imports (need parent of lib/ for "from lib.x" imports)
for lib_path in ["/flash", "/remote"]:
    if lib_path not in sys.path:
        sys.path.insert(0, lib_path)

from lib.app_base import AppBase

# =============================================================================
# APP CLASS
# =============================================================================


class HelloWorld(AppBase):
    """
    Minimal hello world app template.

    This demonstrates the simplest possible app structure.
    Copy this file as a starting point for new apps.
    """

    def __init__(self):
        """
        Initialize the app.

        Always call super().__init__() first!
        Set self.name to what should appear in the launcher menu.
        """
        super().__init__()
        self.name = "Hello World"

    def on_view(self):
        """
        Draw the app's UI.

        Called once when the app starts (after on_launch, before on_run).
        This is where you set up the initial display.

        LCD BASICS:
        -----------
        - Lcd.fillScreen(color) - Clear screen with a color
        - Lcd.setFont(font) - Set the font (ASCII7 is a good default)
        - Lcd.setTextSize(n) - Scale text (1=normal, 2=double, etc.)
        - Lcd.setTextColor(fg, bg) - Set foreground and background colors
        - Lcd.setCursor(x, y) - Position for next print
        - Lcd.print(text) - Draw text at cursor position

        COLORS:
        -------
        Use Lcd.COLOR.* constants: BLACK, WHITE, RED, GREEN, BLUE,
        YELLOW, CYAN, MAGENTA, ORANGE, etc.
        """
        # Clear the screen to black
        Lcd.fillScreen(Lcd.COLOR.BLACK)

        # Set up text rendering
        Lcd.setFont(Widgets.FONTS.ASCII7)  # Monospace font, 6x9 pixels base
        Lcd.setTextSize(2)  # Double size = 12x18 pixels per character
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)

        # Draw centered-ish greeting
        # Screen is 240x135 pixels in landscape mode
        Lcd.setCursor(10, 50)
        Lcd.print("Hello World!")

        # Draw help text at bottom
        Lcd.setTextSize(1)
        Lcd.setCursor(10, 125)
        Lcd.print("ESC = back")

    async def on_run(self):
        """
        Async background task.

        Called after on_view(). Runs continuously while the app is active.
        Use this for:
        - Periodic updates (animations, sensor readings, clocks)
        - Background processing
        - Waiting for events

        IMPORTANT:
        ----------
        - This is an async function - use 'await' for delays!
        - Use 'await asyncio.sleep_ms(n)' instead of 'time.sleep()'
        - If you don't need background work, just idle with a sleep loop
        - When the app exits, this task is automatically cancelled

        EXAMPLE WITH UPDATES:
        ---------------------
        async def on_run(self):
            counter = 0
            while True:
                counter += 1
                Lcd.setCursor(10, 80)
                Lcd.print(f"Count: {counter}")
                await asyncio.sleep_ms(1000)  # Update every second
        """
        # This app has no background work, so just idle
        # The sleep prevents busy-waiting and allows other tasks to run
        while True:
            await asyncio.sleep_ms(100)


if __name__ == "__main__":
    # Standalone mode - run this app directly, ESC exits to REPL
    import M5

    M5.begin()
    Lcd.setRotation(1)
    Lcd.setBrightness(40)

    from lib.framework import Framework

    fw = Framework()
    fw.install(HelloWorld())
    fw.start()
