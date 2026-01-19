# NVS Demo - Non-Volatile Storage on ESP32
# NVS is a key-value store that persists across reboots
# Press Enter to advance sections, ESC to exit

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
            Lcd.setTextColor(0x07E0, 0x0000)
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

        Lcd.fillScreen(0x0000)
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 5)
        Lcd.print("1. What is NVS?")

        Lcd.setFont(Widgets.FONTS.DejaVu12)
        Lcd.setTextColor(0x07FF, 0x0000)
        Lcd.setCursor(10, 30)
        Lcd.print("Non-Volatile Storage")

        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextColor(0xFFE0, 0x0000)
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

        Lcd.fillScreen(0x0000)
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 5)
        Lcd.print("2. NVS API")

        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextColor(0x07FF, 0x0000)
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

        Lcd.fillScreen(0x0000)
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 5)
        Lcd.print("3. UIFlow NVS")

        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(1)

        nvs = esp32.NVS("uiflow")

        # Known UIFlow keys
        y = 28
        keys_u8 = ["boot_option", "brightness", "boot_screen", "comlink"]
        keys_str = ["ssid0", "server", "tz"]

        Lcd.setTextColor(0x07FF, 0x0000)
        Lcd.setCursor(10, y)
        Lcd.print("Namespace: 'uiflow'")
        y += 14

        for key in keys_u8:
            try:
                val = nvs.get_u8(key)
                Lcd.setTextColor(0x07E0, 0x0000)
                Lcd.setCursor(10, y)
                Lcd.print(f"{key}: {val}")
            except OSError:
                Lcd.setTextColor(0x7BEF, 0x0000)
                Lcd.setCursor(10, y)
                Lcd.print(f"{key}: (not set)")
            y += 11

        for key in keys_str:
            try:
                val = nvs.get_str(key)
                # Truncate long values
                if len(val) > 15:
                    val = val[:12] + "..."
                Lcd.setTextColor(0xFFE0, 0x0000)
                Lcd.setCursor(10, y)
                Lcd.print(f"{key}: '{val}'")
            except OSError:
                Lcd.setTextColor(0x7BEF, 0x0000)
                Lcd.setCursor(10, y)
                Lcd.print(f"{key}: (not set)")
            y += 11

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 4: Boot Option Explained
        # =====================================================================

        Lcd.fillScreen(0x0000)
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 5)
        Lcd.print("4. boot_option")

        # Get current value
        try:
            boot_opt = nvs.get_u8("boot_option")
        except OSError:
            boot_opt = None

        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextColor(0x07FF, 0x0000)
        Lcd.setCursor(10, 28)
        if boot_opt is not None:
            Lcd.print(f"Current value: {boot_opt}")
        else:
            Lcd.print("Current value: (not set)")

        Lcd.setTextColor(0xFFE0, 0x0000)
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

        Lcd.fillScreen(0x0000)
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 5)
        Lcd.print("5. Namespaces")

        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextColor(0x07FF, 0x0000)
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
            Lcd.setTextColor(0xFFE0 if line.startswith("'") else 0x07FF, 0x0000)
            Lcd.setCursor(10, y)
            Lcd.print(line)
            y += 11

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 6: Try It - Write & Read
        # =====================================================================

        Lcd.fillScreen(0x0000)
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 5)
        Lcd.print("6. Try It!")

        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextColor(0x07FF, 0x0000)
        Lcd.setCursor(10, 28)
        Lcd.print("Writing to 'demo' namespace...")

        # Create our own namespace
        demo_nvs = esp32.NVS("demo")

        # Write a test value
        test_val = time.ticks_ms() % 256
        demo_nvs.set_u8("test_num", test_val)
        demo_nvs.set_str("test_str", "Hello NVS!")
        demo_nvs.commit()

        Lcd.setTextColor(0x07E0, 0x0000)
        Lcd.setCursor(10, 45)
        Lcd.print(f"Wrote test_num: {test_val}")
        Lcd.setCursor(10, 57)
        Lcd.print("Wrote test_str: 'Hello NVS!'")

        # Read it back
        Lcd.setTextColor(0xFFE0, 0x0000)
        Lcd.setCursor(10, 75)
        Lcd.print("Reading back...")

        read_num = demo_nvs.get_u8("test_num")
        read_str = demo_nvs.get_str("test_str")

        Lcd.setCursor(10, 87)
        Lcd.print(f"Read test_num: {read_num}")
        Lcd.setCursor(10, 99)
        Lcd.print(f"Read test_str: '{read_str}'")

        Lcd.setTextColor(0x07E0, 0x0000)
        Lcd.setCursor(10, 115)
        Lcd.print("Persists after reboot!")

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

        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(20, 80)
        Lcd.print("See demo_nvs.py for code")

        wait_for_key()

        self.running = False
        print("NVS Demo exited")
        return self
