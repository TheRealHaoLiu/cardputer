"""
Keyboard Demo - MatrixKeyboard Explorer
========================================

Demonstrates the MatrixKeyboard API available on Cardputer/Cardputer ADV.

API SUMMARY:
------------
MatrixKeyboard provides:
- tick()       : Poll keyboard (framework calls this)
- is_pressed() : True if a key was just pressed
- get_key()    : Returns ASCII key code
- get_string() : Returns string representation
- set_callback(): Register for raw KeyboardI2C events

KeyboardI2C internals (via set_callback):
- _shift_state   : True if Shift is held
- _fn_state      : True if Fn is held
- _modifier_mask : Bitmask of active modifiers

LIMITATIONS:
------------
- No key release detection
- No key hold/repeat detection
- Only discrete key presses are reported

CONTROLS:
---------
- Press any key = See key info
- Enter = Toggle API info page
- ESC = Exit to launcher
"""

import asyncio
import sys

for path in ["/flash", "/remote"]:
    if path not in sys.path:
        sys.path.insert(0, path)

import widgets
from M5 import Lcd, Widgets

from libs.app_base import AppBase

SCREEN_H = 135

# Key constants and modifiers
from libs.keycode import (
    KEY_MOD_LSHIFT,
    KeyCode,
    decode_modifiers,
    get_key_name,
)


