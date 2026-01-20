"""
Sound Tab - Volume control
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


class SoundTab(TabBase):
    """Sound settings tab."""

    def __init__(self):
        self.volume = 128
        self.volume_saved = 128
        self.muted = False
        self._speaker = None

    def _get_speaker(self):
        """Get speaker instance."""
        if self._speaker is None:
            try:
                from M5 import Speaker
                self._speaker = Speaker
            except ImportError:
                print("[sound] Speaker not available")
        return self._speaker

    def draw(self, app):
        """Draw sound tab content."""
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(1)

        # Title and mute indicator
        Lcd.setTextColor(CYAN, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 5)
        Lcd.print("Volume")

        if self.muted:
            Lcd.setTextColor(YELLOW, BLACK)
            Lcd.setCursor(70, CONTENT_Y + 5)
            Lcd.print("[MUTED]")
        else:
            Lcd.setTextColor(GREEN, BLACK)
            Lcd.setCursor(70, CONTENT_Y + 5)
            Lcd.print("[ON]")

        # Current value
        pct = (self.volume * 100) // 255
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

        fill_w = (self.volume * (bar_w - 2)) // 255
        fill_color = GRAY if self.muted else GREEN
        if fill_w > 0:
            Lcd.fillRect(bar_x + 1, bar_y + 1, fill_w, bar_h - 2, fill_color)

        Lcd.drawRect(bar_x, bar_y, bar_w, bar_h, WHITE)

        # Controls
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 45)
        Lcd.print("[,/] Adjust  [M] Mute  [T] Test")
        Lcd.setCursor(10, CONTENT_Y + 60)
        Lcd.print("[S] Save")

        # Save indicator
        if self.volume != self.volume_saved:
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

    def _set_volume(self, value):
        """Set volume."""
        self.volume = max(0, min(255, value))
        speaker = self._get_speaker()
        if speaker:
            speaker.setVolume(0 if self.muted else self.volume)

    def _adjust(self, app, delta):
        """Adjust volume by delta."""
        self._set_volume(self.volume + delta)
        if not self.muted:
            self._play_tone(880, 50)
        self._redraw(app)

    def _toggle_mute(self, app):
        """Toggle mute."""
        self.muted = not self.muted
        speaker = self._get_speaker()
        if speaker:
            speaker.setVolume(0 if self.muted else self.volume)
        print(f"[sound] Muted: {self.muted}")
        self._redraw(app)

    def _play_tone(self, freq, duration_ms):
        """Play a tone."""
        speaker = self._get_speaker()
        if speaker and not self.muted:
            try:
                speaker.tone(freq, duration_ms)
            except Exception as e:
                print(f"[sound] Tone failed: {e}")

    def _test_tone(self):
        """Play test tone."""
        print("[sound] Playing test tone")
        self._play_tone(440, 500)

    def _save(self, app):
        """Save volume to NVS."""
        try:
            import esp32
            nvs = esp32.NVS("settings")
            nvs.set_i32("volume", self.volume)
            nvs.commit()
            self.volume_saved = self.volume
            print(f"[sound] Volume saved: {self.volume}")
        except Exception as e:
            print(f"[sound] NVS save failed: {e}")
        self._redraw(app)

    def handle_key(self, app, key):
        """Handle key press."""
        from lib.keycode import KEY_NAV_LEFT, KEY_NAV_RIGHT

        if key == KEY_NAV_LEFT:
            self._adjust(app, -15)
            return True

        if key == KEY_NAV_RIGHT:
            self._adjust(app, 15)
            return True

        if key == ord("m") or key == ord("M"):
            self._toggle_mute(app)
            return True

        if key == ord("t") or key == ord("T"):
            self._test_tone()
            return True

        if key == ord("s") or key == ord("S"):
            self._save(app)
            return True

        return False
