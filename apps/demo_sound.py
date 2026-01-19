"""
Sound Demo - Audio Output on M5Stack Cardputer
==============================================

Learn how to generate sounds on the Cardputer using the built-in speaker.
Great for audio feedback, alerts, and simple music.

CONCEPTS COVERED:
-----------------
1. Basic Tones - Speaker.tone(frequency_hz, duration_ms)
2. Musical Notes - Frequency values for musical scale
3. Volume Control - setVolume(0-255)
4. Sound Effects - Combining tones for beeps, sweeps, alerts
5. Frequency Sweep - Smooth tone transitions

COMMON NOTE FREQUENCIES (Hz):
-----------------------------
    C4=262  D4=294  E4=330  F4=349
    G4=392  A4=440  B4=494  C5=523

SPEAKER API QUICK REFERENCE:
----------------------------
    Speaker.tone(freq, duration_ms)  # Play tone
    Speaker.setVolume(0-255)         # Set volume
    Speaker.getVolume()              # Get current volume
    Speaker.isPlaying()              # Check if playing
    Speaker.stop()                   # Stop playback
    Speaker.playWavFile(path)        # Play WAV file

VOLUME CONVERSION:
------------------
To convert percentage to 0-255:
    volume = int(percentage * 255 / 100)

CONTROLS:
---------
- Enter = Advance to next section
- ESC = Exit to launcher
"""

import time

import M5
from M5 import Lcd, Speaker, Widgets

SCREEN_W = 240
SCREEN_H = 135


