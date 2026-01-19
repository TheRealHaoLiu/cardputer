"""
Brightness Demo - LCD Brightness Control
=========================================

Demonstrates how to control the LCD backlight brightness for power
saving or visibility adjustment. The brightness setting can be
persisted using NVS (see storage_demo.py).

BRIGHTNESS API:
---------------
    Lcd.setBrightness(0-255)   # Set brightness (0=off, 255=max)
    Lcd.getBrightness()        # Get current brightness

BRIGHTNESS LEVELS:
------------------
    0     = Screen off (backlight disabled)
    1-50  = Very dim (power saving, dark environments)
    51-100 = Low (indoor use)
    101-150 = Medium (typical use)
    151-200 = Bright (well-lit environments)
    201-255 = Maximum (outdoor/bright light)

POWER CONSIDERATIONS:
---------------------
    - Lower brightness = longer battery life
    - Screen off (0) = minimum power consumption
    - Maximum brightness can drain battery quickly

CONTROLS:
---------
    Up/Down or +/- = Adjust brightness
    1-5 = Quick presets (20%, 40%, 60%, 80%, 100%)
    0 = Screen off (press any key to restore)
    S = Save to NVS (persists after reboot)
    ESC = Exit to launcher
"""

import asyncio
import sys

for path in ["/flash", "/remote"]:
    if path not in sys.path:
        sys.path.insert(0, path)

import esp32
from M5 import Lcd, Widgets

from lib.app_base import AppBase
from lib.keycode import KeyCode

SCREEN_W = 240
SCREEN_H = 135

# Brightness step for adjustments
BRIGHTNESS_STEP = 10

# Quick preset levels (percentage)
PRESETS = {
    ord("1"): 20,
    ord("2"): 40,
    ord("3"): 60,
    ord("4"): 80,
    ord("5"): 100,
}


class BrightnessDemo(AppBase):
    """LCD brightness control demo."""

    def __init__(self):
        super().__init__()
        self.name = "Brightness"
        self._brightness = 40  # Default
        self._screen_off = False
        self._saved_brightness = None

    def on_launch(self):
        """Load current brightness."""
        self._brightness = Lcd.getBrightness()

        # Try to load saved brightness from NVS
        try:
            nvs = esp32.NVS("uiflow")
            self._saved_brightness = nvs.get_u8("brightness")
        except OSError:
            self._saved_brightness = None

    def on_view(self):
        """Draw the brightness control interface."""
        if self._screen_off:
            Lcd.fillScreen(Lcd.COLOR.BLACK)
            return

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.ASCII7)

        # Title
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("Brightness")

        Lcd.setTextSize(1)

        # Current value
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 28)
        pct = int(self._brightness / 255 * 100)
        Lcd.print(f"Current: {self._brightness} ({pct}%)")

        # Brightness bar
        bar_x, bar_y, bar_w, bar_h = 10, 45, 180, 20
        Lcd.drawRect(bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2, Lcd.COLOR.WHITE)

        # Gradient bar showing brightness level
        fill_w = int(self._brightness / 255 * bar_w)

        # Color gradient from dim to bright
        if self._brightness < 85:
            bar_color = Lcd.COLOR.RED
        elif self._brightness < 170:
            bar_color = Lcd.COLOR.YELLOW
        else:
            bar_color = Lcd.COLOR.GREEN

        Lcd.fillRect(bar_x, bar_y, fill_w, bar_h, bar_color)
        Lcd.fillRect(bar_x + fill_w, bar_y, bar_w - fill_w, bar_h, Lcd.COLOR.BLACK)

        # Percentage text on bar
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(bar_x + bar_w + 5, bar_y + 6)
        Lcd.print(f"{pct:3}%")

        # Saved value indicator
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 72)
        if self._saved_brightness is not None:
            saved_pct = int(self._saved_brightness / 255 * 100)
            Lcd.print(f"Saved: {self._saved_brightness} ({saved_pct}%)")
        else:
            Lcd.print("Saved: (none)")

        # Presets
        Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 87)
        Lcd.print("1:20% 2:40% 3:60% 4:80% 5:100%")

        # Controls
        Lcd.setCursor(10, 100)
        Lcd.print("+/-: Adjust  0: Off  S: Save")

        # Footer
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(0, SCREEN_H - 12)
        Lcd.print("ESC=Exit")

    def _update_brightness(self, new_value):
        """Update brightness and redraw."""
        self._brightness = max(1, min(255, new_value))  # Clamp to 1-255
        Lcd.setBrightness(self._brightness)
        self.on_view()

    def _save_brightness(self):
        """Save current brightness to NVS."""
        try:
            nvs = esp32.NVS("uiflow")
            nvs.set_u8("brightness", self._brightness)
            nvs.commit()
            self._saved_brightness = self._brightness

            # Show confirmation
            Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
            Lcd.setCursor(140, 72)
            Lcd.print(" Saved!")
        except OSError as e:
            Lcd.setTextColor(Lcd.COLOR.RED, Lcd.COLOR.BLACK)
            Lcd.setCursor(140, 72)
            Lcd.print(f" Error: {e}")

    async def _kb_event_handler(self, event, fw):
        """Handle keyboard events."""
        key = event.key

        # If screen is off, any key restores it
        if self._screen_off:
            self._screen_off = False
            Lcd.setBrightness(self._brightness)
            self.on_view()
            event.status = True
            return

        # Don't handle ESC
        if key == KeyCode.KEYCODE_ESC:
            return

        # Brightness up
        if key == ord("+") or key == ord("=") or key == KeyCode.KEYCODE_UP:
            self._update_brightness(self._brightness + BRIGHTNESS_STEP)
            event.status = True
            return

        # Brightness down
        if key == ord("-") or key == KeyCode.KEYCODE_DOWN:
            self._update_brightness(self._brightness - BRIGHTNESS_STEP)
            event.status = True
            return

        # Screen off
        if key == ord("0"):
            self._screen_off = True
            Lcd.setBrightness(0)
            self.on_view()
            event.status = True
            return

        # Presets
        if key in PRESETS:
            pct = PRESETS[key]
            self._update_brightness(int(pct / 100 * 255))
            event.status = True
            return

        # Save to NVS
        if key == ord("s") or key == ord("S"):
            self._save_brightness()
            event.status = True
            return

        event.status = True

    async def on_run(self):
        """Background task."""
        while True:
            await asyncio.sleep_ms(100)


# Export for framework discovery
App = BrightnessDemo

if __name__ == "__main__":
    import M5

    M5.begin()
    Lcd.setRotation(1)
    Lcd.setBrightness(40)

    from lib.framework import Framework

    fw = Framework()
    fw.install(BrightnessDemo())
    fw.start()
