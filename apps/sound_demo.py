"""
Sound Demo - Interactive Audio Synthesizer
===========================================

Demonstrates the Speaker hardware on M5Stack Cardputer with real-time
keyboard control. Learn how to generate tones, control volume, and
create sound effects.

SPEAKER API SUMMARY:
--------------------
    Speaker.tone(freq_hz, duration_ms)  # Play square wave tone
    Speaker.setVolume(0-255)            # Set volume (0=mute, 255=max)
    Speaker.getVolume()                 # Get current volume
    Speaker.stop()                      # Stop current playback
    Speaker.isPlaying()                 # Check if audio is playing

MUSICAL NOTE FREQUENCIES (Hz):
------------------------------
    C4=262  D4=294  E4=330  F4=349  G4=392  A4=440  B4=494  C5=523
    C5=523  D5=587  E5=659  F5=698  G5=784  A5=880  B5=988  C6=1047

CONTROLS:
---------
    Number keys (1-8) = Play musical notes C4 to C5
    +/= = Increase volume
    -   = Decrease volume
    S   = Play scale demo
    E   = Play sound effects demo
    ESC = Exit to launcher
"""

import asyncio
import sys

# Ensure lib is in path for imports
for path in ["/flash", "/remote"]:
    if path not in sys.path:
        sys.path.insert(0, path)

from M5 import Lcd, Speaker, Widgets

from lib.app_base import AppBase
from lib.keycode import KeyCode

# Screen dimensions
SCREEN_W = 240
SCREEN_H = 135

# Musical notes - C major scale from C4 to C5
NOTES = {
    ord("1"): ("C4", 262),
    ord("2"): ("D4", 294),
    ord("3"): ("E4", 330),
    ord("4"): ("F4", 349),
    ord("5"): ("G4", 392),
    ord("6"): ("A4", 440),
    ord("7"): ("B4", 494),
    ord("8"): ("C5", 523),
}

# Volume step for adjustments
VOLUME_STEP = 25


