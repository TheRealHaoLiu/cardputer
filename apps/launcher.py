"""
Launcher App - Home Screen Menu
================================

The launcher is the home screen that displays all installed apps.
Users navigate with keyboard and press Enter to launch an app.
Pressing ESC from any app returns here.

HOW IT WORKS:
-------------
1. Framework calls on_view() - we draw the menu
2. Framework routes keyboard events to _kb_event_handler()
3. User navigates with ;/. keys and selects with Enter
4. We call fw.launch_app() to switch to selected app
5. When that app exits (ESC), framework calls our on_view() again

CONTROLS:
---------
- ; (semicolon) or UP arrow = Move selection up
- . (period) or DOWN arrow = Move selection down
- Enter = Launch selected app

The launcher excludes itself from the app list (you can't launch the launcher).
"""

import sys
import os

# =============================================================================
# IMPORTS
# =============================================================================

from M5 import Lcd, Widgets

# Path setup for imports
for lib_path in ["/flash/lib", "/remote/lib"]:
    if lib_path not in sys.path:
        sys.path.insert(0, lib_path)

from lib.app_base import AppBase

# Import KeyCode for arrow key constants
# Falls back to a local definition if not available in firmware
try:
    from unit import KeyCode
except ImportError:
    class KeyCode:
        KEYCODE_ESC = 0x1B
        KEYCODE_ENTER = 0x0D
        KEYCODE_UP = 0x26
        KEYCODE_DOWN = 0x28


# =============================================================================
# RUN MODE DETECTION
# =============================================================================
# Detect if we're running from mounted files (development) or flash (deployed).
# This is shown in the UI to help during development.

try:
    os.stat("/remote/main.py")
    RUN_MODE = "remote"  # Files mounted from computer
except OSError:
    RUN_MODE = "flash"  # Files deployed to device


# =============================================================================
# LAYOUT CONSTANTS
# =============================================================================
# These control the visual layout of the menu.
# Adjust these if you want more/fewer items visible.

MENU_START_Y = 22   # Y position where menu items start (below title)
MENU_ITEM_H = 22    # Height of each menu item in pixels
VISIBLE_ITEMS = 4   # How many items fit on screen at once


# =============================================================================
# LAUNCHER APP CLASS
# =============================================================================


class LauncherApp(AppBase):
    """
    The launcher app - displays a menu of all installed apps.

    This is both the "home screen" and an app itself.
    The framework treats it specially - ESC always returns here.
    """

    def __init__(self):
        super().__init__()
        self.name = "Launcher"

        # Menu state
        # _selected: Index of currently highlighted item
        # _scroll_offset: Index of first visible item (for scrolling)
        self._selected = 0
        self._scroll_offset = 0

    def on_view(self):
        """
        Set up display and draw the menu.

        Called when:
        - Launcher first starts (on boot)
        - Returning from another app (after ESC)
        """
        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        self._draw_menu()

    def _get_apps(self):
        """
        Get list of apps to display (excludes self).

        The launcher shouldn't show itself in the list -
        you can't "launch" the launcher from the launcher.
        """
        if self._fw:
            return [app for app in self._fw.get_apps() if app != self]
        return []

    def _draw_menu(self):
        """
        Draw the menu on screen.

        This handles:
        - Title bar with run mode indicator
        - Scrollable list of apps with ">" cursor
        - Scroll indicators (^ and v) when there are more items
        - Key hints at the bottom
        """
        apps = self._get_apps()

        # Handle empty app list
        if not apps:
            Lcd.fillScreen(Lcd.COLOR.BLACK)
            Lcd.setCursor(10, 50)
            Lcd.print("No apps installed")
            return

        # Keep selection within bounds
        # This handles the case where apps list changed
        if self._selected >= len(apps):
            self._selected = len(apps) - 1
        if self._selected < 0:
            self._selected = 0

        # Adjust scroll to keep selection visible
        # If selection moved above visible area, scroll up
        if self._selected < self._scroll_offset:
            self._scroll_offset = self._selected
        # If selection moved below visible area, scroll down
        elif self._selected >= self._scroll_offset + VISIBLE_ITEMS:
            self._scroll_offset = self._selected - VISIBLE_ITEMS + 1

        # Clear screen and draw title
        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(0, 0)
        Lcd.print("Cardputer")

        # Show run mode indicator (helps during development)
        # Cyan = running from mounted files (development)
        # Green = running from flash (deployed)
        Lcd.setTextSize(1)
        if RUN_MODE == "remote":
            Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        else:
            Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(200, 5)
        Lcd.print(RUN_MODE)

        # Draw visible menu items
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)

        for i in range(VISIBLE_ITEMS):
            idx = self._scroll_offset + i
            if idx >= len(apps):
                break

            app = apps[idx]
            y = MENU_START_Y + i * MENU_ITEM_H
            Lcd.setCursor(10, y)

            # ">" cursor indicates selected item
            prefix = "> " if idx == self._selected else "  "

            # Get app name (apps should set self.name)
            app_name = getattr(app, "name", app.__class__.__name__)
            Lcd.print(f"{prefix}{app_name}")

        # Draw scroll indicators if there are items above/below
        Lcd.setTextSize(1)
        if self._scroll_offset > 0:
            Lcd.setCursor(225, MENU_START_Y)
            Lcd.print("^")  # More items above
        if self._scroll_offset + VISIBLE_ITEMS < len(apps):
            Lcd.setCursor(225, MENU_START_Y + (VISIBLE_ITEMS - 1) * MENU_ITEM_H + 10)
            Lcd.print("v")  # More items below

        # Draw key hints at bottom
        Lcd.setCursor(0, 125)
        Lcd.print("Enter=Select  ;/.=Nav")

    async def _kb_event_handler(self, event, fw):
        """
        Handle keyboard input for menu navigation.

        This is called by the framework whenever a key is pressed.

        Parameters:
        -----------
        event : KeyEvent
            - event.key: The key code (ASCII or KeyCode constant)
            - event.status: Set to True if you handled the event
        fw : Framework
            The framework instance (for launching apps, etc.)

        Key handling:
        - Enter (0x0D or 0x0A): Launch selected app
        - ; (59) or UP: Move selection up
        - . (46) or DOWN: Move selection down
        - ESC: Not handled here - framework handles it
        """
        key = event.key
        apps = self._get_apps()

        if not apps:
            return

        # Enter - launch the selected app
        if key == KeyCode.KEYCODE_ENTER or key == 0x0D or key == 0x0A:
            event.status = True  # Mark as handled
            selected_app = apps[self._selected]
            await fw.launch_app(selected_app)
            return

        # Up navigation: ; (semicolon) or UP arrow
        if key == 59 or key == KeyCode.KEYCODE_UP:
            event.status = True
            # Wrap around: if at top, go to bottom
            self._selected = (self._selected - 1) % len(apps)
            self._draw_menu()
            return

        # Down navigation: . (period) or DOWN arrow
        if key == 46 or key == KeyCode.KEYCODE_DOWN:
            event.status = True
            # Wrap around: if at bottom, go to top
            self._selected = (self._selected + 1) % len(apps)
            self._draw_menu()
            return

        # Other keys: don't mark as handled
        # This allows ESC to flow through to framework

    async def on_run(self):
        """
        Background task - the launcher just idles.

        The launcher doesn't need to do anything in the background.
        All interaction happens through _kb_event_handler().
        """
        import asyncio
        while True:
            await asyncio.sleep_ms(100)
