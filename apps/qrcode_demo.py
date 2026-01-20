"""
QR Code Demo - Generate and Display QR Codes
=============================================

Demonstrates the LCD's built-in QR code generation capability.
QR codes can encode URLs, text, WiFi credentials, and more.

QR CODE API:
------------
    Lcd.drawQR(text, x, y, width, version)

    Parameters:
    - text: String to encode (URL, text, etc.)
    - x, y: Position on screen
    - width: Pixel width of QR code
    - version: QR version 1-40 (higher = more data capacity)
               Version 1 = 21x21 modules, can hold ~25 chars
               Version 3 = 29x29 modules, can hold ~77 chars
               Version 10 = 57x57 modules, can hold ~395 chars

QR CODE CONTENT TYPES:
----------------------
    URL:     "https://example.com"
    Text:    "Hello World"
    WiFi:    "WIFI:T:WPA;S:NetworkName;P:Password;;"
    Email:   "mailto:user@example.com"
    Phone:   "tel:+1234567890"
    SMS:     "sms:+1234567890"

CONTROLS:
---------
    Left/Right or ,/. = Previous/Next QR code
    ESC = Exit to launcher
"""

import asyncio
import sys

for path in ["/flash", "/remote"]:
    if path not in sys.path:
        sys.path.insert(0, path)

from M5 import Lcd, Widgets

from libs.app_base import AppBase
from libs.keycode import KeyCode

SCREEN_W = 240
SCREEN_H = 135

# Sample QR codes to display
QR_SAMPLES = [
    ("M5Stack", "https://m5stack.com", 3),
    ("GitHub", "https://github.com", 3),
    ("Hello!", "Hello Cardputer!", 2),
    ("WiFi Example", "WIFI:T:WPA;S:MyNetwork;P:password123;;", 5),
    ("Email", "mailto:hello@example.com", 3),
    ("Phone", "tel:+15551234567", 2),
]


class QRCodeDemo(AppBase):
    """QR Code generation demo."""

    def __init__(self):
        super().__init__()
        self.name = "QR Code Demo"
        self._qr_idx = 0

    def on_view(self):
        """Draw the current QR code."""
        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.ASCII7)

        # Title
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("QR Code Demo")

        # Get current QR data
        name, content, version = QR_SAMPLES[self._qr_idx]

        # QR code info
        Lcd.setTextSize(1)
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 28)
        Lcd.print(f"Type: {name}")

        # Show content (truncated if long)
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 40)
        display_content = content if len(content) <= 25 else content[:22] + "..."
        Lcd.print(f"{display_content}")

        # Show version
        Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 52)
        Lcd.print(f"Version: {version}")

        # Draw QR code on right side
        qr_size = 80
        qr_x = SCREEN_W - qr_size - 10
        qr_y = 30
        Lcd.drawQR(content, qr_x, qr_y, qr_size, version)

        # Navigation hint
        Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 70)
        Lcd.print("</> or ,/. to navigate")

        # API hint
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 85)
        Lcd.print("drawQR(text,x,y,w,ver)")

        # Footer
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(0, SCREEN_H - 12)
        Lcd.print(f"ESC=Exit    [{self._qr_idx + 1}/{len(QR_SAMPLES)}]")

    async def _kb_event_handler(self, event, fw):
        """Handle keyboard events."""
        key = event.key

        # Don't handle ESC
        if key == KeyCode.KEYCODE_ESC:
            return

        # Next QR
        if key == ord(".") or key == ord(">") or key == KeyCode.KEYCODE_RIGHT:
            self._qr_idx = (self._qr_idx + 1) % len(QR_SAMPLES)
            self.on_view()
            event.status = True
            return

        # Previous QR
        if key == ord(",") or key == ord("<") or key == KeyCode.KEYCODE_LEFT:
            self._qr_idx = (self._qr_idx - 1) % len(QR_SAMPLES)
            self.on_view()
            event.status = True
            return

        event.status = True

    async def on_run(self):
        """Background task."""
        while True:
            await asyncio.sleep_ms(100)


# Export for framework discovery
App = QRCodeDemo

if __name__ == "__main__":
    import M5

    M5.begin()
    Lcd.setRotation(1)
    Lcd.setBrightness(40)

    from libs.framework import Framework

    fw = Framework()
    fw.install(QRCodeDemo())
    fw.start()
