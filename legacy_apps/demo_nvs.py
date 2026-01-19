"""
NVS Demo - Non-Volatile Storage on ESP32
=========================================

Learn to use NVS (Non-Volatile Storage) - a persistent key-value store
built into the ESP32. Data survives reboots and power cycles!

CONCEPTS COVERED:
-----------------
1. What is NVS - Key-value store in flash memory
2. Basic API - Reading and writing values
3. Namespaces - Organizing data by app
4. Data Types - u8, i32, str, blob
5. UIFlow Settings - Understanding system namespaces

NVS API QUICK REFERENCE:
------------------------
    import esp32
    nvs = esp32.NVS('namespace_name')

    # Read values (raises OSError if key doesn't exist)
    val = nvs.get_u8('key')     # Unsigned 8-bit (0-255)
    val = nvs.get_i32('key')    # Signed 32-bit integer
    val = nvs.get_str('key')    # String

    # Write values (MUST call commit() after!)
    nvs.set_u8('key', value)
    nvs.set_i32('key', value)
    nvs.set_str('key', value)
    nvs.commit()  # Actually saves to flash!

IMPORTANT: Always call nvs.commit() after writes, or data won't be saved!

COMMON NAMESPACES:
------------------
- 'uiflow': UIFlow2 system settings (boot_option, brightness, wifi, etc.)
- 'nvs': System defaults
- Your own: Any string up to 15 characters

UIFLOW boot_option VALUES:
--------------------------
- 0: Run /flash/main.py directly (best for development)
- 1: Show built-in launcher menu
- 2: Network setup only

USE CASES:
----------
- Save user settings (brightness, preferences)
- Store high scores
- Remember WiFi credentials
- Save app state between sessions

CONTROLS:
---------
- Enter = Advance to next section
- ESC = Exit to launcher
"""

import time

import esp32
import M5
from M5 import Lcd, Widgets

SCREEN_W = 240
SCREEN_H = 135


