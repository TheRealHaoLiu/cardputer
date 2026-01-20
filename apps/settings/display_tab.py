"""
Display Tab - Brightness control
"""

from M5 import Lcd, Widgets

from . import (
    BLACK,
    CONTENT_H,
    CONTENT_Y,
    CYAN,
    DARK_GRAY,
    GRAY,
    GREEN,
    SCREEN_W,
    WHITE,
    YELLOW,
    TabBase,
)


class DisplayTab(TabBase):
    """Display settings tab."""

    def __init__(self):
        self.brightness = 128
        self.brightness_saved = 128

    def on_enter(self):
        """Called when tab becomes active."""
        try:
            self.brightness = Lcd.getBrightness()
            self.brightness_saved = self.brightness
        except:
            pass

    def draw(self, app):
        """Draw display tab content."""
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(1)

        # Title
        Lcd.setTextColor(CYAN, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 5)
        Lcd.print("Brightness")

        # Current value as percentage
        pct = (self.brightness * 100) // 255
        value_str = f"{pct}%"
        Lcd.setTextColor(WHITE, BLACK)
        Lcd.setCursor(SCREEN_W - 10 - len(value_str) * 6, CONTENT_Y + 5)
        Lcd.print(value_str)

        # Slider bar
        bar_x = 10
        bar_y = CONTENT_Y + 22
        bar_w = SCREEN_W - 20
        bar_h = 14
        Lcd.fillRect(bar_x, bar_y, bar_w, bar_h, DARK_GRAY)

        fill_w = (self.brightness * (bar_w - 2)) // 255
        if fill_w > 0:
            Lcd.fillRect(bar_x + 1, bar_y + 1, fill_w, bar_h - 2, GREEN)

        Lcd.drawRect(bar_x, bar_y, bar_w, bar_h, WHITE)

        # Presets
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 45)
        Lcd.print("Presets:")
        Lcd.setTextColor(WHITE, BLACK)
        Lcd.setCursor(70, CONTENT_Y + 45)
        Lcd.print("[1]25% [2]50% [3]75% [4]100%")

        # Controls
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 60)
        Lcd.print("[,/] Adjust  [S] Save  [0] Off")

        # Save indicator
        if self.brightness != self.brightness_saved:
            Lcd.setTextColor(YELLOW, BLACK)
            Lcd.setCursor(10, CONTENT_Y + 78)
            Lcd.print("* Unsaved changes")
        else:
            Lcd.setTextColor(GREEN, BLACK)
            Lcd.setCursor(10, CONTENT_Y + 78)
            Lcd.print("  Saved")

    def _redraw(self, app):
        """Redraw tab content."""
        Lcd.fillRect(0, CONTENT_Y, SCREEN_W, CONTENT_H, BLACK)
        self.draw(app)

    def _set_brightness(self, value):
        """Set brightness to value."""
        self.brightness = max(0, min(255, value))
        Lcd.setBrightness(self.brightness)

    def _adjust(self, app, delta):
        """Adjust brightness by delta."""
        self._set_brightness(self.brightness + delta)
        self._redraw(app)

    def _save(self, app):
        """Save brightness to NVS."""
        try:
            import esp32
            nvs = esp32.NVS("settings")
            nvs.set_i32("brightness", self.brightness)
            nvs.commit()
            self.brightness_saved = self.brightness
            print(f"[display] Brightness saved: {self.brightness}")
        except Exception as e:
            print(f"[display] NVS save failed: {e}")
        self._redraw(app)

    def _screen_off(self, app):
        """Turn off screen."""
        print("[display] Screen off")
        Lcd.setBrightness(0)

    def handle_key(self, app, key):
        """Handle key press."""
        from libs.keycode import KEY_NAV_LEFT, KEY_NAV_RIGHT

        # Restore screen if off
        if self.brightness == 0:
            self._set_brightness(self.brightness_saved or 128)
            self._redraw(app)
            return True

        if key == KEY_NAV_LEFT:
            self._adjust(app, -15)
            return True

        if key == KEY_NAV_RIGHT:
            self._adjust(app, 15)
            return True

        if key == ord("1"):
            self._set_brightness(64)
            self._redraw(app)
            return True

        if key == ord("2"):
            self._set_brightness(128)
            self._redraw(app)
            return True

        if key == ord("3"):
            self._set_brightness(191)
            self._redraw(app)
            return True

        if key == ord("4"):
            self._set_brightness(255)
            self._redraw(app)
            return True

        if key == ord("0"):
            self._screen_off(app)
            return True

        if key == ord("s") or key == ord("S"):
            self._save(app)
            return True

        return False
