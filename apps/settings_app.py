"""
Settings App - Device Configuration
====================================

Tabbed settings interface for configuring the Cardputer.

TABS:
    WiFi    - Network configuration
    Display - Brightness control
    Sound   - Volume control
    System  - Boot options, memory, reboot
    About   - Device information

CONTROLS:
    Tab     = Next tab
    ;/.     = Navigate (tab-specific)
    Enter   = Select/confirm
    ESC     = Exit to launcher
"""

import asyncio
import sys

# Add lib paths for imports (needed on device)
for path in ["/flash", "/remote"]:
    if path not in sys.path:
        sys.path.insert(0, path)

from M5 import Lcd, Widgets

from lib.app_base import AppBase
from lib.keycode import HID_TAB, KEY_NAV_DOWN, KEY_NAV_UP, KeyCode

# Import shared constants from settings package
from apps.settings import (
    BLACK,
    CONTENT_H,
    CONTENT_Y,
    DARK_GRAY,
    GRAY,
    SCREEN_H,
    SCREEN_W,
    TAB_H,
    TAB_NAMES,
    TAB_Y,
    WHITE,
)

# Tab indices
TAB_WIFI = 0
TAB_DISPLAY = 1
TAB_SOUND = 2
TAB_SYSTEM = 3
TAB_ABOUT = 4

# Footer
FOOTER_Y = SCREEN_H - 12


class SettingsApp(AppBase):
    """
    Tabbed settings application with lazy-loaded tab modules.
    """

    def __init__(self):
        super().__init__()
        self.name = "Settings"
        self._current_tab = 0
        self._tabs = {}  # Lazy-loaded tab instances
        print("[settings] App initialized")

    def _get_tab(self, index):
        """
        Get tab instance, loading module lazily if needed.

        Args:
            index: Tab index (TAB_WIFI, TAB_DISPLAY, etc.)

        Returns:
            Tab instance
        """
        if index not in self._tabs:
            print(f"[settings] Loading tab: {TAB_NAMES[index]}")
            if index == TAB_WIFI:
                from apps.settings.wifi_tab import WiFiTab
                self._tabs[index] = WiFiTab()
            elif index == TAB_DISPLAY:
                from apps.settings.display_tab import DisplayTab
                self._tabs[index] = DisplayTab()
            elif index == TAB_SOUND:
                from apps.settings.sound_tab import SoundTab
                self._tabs[index] = SoundTab()
            elif index == TAB_SYSTEM:
                from apps.settings.system_tab import SystemTab
                self._tabs[index] = SystemTab()
            elif index == TAB_ABOUT:
                from apps.settings.about_tab import AboutTab
                self._tabs[index] = AboutTab()
        return self._tabs.get(index)

    def on_launch(self):
        """Called when app becomes active."""
        print("[settings] Launched")
        # Pre-load Display tab and init brightness
        tab = self._get_tab(TAB_DISPLAY)
        if hasattr(tab, 'on_enter'):
            tab.on_enter()

    def on_view(self):
        """Draw the complete settings interface."""
        print(f"[settings] Drawing view, tab: {TAB_NAMES[self._current_tab]}")
        Lcd.fillScreen(BLACK)
        self._draw_tabs()
        self._draw_content()
        self._draw_footer()

    def _draw_tabs(self):
        """Draw the tab bar."""
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(1)

        tab_w = SCREEN_W // len(TAB_NAMES)

        for i, name in enumerate(TAB_NAMES):
            x = i * tab_w

            if i == self._current_tab:
                Lcd.fillRect(x, TAB_Y, tab_w, TAB_H, WHITE)
                Lcd.setTextColor(BLACK, WHITE)
            else:
                Lcd.fillRect(x, TAB_Y, tab_w, TAB_H, DARK_GRAY)
                Lcd.setTextColor(GRAY, DARK_GRAY)

            text_x = x + (tab_w - len(name) * 6) // 2
            text_y = TAB_Y + 4
            Lcd.setCursor(text_x, text_y)
            Lcd.print(name)

        Lcd.drawLine(0, TAB_H, SCREEN_W, TAB_H, GRAY)

    def _draw_content(self):
        """Draw current tab content."""
        tab = self._get_tab(self._current_tab)
        if tab:
            tab.draw(self)
        else:
            self._draw_placeholder()

    def _draw_placeholder(self):
        """Draw placeholder for unloaded tabs."""
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(2)
        Lcd.setTextColor(WHITE, BLACK)

        tab_name = TAB_NAMES[self._current_tab]
        text_w = len(tab_name) * 12
        x = (SCREEN_W - text_w) // 2
        y = CONTENT_Y + (CONTENT_H - 16) // 2

        Lcd.setCursor(x, y)
        Lcd.print(tab_name)

    def _draw_footer(self):
        """Draw footer with navigation hints."""
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(1)
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(5, FOOTER_Y)
        Lcd.print("Tab=Next  Enter=Select  ESC=Exit")

    def _switch_tab(self, direction):
        """Switch to next or previous tab."""
        old_tab = self._current_tab
        self._current_tab = (self._current_tab + direction) % len(TAB_NAMES)
        print(f"[settings] Tab: {TAB_NAMES[old_tab]} -> {TAB_NAMES[self._current_tab]}")

        # Call on_enter if tab has it
        tab = self._get_tab(self._current_tab)
        if tab and hasattr(tab, 'on_enter'):
            tab.on_enter()

        self.on_view()

    async def _kb_event_handler(self, event, fw):
        """Handle keyboard events."""
        key = event.key

        # ESC - let framework handle exit
        if key == KeyCode.KEYCODE_ESC:
            print("[settings] ESC pressed, exiting")
            return

        # Tab key - next tab
        if key == HID_TAB:
            self._switch_tab(1)
            event.status = True
            return

        # Get current tab for key handling
        tab = self._get_tab(self._current_tab)

        # For WiFi tab, ; and . are used for list navigation
        # For other tabs, they switch tabs
        if self._current_tab != TAB_WIFI:
            if key == KEY_NAV_UP:
                self._switch_tab(-1)
                event.status = True
                return
            if key == KEY_NAV_DOWN:
                self._switch_tab(1)
                event.status = True
                return

        # Dispatch to tab handler
        if tab and tab.handle_key(self, key):
            event.status = True
            return

        event.status = True

    async def on_run(self):
        """Background task loop."""
        while True:
            await asyncio.sleep_ms(100)


# Export for framework
App = SettingsApp

# Allow direct execution
if __name__ == "__main__":
    import M5

    M5.begin()
    Lcd.setRotation(1)
    Lcd.setBrightness(80)

    from lib.framework import Framework

    fw = Framework()
    fw.install(SettingsApp())
    fw.start()
