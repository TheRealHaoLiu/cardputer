"""
About Tab - Device information
"""

from M5 import Lcd, Widgets

from . import (
    BLACK,
    CONTENT_Y,
    GRAY,
    GREEN,
    WHITE,
    YELLOW,
    TabBase,
)


class AboutTab(TabBase):
    """About/device info tab."""

    def draw(self, app):
        """Draw about tab content."""
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(1)

        y = CONTENT_Y + 5
        line_h = 14

        # Device model
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, y)
        Lcd.print("Device:")
        Lcd.setTextColor(WHITE, BLACK)
        Lcd.setCursor(80, y)
        Lcd.print("M5Stack Cardputer")

        # Chip info
        y += line_h
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, y)
        Lcd.print("Chip:")
        Lcd.setTextColor(WHITE, BLACK)
        Lcd.setCursor(80, y)
        Lcd.print("ESP32-S3 @ 240MHz")

        # MicroPython version
        y += line_h
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, y)
        Lcd.print("uPython:")
        Lcd.setTextColor(WHITE, BLACK)
        Lcd.setCursor(80, y)
        try:
            import sys
            ver = sys.version.split()[0] if hasattr(sys, "version") else "unknown"
            Lcd.print(ver[:20])
        except:
            Lcd.print("unknown")

        # MAC address
        y += line_h
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, y)
        Lcd.print("MAC:")
        Lcd.setTextColor(WHITE, BLACK)
        Lcd.setCursor(80, y)
        try:
            import network
            wlan = network.WLAN(network.STA_IF)
            mac = wlan.config("mac")
            mac_str = ":".join(f"{b:02X}" for b in mac)
            Lcd.print(mac_str)
        except:
            Lcd.print("(unavailable)")

        # Uptime
        y += line_h
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, y)
        Lcd.print("Uptime:")
        Lcd.setTextColor(WHITE, BLACK)
        Lcd.setCursor(80, y)
        try:
            import time
            ticks = time.ticks_ms()
            secs = ticks // 1000
            mins = secs // 60
            hours = mins // 60
            secs = secs % 60
            mins = mins % 60
            Lcd.print(f"{hours}h {mins}m {secs}s")
        except:
            Lcd.print("(unavailable)")

        # Battery level
        y += line_h
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, y)
        Lcd.print("Battery:")
        Lcd.setCursor(80, y)
        try:
            from M5 import Power
            level = Power.getBatteryLevel()
            charging = Power.isCharging()
            if level > 50:
                Lcd.setTextColor(GREEN, BLACK)
            elif level > 20:
                Lcd.setTextColor(YELLOW, BLACK)
            else:
                Lcd.setTextColor(0xFF0000, BLACK)
            status = " (charging)" if charging else ""
            Lcd.print(f"{level}%{status}")
        except:
            Lcd.setTextColor(WHITE, BLACK)
            Lcd.print("(unavailable)")

    def handle_key(self, app, key):
        """Handle key press - About tab has no special keys."""
        return False