class SoundDemo(AppBase):
    """Interactive sound demo with keyboard-controlled tone generation."""

    def __init__(self):
        super().__init__()
        self.name = "Sound Demo"
        self._volume = 128  # Start at 50% volume
        self._current_note = None
        self._playing_demo = False

    def on_launch(self):
        """Initialize speaker volume."""
        Speaker.setVolume(self._volume)

    def on_view(self):
        """Draw the sound demo interface."""
        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.ASCII7)

        # Title
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("Sound Demo")

        # Instructions
        Lcd.setTextSize(1)
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 28)
        Lcd.print("Keys 1-8: Play notes C4-C5")

        # Note display area
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 43)
        Lcd.print("1  2  3  4  5  6  7  8")
        Lcd.setCursor(10, 53)
        Lcd.print("C4 D4 E4 F4 G4 A4 B4 C5")

        # Volume display
        self._draw_volume()

        # Controls hint
        Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 95)
        Lcd.print("+/- Volume  S=Scale  E=Effects")

        # Footer
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(0, SCREEN_H - 12)
        Lcd.print("ESC=Exit")

    def _draw_volume(self):
        """Draw volume bar and percentage."""
        # Volume label
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 70)
        Lcd.print("Volume:")

        # Volume bar background
        bar_x, bar_y, bar_w, bar_h = 60, 68, 120, 12
        Lcd.drawRect(bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2, Lcd.COLOR.WHITE)

        # Volume bar fill
        fill_w = int(self._volume / 255 * bar_w)
        Lcd.fillRect(bar_x, bar_y, fill_w, bar_h, Lcd.COLOR.GREEN)
        Lcd.fillRect(bar_x + fill_w, bar_y, bar_w - fill_w, bar_h, Lcd.COLOR.BLACK)

        # Percentage
        pct = int(self._volume / 255 * 100)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(190, 70)
        Lcd.print(f"{pct:3}%")

    def _highlight_note(self, note_name):
        """Highlight the currently playing note."""
        # Map note names to x positions
        # ASCII7 font at size 1 = 6 pixels per character
        # String "C4 D4 E4..." has notes at 3-char intervals (note + space)
        # Base x=10, each note is 3*6=18 pixels apart
        char_width = 6
        base_x = 10
        note_positions = {
            "C4": base_x + 0 * 3 * char_width,   # 10
            "D4": base_x + 1 * 3 * char_width,   # 28
            "E4": base_x + 2 * 3 * char_width,   # 46
            "F4": base_x + 3 * 3 * char_width,   # 64
            "G4": base_x + 4 * 3 * char_width,   # 82
            "A4": base_x + 5 * 3 * char_width,   # 100
            "B4": base_x + 6 * 3 * char_width,   # 118
            "C5": base_x + 7 * 3 * char_width,   # 136
        }

        # Clear previous highlight
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 53)
        Lcd.print("C4 D4 E4 F4 G4 A4 B4 C5")

        # Highlight current note
        if note_name in note_positions:
            x = note_positions[note_name]
            Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
            Lcd.setCursor(x, 53)
            Lcd.print(note_name)

    async def _play_scale(self):
        """Play ascending and descending scale."""
        self._playing_demo = True

        # Ascending
        for key in [ord("1"), ord("2"), ord("3"), ord("4"), ord("5"), ord("6"), ord("7"), ord("8")]:
            if not self._playing_demo:
                break
            note_name, freq = NOTES[key]
            self._highlight_note(note_name)
            Speaker.tone(freq, 200)
            await asyncio.sleep_ms(250)

        # Descending
        for key in [ord("7"), ord("6"), ord("5"), ord("4"), ord("3"), ord("2"), ord("1")]:
            if not self._playing_demo:
                break
            note_name, freq = NOTES[key]
            self._highlight_note(note_name)
            Speaker.tone(freq, 200)
            await asyncio.sleep_ms(250)

        self._highlight_note("")
        self._playing_demo = False

    async def _play_effects(self):
        """Play various sound effects."""
        self._playing_demo = True

        # Show effect name
        def show_effect(name):
            Lcd.setTextColor(Lcd.COLOR.MAGENTA, Lcd.COLOR.BLACK)
            Lcd.setCursor(10, 53)
            Lcd.print(f"Effect: {name:<20}")

        # Rising sweep
        show_effect("Rising sweep")
        for freq in range(200, 1000, 50):
            if not self._playing_demo:
                break
            Speaker.tone(freq, 30)
            await asyncio.sleep_ms(30)

        await asyncio.sleep_ms(200)

        # Falling sweep
        show_effect("Falling sweep")
        for freq in range(1000, 200, -50):
            if not self._playing_demo:
                break
            Speaker.tone(freq, 30)
            await asyncio.sleep_ms(30)

        await asyncio.sleep_ms(200)

        # Alert beeps
        show_effect("Alert beeps")
        for _ in range(3):
            if not self._playing_demo:
                break
            Speaker.tone(800, 100)
            await asyncio.sleep_ms(150)
            Speaker.tone(600, 100)
            await asyncio.sleep_ms(150)

        await asyncio.sleep_ms(200)

        # Victory jingle
        show_effect("Victory jingle")
        jingle = [(523, 100), (659, 100), (784, 200)]
        for freq, dur in jingle:
            if not self._playing_demo:
                break
            Speaker.tone(freq, dur)
            await asyncio.sleep_ms(dur + 50)

        # Restore display
        self.on_view()
        self._playing_demo = False

    async def _kb_event_handler(self, event, fw):
        """Handle keyboard events for sound control."""
        key = event.key

        # Don't handle ESC - let framework handle it
        if key == KeyCode.KEYCODE_ESC:
            self._playing_demo = False  # Stop any demo
            return

        # Play notes with number keys
        if key in NOTES:
            note_name, freq = NOTES[key]
            self._highlight_note(note_name)
            Speaker.tone(freq, 300)
            event.status = True
            return

        # Volume up
        if key == ord("+") or key == ord("="):
            self._volume = min(255, self._volume + VOLUME_STEP)
            Speaker.setVolume(self._volume)
            self._draw_volume()
            Speaker.tone(440, 50)  # Feedback beep
            event.status = True
            return

        # Volume down
        if key == ord("-"):
            self._volume = max(0, self._volume - VOLUME_STEP)
            Speaker.setVolume(self._volume)
            self._draw_volume()
            Speaker.tone(440, 50)  # Feedback beep
            event.status = True
            return

        # Scale demo
        if key == ord("s") or key == ord("S"):
            if not self._playing_demo:
                asyncio.create_task(self._play_scale())
            event.status = True
            return

        # Effects demo
        if key == ord("e") or key == ord("E"):
            if not self._playing_demo:
                asyncio.create_task(self._play_effects())
            event.status = True
            return

        event.status = True

    async def on_run(self):
        """Background task - not much needed here."""
        while True:
            await asyncio.sleep_ms(100)


# Export the App class for framework discovery
App = SoundDemo

if __name__ == "__main__":
    import M5

    M5.begin()
    Lcd.setRotation(1)
    Lcd.setBrightness(40)

    from lib.framework import Framework

    fw = Framework()
    fw.install(SoundDemo())
    fw.start()