class SoundDemo:
    def __init__(self, keyboard):
        self.kb = keyboard
        self.running = False

    def run(self):
        self.running = True
        exit_flag = False
        next_flag = False

        def on_key(keyboard):
            nonlocal exit_flag, next_flag
            while keyboard._keyevents:
                event = keyboard._keyevents.pop(0)
                key = event.keycode
                if key == 0x1B:  # ESC
                    exit_flag = True
                elif key == 0x0D or key == 0x0A:  # Enter/OK
                    next_flag = True

        self.kb.set_keyevent_callback(on_key)

        def wait_for_key():
            nonlocal next_flag, exit_flag
            next_flag = False
            Lcd.setFont(Widgets.FONTS.ASCII7)
            Lcd.setTextSize(1)
            Lcd.setTextColor(0x07E0, 0x0000)
            Lcd.setCursor(0, SCREEN_H - 10)
            Lcd.print("Enter=Next  ESC=Exit")
            while not next_flag and not exit_flag:
                M5.update()
                time.sleep(0.01)
            return not exit_flag

        print("Sound Demo - Enter=Next, ESC=Exit")

        # Initialize speaker
        # Speaker.begin() is usually called by M5.begin()
        Speaker.setVolume(191)  # 75% volume (0-255)

        # =====================================================================
        # DEMO 1: Basic Tone
        # =====================================================================
        # Speaker.tone(frequency_hz, duration_ms)
        # Plays a square wave tone at the given frequency

        Lcd.fillScreen(0x0000)
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(2)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 10)
        Lcd.print("1. Basic Tone")

        Lcd.setTextSize(1)
        Lcd.setTextColor(0x07FF, 0x0000)
        Lcd.setCursor(10, 40)
        Lcd.print("Speaker.tone(freq, duration_ms)")
        Lcd.setCursor(10, 55)
        Lcd.print("Playing 440Hz (A4) for 500ms...")

        # Play A4 (440 Hz) for 500ms
        Speaker.tone(440, 500)

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 2: Musical Scale
        # =====================================================================
        # Common note frequencies (Hz):
        #   C4=262, D4=294, E4=330, F4=349, G4=392, A4=440, B4=494, C5=523

        Lcd.fillScreen(0x0000)
        Lcd.setTextSize(2)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 10)
        Lcd.print("2. Musical Scale")

        Lcd.setTextSize(1)
        Lcd.setTextColor(0x07FF, 0x0000)
        Lcd.setCursor(10, 40)
        Lcd.print("C4  D4  E4  F4  G4  A4  B4  C5")
        Lcd.setCursor(10, 55)
        Lcd.print("262 294 330 349 392 440 494 523")

        notes = [262, 294, 330, 349, 392, 440, 494, 523]
        note_names = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]

        for i, (freq, name) in enumerate(zip(notes, note_names)):
            # Highlight current note
            Lcd.setTextColor(0xFFE0, 0x0000)
            Lcd.setCursor(10 + i * 28, 75)
            Lcd.print(name)
            Speaker.tone(freq, 200)
            time.sleep(0.25)
            # Unhighlight
            Lcd.setTextColor(0x07FF, 0x0000)
            Lcd.setCursor(10 + i * 28, 75)
            Lcd.print(name)

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 3: Volume Control
        # =====================================================================
        # Speaker.setVolume(0-255) - set volume by raw value
        # Speaker.setVolumePercentage(0-100) - set by percentage (built-in)
        # Speaker.getVolume() - get current volume (0-255)

        # Helper function: convert percentage to 0-255 value
        def vol_pct(percent):
            return int(percent * 255 / 100)

        Lcd.fillScreen(0x0000)
        Lcd.setTextSize(2)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 10)
        Lcd.print("3. Volume")

        Lcd.setTextSize(1)
        Lcd.setTextColor(0x07FF, 0x0000)
        Lcd.setCursor(10, 40)
        Lcd.print("vol = int(pct * 255 / 100)")

        # Demo various volume levels
        percentages = [10, 25, 50, 75, 100]
        for pct in percentages:
            vol = vol_pct(pct)
            Speaker.setVolume(vol)
            Lcd.setTextColor(0xFFE0, 0x0000)
            Lcd.setCursor(10, 60)
            Lcd.print(f"{pct:3}% = {vol:3}  ")
            Speaker.tone(440, 250)
            time.sleep(0.4)

        Speaker.setVolume(vol_pct(75))  # Reset to 75%

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 4: Sound Effects
        # =====================================================================
        # Combine tones to create simple sound effects

        Lcd.fillScreen(0x0000)
        Lcd.setTextSize(2)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 10)
        Lcd.print("4. Sound Effects")

        Lcd.setTextSize(1)
        Lcd.setTextColor(0x07FF, 0x0000)

        # Beep
        Lcd.setCursor(10, 40)
        Lcd.print("Beep...")
        Speaker.tone(1000, 100)
        time.sleep(0.3)

        # Rising sweep
        Lcd.setCursor(10, 55)
        Lcd.print("Rising sweep...")
        for freq in range(200, 1000, 50):
            Speaker.tone(freq, 30)
            time.sleep(0.03)
        time.sleep(0.2)

        # Falling sweep
        Lcd.setCursor(10, 70)
        Lcd.print("Falling sweep...")
        for freq in range(1000, 200, -50):
            Speaker.tone(freq, 30)
            time.sleep(0.03)
        time.sleep(0.2)

        # Alert (two-tone)
        Lcd.setCursor(10, 85)
        Lcd.print("Alert...")
        for _ in range(3):
            Speaker.tone(800, 100)
            time.sleep(0.15)
            Speaker.tone(600, 100)
            time.sleep(0.15)

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 5: Frequency Sweep
        # =====================================================================
        # Continuous sweep through the full frequency range

        Lcd.fillScreen(0x0000)
        Lcd.setTextSize(2)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 5)
        Lcd.print("5. Freq Sweep")

        Lcd.setTextSize(1)
        Lcd.setTextColor(0x07FF, 0x0000)

        # Sweep up
        Lcd.setCursor(10, 35)
        Lcd.print("Sweep UP: 100Hz -> 8000Hz")

        for freq in range(100, 8000, 100):
            # Draw frequency bar
            bar_x = int((freq - 100) / 7900 * 200)
            Lcd.fillRect(20, 55, bar_x, 10, 0x07E0)
            Lcd.fillRect(20 + bar_x, 55, 200 - bar_x, 10, 0x0000)
            Lcd.setCursor(20, 70)
            Lcd.print(f"{freq:5}Hz")
            Speaker.tone(freq, 15)
            time.sleep(0.015)

        time.sleep(0.3)

        # Sweep down
        Lcd.setCursor(10, 85)
        Lcd.print("Sweep DOWN: 8000Hz -> 100Hz")

        for freq in range(8000, 100, -100):
            bar_x = int((freq - 100) / 7900 * 200)
            Lcd.fillRect(20, 100, bar_x, 10, 0xF800)
            Lcd.fillRect(20 + bar_x, 100, 200 - bar_x, 10, 0x0000)
            Lcd.setCursor(20, 115)
            Lcd.print(f"{freq:5}Hz")
            Speaker.tone(freq, 15)
            time.sleep(0.015)

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 6: API Reference
        # =====================================================================
        Lcd.fillScreen(0x0000)
        Lcd.setTextSize(2)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 5)
        Lcd.print("5. API Reference")

        Lcd.setTextSize(1)
        Lcd.setTextColor(0x07FF, 0x0000)
        y = 28
        apis = [
            "tone(freq, ms)",
            "setVolume(0-255)",
            "getVolume()",
            "isPlaying()",
            "stop()",
            "playWavFile(path)",
        ]
        for api in apis:
            Lcd.setCursor(10, y)
            Lcd.print(f"Speaker.{api}")
            y += 12

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DONE
        # =====================================================================
        Lcd.fillScreen(0x0000)
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(0x07E0, 0x0000)
        Lcd.drawCenterString("Demo Complete!", 120, 50)

        # Victory jingle
        Speaker.tone(523, 100)  # C5
        time.sleep(0.1)
        Speaker.tone(659, 100)  # E5
        time.sleep(0.1)
        Speaker.tone(784, 200)  # G5
        time.sleep(0.2)

        wait_for_key()

        self.running = False
        print("Sound Demo exited")
        return self


if __name__ == "__main__":
    import M5
    import machine
    from hardware import KeyboardI2C
    from M5 import Lcd

    M5.begin()
    Lcd.setRotation(1)
    Lcd.setBrightness(40)

    i2c1 = machine.I2C(1, scl=machine.Pin(9), sda=machine.Pin(8), freq=400000)
    intr_pin = machine.Pin(11, mode=machine.Pin.IN, pull=None)
    kb = KeyboardI2C(i2c1, intr_pin=intr_pin, mode=KeyboardI2C.ASCII_MODE)

    SoundDemo(kb).run()
