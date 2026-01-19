"""
Keyboard Demo - Input Handling on M5Stack Cardputer ADV
========================================================

Deep dive into the Cardputer's keyboard system. Learn how to handle
keypresses, detect modifiers, and work with special keys.

CONCEPTS COVERED:
-----------------
1. Key Events - keycode, state, row, col, modifier_mask
2. Modifier Keys - CTRL, SHIFT, ALT, OPT detection
3. Special Keys - Arrow keys via FN combinations
4. Matrix Layout - Physical key positions (4 rows x 14 cols)

KEY EVENT PROPERTIES:
---------------------
    event.keycode       - ASCII code (0-127) or special code
    event.state         - True=pressed, False=released
    event.row           - Matrix row (0-3)
    event.col           - Matrix column (0-13)
    event.modifier_mask - Bitmask of active modifiers

MODIFIER MASK BITS:
-------------------
    0x01 = CTRL
    0x02 = SHIFT
    0x04 = ALT
    0x08 = OPT

COMMON KEY CODES:
-----------------
    0x1B (27)  = ESC
    0x0D (13)  = Enter
    0x08 (8)   = Backspace
    0x7F (127) = Delete (FN+Backspace)
    180-183    = Arrow keys (via FN)

FN KEY COMBINATIONS:
--------------------
    FN + ;  = UP    (181)
    FN + .  = DOWN  (182)
    FN + ,  = LEFT  (180)
    FN + /  = RIGHT (183)
    FN + BS = DEL   (127)

CONTROLS:
---------
- Press any key = See event data in real-time
- Enter = Advance to next section
- ESC = Exit to launcher
"""

import time

import M5
from M5 import Lcd, Widgets

SCREEN_W = 240
SCREEN_H = 135


