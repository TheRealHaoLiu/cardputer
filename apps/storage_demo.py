"""
Storage Demo - NVS Persistent Storage
======================================

Demonstrates ESP32's Non-Volatile Storage (NVS) - a key-value store
that persists across reboots. Perfect for saving settings, high scores,
or any data that needs to survive power cycles.

NVS API SUMMARY:
----------------
    import esp32
    nvs = esp32.NVS('namespace')   # Create/open namespace (max 15 chars)

    # Read values (raises OSError if key doesn't exist)
    nvs.get_u8('key')              # Unsigned 8-bit (0-255)
    nvs.get_i32('key')             # Signed 32-bit integer
    nvs.get_str('key')             # String

    # Write values (MUST call commit() after!)
    nvs.set_u8('key', value)
    nvs.set_i32('key', value)
    nvs.set_str('key', value)
    nvs.commit()                   # Saves to flash - don't forget!

IMPORTANT NOTES:
----------------
- Always call commit() after writes, or data won't be saved!
- Key names: max 15 characters
- Namespace names: max 15 characters
- Data survives reboots and power cycles

CONTROLS:
---------
    + = Increment counter
    - = Decrement counter
    R = Reset counter to 0
    N = Edit name (toggles edit mode)
    ESC = Exit to launcher
"""

import asyncio
import sys

for path in ["/flash", "/remote"]:
    if path not in sys.path:
        sys.path.insert(0, path)

import esp32
from M5 import Lcd, Widgets

from libs.app_base import AppBase
from libs.keycode import KeyCode

SCREEN_W = 240
SCREEN_H = 135

# NVS namespace for this demo
NVS_NAMESPACE = "storage_demo"


class StorageDemo(AppBase):
    """NVS persistent storage demo with counter and name."""

    def __init__(self):
        super().__init__()
        self.name = "Storage Demo"
        self._nvs = None
        self._counter = 0
        self._stored_name = ""
        self._edit_mode = False
        self._boot_count = 0

    def on_launch(self):
        """Initialize NVS and load saved values."""
        self._nvs = esp32.NVS(NVS_NAMESPACE)

        # Load counter (default to 0 if not set)
        try:
            self._counter = self._nvs.get_i32("counter")
        except OSError:
            self._counter = 0

        # Load name (default to empty if not set)
        try:
            self._stored_name = self._nvs.get_str("name")
        except OSError:
            self._stored_name = ""

        # Increment and save boot count
        try:
            self._boot_count = self._nvs.get_i32("boots") + 1
        except OSError:
            self._boot_count = 1

        self._nvs.set_i32("boots", self._boot_count)
        self._nvs.commit()

    def on_view(self):
        """Draw the storage demo interface."""
        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.ASCII7)

        # Title
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("Storage Demo")

        Lcd.setTextSize(1)

        # Boot count (proves persistence)
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 28)
        Lcd.print(f"Boot count: {self._boot_count}")
        Lcd.setCursor(130, 28)
        Lcd.print("(persists!)")

        # Counter display
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 45)
        Lcd.print("Counter:")

        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
        Lcd.setCursor(75, 42)
        Lcd.print(f"{self._counter:6}")

        Lcd.setTextSize(1)

        # Name display
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 65)
        Lcd.print("Name:")

        name_color = Lcd.COLOR.CYAN if self._edit_mode else Lcd.COLOR.YELLOW
        Lcd.setTextColor(name_color, Lcd.COLOR.BLACK)
        Lcd.setCursor(50, 65)
        display_name = self._stored_name if self._stored_name else "(empty)"
        if self._edit_mode:
            display_name += "_"  # Cursor
        Lcd.print(f"{display_name:<20}")

        # Controls
        Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 85)
        Lcd.print("+/-: Counter  R: Reset")
        Lcd.setCursor(10, 97)
        if self._edit_mode:
            Lcd.print("Type name, Enter to save")
        else:
            Lcd.print("N: Edit name")

        # Footer
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(0, SCREEN_H - 12)
        Lcd.print("ESC=Exit  Data saved to NVS")

    def _save_counter(self):
        """Save counter to NVS."""
        self._nvs.set_i32("counter", self._counter)
        self._nvs.commit()

    def _save_name(self):
        """Save name to NVS."""
        self._nvs.set_str("name", self._stored_name)
        self._nvs.commit()

    async def _kb_event_handler(self, event, fw):
        """Handle keyboard events."""
        key = event.key

        # Don't handle ESC
        if key == KeyCode.KEYCODE_ESC:
            self._edit_mode = False
            return

        # Edit mode handling
        if self._edit_mode:
            # Enter saves and exits edit mode
            if key == KeyCode.KEYCODE_ENTER:
                self._save_name()
                self._edit_mode = False
                self.on_view()
                event.status = True
                return

            # Backspace
            if key == KeyCode.KEYCODE_BACKSPACE:
                if len(self._stored_name) > 0:
                    self._stored_name = self._stored_name[:-1]
                    self.on_view()
                event.status = True
                return

            # Printable characters
            if 0x20 <= key <= 0x7E:
                if len(self._stored_name) < 15:  # NVS key limit
                    self._stored_name += chr(key)
                    self.on_view()
                event.status = True
                return

            event.status = True
            return

        # Normal mode controls
        # Increment counter
        if key == ord("+") or key == ord("="):
            self._counter += 1
            self._save_counter()
            self.on_view()
            event.status = True
            return

        # Decrement counter
        if key == ord("-"):
            self._counter -= 1
            self._save_counter()
            self.on_view()
            event.status = True
            return

        # Reset counter
        if key == ord("r") or key == ord("R"):
            self._counter = 0
            self._save_counter()
            self.on_view()
            event.status = True
            return

        # Toggle edit mode for name
        if key == ord("n") or key == ord("N"):
            self._edit_mode = True
            self.on_view()
            event.status = True
            return

        event.status = True

    async def on_run(self):
        """Background task."""
        while True:
            await asyncio.sleep_ms(100)


# Export for framework discovery
App = StorageDemo

if __name__ == "__main__":
    import M5

    M5.begin()
    Lcd.setRotation(1)
    Lcd.setBrightness(40)

    from libs.framework import Framework

    fw = Framework()
    fw.install(StorageDemo())
    fw.start()
