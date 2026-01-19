import time

import M5
from M5 import Lcd, Widgets

# Screen dimensions (landscape) - ASCII7 at size 2
SCREEN_W = 240
SCREEN_H = 135
CHAR_W = 12  # 6 * 2
CHAR_H = 18  # 9 * 2
COLS = SCREEN_W // CHAR_W  # 20 chars
ROWS = SCREEN_H // CHAR_H  # 7 rows


class Notepad:
    def __init__(self, keyboard):
        self.kb = keyboard
        self.lines = [""]
        self.cursor_row = 0
        self.cursor_col = 0
        self.running = False
        self.first_key = True

    def flash_edge(self):
        # Flash right edge red
        Lcd.fillRect(SCREEN_W - 4, 0, 4, SCREEN_H, 0xFF0000)
        time.sleep_ms(100)
        Lcd.fillRect(SCREEN_W - 4, 0, 4, SCREEN_H, 0x000000)

    def draw_cursor(self):
        # Draw underscore cursor
        x = self.cursor_col * CHAR_W
        y = self.cursor_row * CHAR_H + CHAR_H - 2
        Lcd.fillRect(x, y, CHAR_W, 2, 0xFFFFFF)

    def clear_cursor(self):
        # Clear cursor
        x = self.cursor_col * CHAR_W
        y = self.cursor_row * CHAR_H + CHAR_H - 2
        Lcd.fillRect(x, y, CHAR_W, 2, 0x000000)

    def redraw(self):
        Lcd.fillScreen(0x000000)
        for i, line in enumerate(self.lines):
            if i >= ROWS:
                break
            Lcd.setCursor(0, i * CHAR_H)
            Lcd.print(line[:COLS])
        self.draw_cursor()

    def on_key(self, keyboard):
        while keyboard._keyevents:
            event = keyboard._keyevents.pop(0)
            key = event.keycode

            # Skip modifier keys and zero
            if key == 0 or key > 127:
                continue

            # ESC to exit
            if key == 0x1B:
                self.running = False
                return

            # Clear help text on first keypress
            if self.first_key:
                self.first_key = False
                Lcd.fillScreen(0x000000)
                self.draw_cursor()

            if key == 0x0D or key == 0x0A:  # Enter
                current = self.lines[self.cursor_row]
                self.lines[self.cursor_row] = current[: self.cursor_col]
                self.lines.insert(self.cursor_row + 1, current[self.cursor_col :])
                self.cursor_row += 1
                self.cursor_col = 0
                self.redraw()
            elif key == 0x08:  # Backspace
                if self.cursor_col > 0:
                    current = self.lines[self.cursor_row]
                    self.lines[self.cursor_row] = (
                        current[: self.cursor_col - 1] + current[self.cursor_col :]
                    )
                    self.cursor_col -= 1
                    self.redraw()
                elif self.cursor_row > 0:
                    prev_len = len(self.lines[self.cursor_row - 1])
                    self.lines[self.cursor_row - 1] += self.lines[self.cursor_row]
                    self.lines.pop(self.cursor_row)
                    self.cursor_row -= 1
                    self.cursor_col = prev_len
                    self.redraw()
            elif 0x20 <= key <= 0x7E:  # Printable ASCII
                # Check if at edge
                if self.cursor_col >= COLS:
                    self.flash_edge()
                    continue
                self.clear_cursor()
                char = chr(key)
                current = self.lines[self.cursor_row]
                self.lines[self.cursor_row] = (
                    current[: self.cursor_col] + char + current[self.cursor_col :]
                )
                Lcd.setCursor(self.cursor_col * CHAR_W, self.cursor_row * CHAR_H)
                Lcd.print(char)
                self.cursor_col += 1
                self.draw_cursor()

    def run(self):
        self.running = True
        self.first_key = True
        self.kb.set_keyevent_callback(self.on_key)
        Lcd.fillScreen(0x000000)
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(2)
        Lcd.setTextColor(0xFFFFFF, 0x000000)
        Lcd.setCursor(0, 0)
        Lcd.print("ESC=exit")
        print("Notepad started. ESC to exit.")

        while self.running:
            M5.update()
            time.sleep(0.01)

        print("Notepad exited")
        return self