class KeyboardDemo(AppBase):
    """Explore MatrixKeyboard features."""

    def __init__(self):
        super().__init__()
        self.name = "Keyboard Demo"
        self._kb = None
        self._kb_i2c = None  # KeyboardI2C for modifier access
        self._last_key = None
        self._last_char = ""
        self._key_count = 0
        self._page = 0  # 0 = key inspector, 1 = API info
        # Modifier state from KeyboardI2C
        self._shift = False
        self._fn = False
        self._modifier_mask = 0
        # Labels for key inspector (created in _draw_key_inspector)
        self._lbl_key = None
        self._lbl_hex = None
        self._lbl_char = None
        self._lbl_shift = None
        self._lbl_fn = None
        self._lbl_count = None
        self._lbl_mod = None

    def on_launch(self):
        """Get keyboard from framework and set up modifier tracking."""
        if self._fw and hasattr(self._fw, "_kb") and self._fw._kb:
            self._kb = self._fw._kb
            # Register callback to get KeyboardI2C access for modifiers
            if hasattr(self._kb, "set_callback"):
                self._kb.set_callback(self._on_kb_event)
        else:
            print("[keyboard_demo] Warning: No keyboard available")

    def _on_kb_event(self, kb_i2c):
        """Callback from MatrixKeyboard - captures modifier state."""
        self._kb_i2c = kb_i2c
        # Read modifier state from KeyboardI2C internals
        self._shift = getattr(kb_i2c, "_shift_state", False)
        self._fn = getattr(kb_i2c, "_fn_state", False)
        self._modifier_mask = getattr(kb_i2c, "_modifier_mask", 0)

    def on_view(self):
        """Draw the current page."""
        if self._page == 0:
            self._draw_key_inspector()
        else:
            self._draw_api_info()

    def _draw_key_inspector(self):
        """Page 0: Real-time key inspector."""
        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.ASCII7)

        # Title
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("Key Inspector")

        # Instructions
        Lcd.setTextSize(1)
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 28)
        Lcd.print("Press keys to see codes")

        # Row 1: Key, Hex, Char (static labels)
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 45)
        Lcd.print("Key:")
        Lcd.setCursor(75, 45)
        Lcd.print("Hex:")
        Lcd.setCursor(145, 45)
        Lcd.print("Char:")

        # Row 1: Value labels
        self._lbl_key = widgets.Label(
            "--", 35, 45, w=35,
            fg_color=Lcd.COLOR.YELLOW, bg_color=Lcd.COLOR.BLACK,
            font=Widgets.FONTS.ASCII7,
        )
        self._lbl_hex = widgets.Label(
            "--", 100, 45, w=40,
            fg_color=Lcd.COLOR.YELLOW, bg_color=Lcd.COLOR.BLACK,
            font=Widgets.FONTS.ASCII7,
        )
        self._lbl_char = widgets.Label(
            "--", 180, 45, w=55,
            fg_color=Lcd.COLOR.YELLOW, bg_color=Lcd.COLOR.BLACK,
            font=Widgets.FONTS.ASCII7,
        )

        # Row 2: Shift, Fn, Count (static labels)
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 60)
        Lcd.print("Shft:")
        Lcd.setCursor(75, 60)
        Lcd.print("Fn:")
        Lcd.setCursor(130, 60)
        Lcd.print("Count:")

        # Row 2: Value labels
        self._lbl_shift = widgets.Label(
            "off", 40, 60, w=30,
            fg_color=Lcd.COLOR.YELLOW, bg_color=Lcd.COLOR.BLACK,
            font=Widgets.FONTS.ASCII7,
        )
        self._lbl_fn = widgets.Label(
            "off", 93, 60, w=30,
            fg_color=Lcd.COLOR.YELLOW, bg_color=Lcd.COLOR.BLACK,
            font=Widgets.FONTS.ASCII7,
        )
        self._lbl_count = widgets.Label(
            "0", 170, 60, w=50,
            fg_color=Lcd.COLOR.YELLOW, bg_color=Lcd.COLOR.BLACK,
            font=Widgets.FONTS.ASCII7,
        )

        # Row 3: Mod (static label)
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 75)
        Lcd.print("Mod:")

        # Row 3: Value label (full width)
        self._lbl_mod = widgets.Label(
            "none", 35, 75, w=195,
            fg_color=Lcd.COLOR.YELLOW, bg_color=Lcd.COLOR.BLACK,
            font=Widgets.FONTS.ASCII7,
        )

        # Footer
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(0, SCREEN_H - 12)
        Lcd.print("Enter=API info  ESC=Exit")

        self._update_display()

    def _update_display(self):
        """Update the key display values using labels."""
        # Skip if labels not created yet (e.g., on API info page)
        if self._lbl_key is None:
            return

        is_shifted = self._shift or (self._modifier_mask & KEY_MOD_LSHIFT)

        # Row 1: Key, Hex, Char
        if self._last_key is not None:
            key = self._last_key
            self._lbl_key.set_text(str(key))
            self._lbl_hex.set_text(f"0x{key:02X}")

            # Determine char display
            key_name = get_key_name(key, is_shifted)
            if key_name and not is_shifted:
                char_text = key_name
            elif self._last_char:
                char_text = self._last_char
            elif 0x20 <= key <= 0x7E:
                char_text = f"'{chr(key)}'"
            elif key_name:
                char_text = key_name
            else:
                char_text = f"<{key}>"
            self._lbl_char.set_text(char_text)
        else:
            self._lbl_key.set_text("--")
            self._lbl_hex.set_text("--")
            self._lbl_char.set_text("--")

        # Row 2: Shift, Fn, Count
        self._lbl_shift.set_text("ON" if self._shift else "off")
        self._lbl_fn.set_text("ON" if self._fn else "off")
        self._lbl_count.set_text(str(self._key_count))

        # Row 3: Mod
        mod_str = decode_modifiers(self._modifier_mask)
        self._lbl_mod.set_text(mod_str if mod_str else "none")

    def _draw_api_info(self):
        """Page 1: Show API information."""
        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.ASCII7)

        # Title
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("Keyboard API")

        Lcd.setTextSize(1)

        # Left column - MatrixKeyboard
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(5, 28)
        Lcd.print("MatrixKeyboard:")

        Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
        methods = ["get_key()", "is_pressed()", "set_callback()"]
        y = 38
        for method in methods:
            Lcd.setCursor(8, y)
            Lcd.print(method)
            y += 10

        # Right column - KeyboardI2C modifiers
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(120, 28)
        Lcd.print("Modifiers:")

        Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
        mods = ["_shift_state", "_fn_state", "_modifier_mask"]
        y = 38
        for mod in mods:
            Lcd.setCursor(123, y)
            Lcd.print(mod)
            y += 10

        # Warning
        Lcd.setTextColor(Lcd.COLOR.RED, Lcd.COLOR.BLACK)
        Lcd.setCursor(5, 75)
        Lcd.print("No hold/release detection")

        # Usage hint
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(5, 90)
        Lcd.print("Ctrl+key: check modifier_mask")

        # Footer
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(0, SCREEN_H - 12)
        Lcd.print("Enter=Keys  ESC=Exit")

    async def _kb_event_handler(self, event, fw):
        """Handle keyboard events."""
        key = event.key

        # Don't handle ESC - let framework handle it
        if key == KeyCode.KEYCODE_ESC:
            return

        # Enter toggles pages
        if key == KeyCode.KEYCODE_ENTER:
            self._page = 1 - self._page
            self.on_view()
            event.status = True
            return

        # Track the key (only on key inspector page)
        if self._page == 0:
            self._last_key = key
            self._key_count += 1
            self._last_char = ""  # Reset on each keypress

            # Try to get string representation
            if self._kb and hasattr(self._kb, "get_string"):
                s = self._kb.get_string()
                if s:
                    self._last_char = f"'{s}'"

            self._update_display()

        event.status = True

    async def on_run(self):
        """Background task."""
        while True:
            await asyncio.sleep_ms(100)


if __name__ == "__main__":
    import M5

    M5.begin()
    Lcd.setRotation(1)
    Lcd.setBrightness(40)

    from libs.framework import Framework

    fw = Framework()
    fw.install(KeyboardDemo())
    fw.start()