class KeyboardDemo:
    def __init__(self, keyboard):
        self.kb = keyboard
        self.running = False

    def run(self):
        self.running = True
        exit_flag = False
        next_flag = False

        # Store last key event for display
        last_event = None

        # =====================================================================
        # KEYBOARD CALLBACK
        # =====================================================================
        # KeyEvent properties:
        #   event.keycode      - ASCII code of the key (0-255)
        #   event.state        - True=pressed, False=released
        #   event.row          - Matrix row (0-3)
        #   event.col          - Matrix column (0-13)
        #   event.modifier_mask - Bitmask of active modifiers

        def on_key(keyboard):
            nonlocal exit_flag, next_flag, last_event
            while keyboard._keyevents:
                event = keyboard._keyevents.pop(0)
                last_event = event

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

        print("Keyboard Demo - Enter=Next, ESC=Exit")

        # =====================================================================
        # DEMO 1: Key Event Inspector
        # =====================================================================
        # Shows real-time key event data as you press keys

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("1. Key Inspector")

        Lcd.setTextSize(1)
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 28)
        Lcd.print("Press any key to see event data")

        # Labels
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 45)
        Lcd.print("Keycode:")
        Lcd.setCursor(10, 57)
        Lcd.print("Char:")
        Lcd.setCursor(10, 69)
        Lcd.print("State:")
        Lcd.setCursor(10, 81)
        Lcd.print("Row,Col:")
        Lcd.setCursor(10, 93)
        Lcd.print("Mods:")

        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(0, SCREEN_H - 10)
        Lcd.print("Enter=Next  ESC=Exit")

        next_flag = False
        last_displayed = None

        while not exit_flag and not next_flag:
            M5.update()

            # Update display when new key event
            if last_event and last_event != last_displayed:
                last_displayed = last_event
                e = last_event

                Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)

                # Keycode (decimal and hex)
                Lcd.setCursor(80, 45)
                Lcd.print(f"{e.keycode:3} (0x{e.keycode:02X})  ")

                # Character (if printable)
                Lcd.setCursor(80, 57)
                if 0x20 <= e.keycode <= 0x7E:
                    Lcd.print(f"'{chr(e.keycode)}'       ")
                else:
                    # Special key names
                    names = {
                        0x1B: "ESC",
                        0x0D: "ENTER",
                        0x0A: "ENTER",
                        0x08: "BACKSPACE",
                        0x09: "TAB",
                        0x7F: "DEL",
                        180: "LEFT",
                        181: "UP",
                        182: "DOWN",
                        183: "RIGHT",
                    }
                    name = names.get(e.keycode, "???")
                    Lcd.print(f"<{name}>     ")

                # State
                Lcd.setCursor(80, 69)
                state_str = "PRESS  " if e.state else "RELEASE"
                Lcd.print(state_str)

                # Row, Col
                Lcd.setCursor(80, 81)
                Lcd.print(f"({e.row}, {e.col})    ")

                # Modifier mask
                Lcd.setCursor(80, 93)
                mods = []
                if e.modifier_mask & 0x01:
                    mods.append("CTRL")
                if e.modifier_mask & 0x02:
                    mods.append("SHIFT")
                if e.modifier_mask & 0x04:
                    mods.append("ALT")
                if e.modifier_mask & 0x08:
                    mods.append("OPT")
                mod_str = "+".join(mods) if mods else "none"
                Lcd.print(f"{mod_str:20}")

            time.sleep(0.02)

        if exit_flag:
            self.running = False
            return self

        # =====================================================================
        # DEMO 2: Modifier Keys
        # =====================================================================
        # Shows how to detect modifier key combinations

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("2. Modifiers")

        Lcd.setTextSize(1)
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 28)
        Lcd.print("Hold modifier + press a key")

        # Modifier reference
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 45)
        Lcd.print("modifier_mask bits:")
        Lcd.setCursor(10, 57)
        Lcd.print("0x01=CTRL  0x02=SHIFT")
        Lcd.setCursor(10, 69)
        Lcd.print("0x04=ALT   0x08=OPT")

        Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 88)
        Lcd.print("Active:")

        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(0, SCREEN_H - 10)
        Lcd.print("Enter=Next  ESC=Exit")

        next_flag = False
        last_displayed = None

        while not exit_flag and not next_flag:
            M5.update()

            if last_event and last_event != last_displayed:
                last_displayed = last_event
                e = last_event

                # Show active modifiers with visual indicators
                Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
                Lcd.setCursor(70, 88)

                parts = []
                if e.modifier_mask & 0x01:
                    parts.append("CTRL")
                if e.modifier_mask & 0x02:
                    parts.append("SHIFT")
                if e.modifier_mask & 0x04:
                    parts.append("ALT")
                if e.modifier_mask & 0x08:
                    parts.append("OPT")

                if parts:
                    Lcd.print(f"{'+'.join(parts):20}")
                else:
                    Lcd.print("(none)              ")

                # Show the key with modifiers
                Lcd.setCursor(10, 103)
                if 0x20 <= e.keycode <= 0x7E:
                    Lcd.print(f"Key: '{chr(e.keycode)}'  mask: 0x{e.modifier_mask:02X}  ")

            time.sleep(0.02)

        if exit_flag:
            self.running = False
            return self

        # =====================================================================
        # DEMO 3: Special Keys & FN Combinations
        # =====================================================================
        # Arrow keys, DEL, and other FN combinations

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("3. Special Keys")

        Lcd.setTextSize(1)
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 28)
        Lcd.print("FN key combinations:")

        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 43)
        Lcd.print("FN + ;  = UP    (181)")
        Lcd.setCursor(10, 55)
        Lcd.print("FN + .  = DOWN  (182)")
        Lcd.setCursor(10, 67)
        Lcd.print("FN + ,  = LEFT  (180)")
        Lcd.setCursor(10, 79)
        Lcd.print("FN + /  = RIGHT (183)")
        Lcd.setCursor(10, 91)
        Lcd.print("FN + BS = DEL   (127)")

        Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
        Lcd.setCursor(150, 43)
        Lcd.print("Try it!")

        Lcd.setCursor(10, 108)
        Lcd.print("Last:")

        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(0, SCREEN_H - 10)
        Lcd.print("Enter=Next  ESC=Exit")

        next_flag = False
        last_displayed = None

        while not exit_flag and not next_flag:
            M5.update()

            if last_event and last_event != last_displayed:
                last_displayed = last_event
                e = last_event

                Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
                Lcd.setCursor(50, 108)

                # Show arrow key names
                arrow_names = {180: "LEFT", 181: "UP", 182: "DOWN", 183: "RIGHT"}
                if e.keycode in arrow_names:
                    Lcd.print(f"{arrow_names[e.keycode]} ({e.keycode})    ")
                elif e.keycode == 0x7F:
                    Lcd.print(f"DEL ({e.keycode})        ")
                elif 0x20 <= e.keycode <= 0x7E:
                    Lcd.print(f"'{chr(e.keycode)}' ({e.keycode})       ")
                else:
                    Lcd.print(f"code {e.keycode}        ")

            time.sleep(0.02)

        if exit_flag:
            self.running = False
            return self

        # =====================================================================
        # DEMO 4: Keyboard Matrix Reference
        # =====================================================================
        # Shows the physical layout and matrix positions

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("4. Matrix Layout")

        Lcd.setTextSize(1)
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 28)
        Lcd.print("4 rows x 14 cols (0-indexed)")

        # Simplified layout
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 43)
        Lcd.print("R0: ` 1 2 3 4 5 6 7 8 9 0 - = BS")
        Lcd.setCursor(10, 55)
        Lcd.print("R1: TAB Q W E R T Y U I O P [ ]\\")
        Lcd.setCursor(10, 67)
        Lcd.print("R2: FN SH A S D F G H J K L ;'EN")
        Lcd.setCursor(10, 79)
        Lcd.print("R3: CT OP AL Z X C V B N M ,./ _")

        Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 96)
        Lcd.print("Press key to see (row,col)")

        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(0, SCREEN_H - 10)
        Lcd.print("Enter=Next  ESC=Exit")

        next_flag = False
        last_displayed = None

        while not exit_flag and not next_flag:
            M5.update()

            if last_event and last_event != last_displayed:
                last_displayed = last_event
                e = last_event

                Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
                Lcd.setCursor(10, 108)
                if 0x20 <= e.keycode <= 0x7E:
                    Lcd.print(f"'{chr(e.keycode)}' at ({e.row},{e.col})    ")
                else:
                    Lcd.print(f"0x{e.keycode:02X} at ({e.row},{e.col})   ")

            time.sleep(0.02)

        if exit_flag:
            self.running = False
            return self

        # =====================================================================
        # DEMO 5: API Reference
        # =====================================================================

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("5. API Reference")

        Lcd.setTextSize(1)
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        y = 28
        apis = [
            "kb.set_keyevent_callback(fn)",
            "event = kb._keyevents.pop(0)",
            "event.keycode  # ASCII code",
            "event.state    # True=press",
            "event.row, event.col  # matrix",
            "event.modifier_mask  # mods",
        ]
        for api in apis:
            Lcd.setCursor(10, y)
            Lcd.print(api)
            y += 12

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
        Lcd.print("See demo_keyboard.py for code")

        wait_for_key()

        self.running = False
        print("Keyboard Demo exited")
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

    KeyboardDemo(kb).run()