class NvsDemo:
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
                if event.keycode == 0x1B:  # ESC
                    exit_flag = True
                elif event.keycode == 0x0D or event.keycode == 0x0A:  # Enter
                    next_flag = True

        self.kb.set_keyevent_callback(on_key)

        def wait_for_key():
            nonlocal next_flag, exit_flag
            next_flag = False
            Lcd.setFont(Widgets.FONTS.ASCII7)
            Lcd.setTextSize(1)
            Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
            Lcd.setCursor(0, SCREEN_H - 10)
            Lcd.print("Enter=Next  ESC=Exit")
            while not next_flag and not exit_flag:
                M5.update()
                time.sleep(0.01)
            return not exit_flag

        print("NVS Demo - Enter=Next, ESC=Exit")

        # =====================================================================
        # DEMO 1: What is NVS?
        # =====================================================================

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("1. What is NVS?")

        Lcd.setFont(Widgets.FONTS.DejaVu12)
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 30)
        Lcd.print("Non-Volatile Storage")

        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
        y = 50
        info = [
            "- Key-value store in flash",
            "- Survives reboots & power off",
            "- Organized by 'namespace'",
            "- Types: u8, i32, str, blob",
            "- Used for settings, WiFi, etc",
        ]
        for line in info:
            Lcd.setCursor(10, y)
            Lcd.print(line)
            y += 12

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 2: Basic API
        # =====================================================================

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("2. NVS API")

        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        y = 28
        code = [
            "import esp32",
            "nvs = esp32.NVS('uiflow')",
            "",
            "# Read",
            "nvs.get_u8('key')    # 0-255",
            "nvs.get_i32('key')   # signed int",
            "nvs.get_str('key')   # string",
            "",
            "# Write (must commit!)",
            "nvs.set_u8('key', 42)",
            "nvs.commit()",
        ]
        for line in code:
            Lcd.setCursor(10, y)
            Lcd.print(line)
            y += 10

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 3: UIFlow NVS Dump
        # =====================================================================
        # Read known UIFlow keys from NVS

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("3. UIFlow NVS")

        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(1)

        nvs = esp32.NVS("uiflow")

        # Known UIFlow keys
        y = 28
        keys_u8 = ["boot_option", "brightness", "boot_screen", "comlink"]
        keys_str = ["ssid0", "server", "tz"]

        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, y)
        Lcd.print("Namespace: 'uiflow'")
        y += 14

        for key in keys_u8:
            try:
                val = nvs.get_u8(key)
                Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
                Lcd.setCursor(10, y)
                Lcd.print(f"{key}: {val}")
            except OSError:
                Lcd.setTextColor(Lcd.COLOR.LIGHTGREY, Lcd.COLOR.BLACK)
                Lcd.setCursor(10, y)
                Lcd.print(f"{key}: (not set)")
            y += 11

        for key in keys_str:
            try:
                val = nvs.get_str(key)
                # Truncate long values
                if len(val) > 15:
                    val = val[:12] + "..."
                Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
                Lcd.setCursor(10, y)
                Lcd.print(f"{key}: '{val}'")
            except OSError:
                Lcd.setTextColor(Lcd.COLOR.LIGHTGREY, Lcd.COLOR.BLACK)
                Lcd.setCursor(10, y)
                Lcd.print(f"{key}: (not set)")
            y += 11

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 4: Boot Option Explained
        # =====================================================================

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("4. boot_option")

        # Get current value
        try:
            boot_opt = nvs.get_u8("boot_option")
        except OSError:
            boot_opt = None

        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 28)
        if boot_opt is not None:
            Lcd.print(f"Current value: {boot_opt}")
        else:
            Lcd.print("Current value: (not set)")

        Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
        y = 45
        opts = [
            "0 = Run /flash/main.py directly",
            "1 = Show startup menu (default)",
            "2 = Network setup only",
            "",
            "To restore launcher:",
            "  nvs.set_u8('boot_option', 1)",
            "  nvs.commit()",
        ]
        for line in opts:
            Lcd.setCursor(10, y)
            Lcd.print(line)
            y += 11

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 5: Other Namespaces
        # =====================================================================

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("5. Namespaces")

        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        y = 28
        info = [
            "NVS uses namespaces to organize",
            "data from different apps:",
            "",
            "'uiflow'  - UIFlow settings",
            "'nvs'     - System defaults",
            "'myapp'   - Your own namespace!",
            "",
            "nvs = esp32.NVS('myapp')",
            "nvs.set_str('name', 'value')",
            "nvs.commit()",
        ]
        for line in info:
            Lcd.setTextColor(
                Lcd.COLOR.YELLOW if line.startswith("'") else Lcd.COLOR.CYAN, Lcd.COLOR.BLACK
            )
            Lcd.setCursor(10, y)
            Lcd.print(line)
            y += 11

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 6: Try It - Write & Read
        # =====================================================================

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("6. Try It!")

        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 28)
        Lcd.print("Writing to 'demo' namespace...")

        # Create our own namespace
        demo_nvs = esp32.NVS("demo")

        # Write a test value
        test_val = time.ticks_ms() % 256
        demo_nvs.set_u8("test_num", test_val)
        demo_nvs.set_str("test_str", "Hello NVS!")
        demo_nvs.commit()

        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 45)
        Lcd.print(f"Wrote test_num: {test_val}")
        Lcd.setCursor(10, 57)
        Lcd.print("Wrote test_str: 'Hello NVS!'")

        # Read it back
        Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 75)
        Lcd.print("Reading back...")

        read_num = demo_nvs.get_u8("test_num")
        read_str = demo_nvs.get_str("test_str")

        Lcd.setCursor(10, 87)
        Lcd.print(f"Read test_num: {read_num}")
        Lcd.setCursor(10, 99)
        Lcd.print(f"Read test_str: '{read_str}'")

        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 115)
        Lcd.print("Persists after reboot!")

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DONE
        # =====================================================================

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.drawCenterString("Demo Complete!", 120, 50)

        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(20, 80)
        Lcd.print("See demo_nvs.py for code")

        wait_for_key()

        self.running = False
        print("NVS Demo exited")
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

    NvsDemo(kb).run()
