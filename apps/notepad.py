"""
Notepad - Simple Text Editor for Cardputer ADV
===============================================

A minimal text editor that demonstrates real-world input handling patterns.
Type text, use backspace, and press Enter for new lines.

CONCEPTS COVERED:
-----------------
1. Character Input Handling - Processing printable ASCII
2. Text Buffer Management - Storing and editing multi-line text
3. Cursor Tracking - Row and column position
4. Incremental Redraw - Efficient screen updates
5. Edge Detection - Visual feedback for screen boundaries

WHY THIS MATTERS:
-----------------
Text editors are a great learning project because they combine:
- Input handling (every keypress matters)
- State management (cursor position, text content)
- Visual feedback (cursor, text display)
- Edge cases (what happens at line boundaries?)

CONTROLS:
---------
- Any printable key = Insert character
- Enter = New line
- Backspace = Delete character / merge lines
- ESC = Exit to launcher

DATA STRUCTURE:
---------------
Text is stored as a list of strings (lines):
    self.lines = ["Hello world", "Second line", ""]

Cursor position is tracked as (row, col):
    self.cursor_row = 1  # Which line (0-indexed)
    self.cursor_col = 5  # Which character in that line

This makes operations like "insert character" or "merge lines" straightforward.
"""

import time

import M5
from M5 import Lcd, Widgets

# =============================================================================
# SCREEN AND CHARACTER LAYOUT
# =============================================================================
# We use ASCII7 font at 2x scale, giving us 12x18 pixel characters.
# This determines how many characters fit on screen.

SCREEN_W = 240  # Screen width in pixels
SCREEN_H = 135  # Screen height in pixels
CHAR_W = 12  # Character width: 6 (base) * 2 (scale) = 12 pixels
CHAR_H = 18  # Character height: 9 (base) * 2 (scale) = 18 pixels
COLS = SCREEN_W // CHAR_W  # 240 / 12 = 20 characters per line
ROWS = SCREEN_H // CHAR_H  # 135 / 18 = 7 lines visible


class Notepad:
    """
    Simple multi-line text editor.

    STATE VARIABLES:
    ----------------
    - self.lines: List of strings, one per line of text
    - self.cursor_row: Current line index (0-based)
    - self.cursor_col: Current column in line (0-based)
    - self.running: Whether the app is active
    - self.first_key: Tracks if we've received first keypress
    """

    def __init__(self, keyboard):
        """Store keyboard reference and initialize empty document."""
        self.kb = keyboard
        self.lines = [""]  # Start with one empty line
        self.cursor_row = 0  # Cursor on first line
        self.cursor_col = 0  # Cursor at start of line
        self.running = False
        self.first_key = True  # Track first keypress to clear help text

    # =========================================================================
    # CURSOR DRAWING
    # =========================================================================
    # The cursor is an underscore drawn at the current position.
    # We need to draw and clear it separately from text to avoid flicker.

    def flash_edge(self):
        """
        Flash the screen edge red when user tries to type past boundary.

        VISUAL FEEDBACK PATTERN:
        ------------------------
        Instead of just ignoring input at the edge, we show the user
        why their keypress had no effect. This is better UX.
        """
        # Draw red bar on right edge
        Lcd.fillRect(SCREEN_W - 4, 0, 4, SCREEN_H, 0xF800)  # Red
        time.sleep_ms(100)  # Brief pause
        # Clear it back to black
        Lcd.fillRect(SCREEN_W - 4, 0, 4, SCREEN_H, 0x000000)

    def draw_cursor(self):
        """
        Draw an underscore cursor at current position.

        WHY UNDERSCORE?
        ---------------
        - Doesn't obscure the character at that position
        - Easy to draw (just a filled rectangle)
        - Classic terminal/editor style
        """
        x = self.cursor_col * CHAR_W
        y = self.cursor_row * CHAR_H + CHAR_H - 2  # Near bottom of character cell
        Lcd.fillRect(x, y, CHAR_W, 2, 0xFFFFFF)  # White underscore

    def clear_cursor(self):
        """Erase the cursor by drawing black over it."""
        x = self.cursor_col * CHAR_W
        y = self.cursor_row * CHAR_H + CHAR_H - 2
        Lcd.fillRect(x, y, CHAR_W, 2, 0x000000)  # Black (erase)

    def redraw(self):
        """
        Redraw the entire screen.

        Called after operations that affect multiple lines
        (like Enter or Backspace that merges lines).

        PERFORMANCE NOTE:
        -----------------
        Full redraws are slow. For single character insert/delete,
        we use incremental updates (just draw the affected character).
        Full redraw is only for multi-line changes.
        """
        Lcd.fillScreen(0x000000)
        for i, line in enumerate(self.lines):
            if i >= ROWS:
                break  # Don't draw lines below visible area
            Lcd.setCursor(0, i * CHAR_H)
            Lcd.print(line[:COLS])  # Truncate lines longer than screen
        self.draw_cursor()

    # =========================================================================
    # KEYBOARD HANDLER
    # =========================================================================

    def on_key(self, keyboard):
        """
        Handle keyboard input for text editing.

        KEY CATEGORIES:
        ---------------
        1. ESC (0x1B) - Exit the app
        2. Enter (0x0D or 0x0A) - New line
        3. Backspace (0x08) - Delete character or merge lines
        4. Printable ASCII (0x20-0x7E) - Insert character

        IMPORTANT: This is a callback! Keep it fast.
        But for this simple app, the drawing is fast enough
        that we can do it directly in the callback.
        """
        while keyboard._keyevents:
            event = keyboard._keyevents.pop(0)
            key = event.keycode

            # Skip modifier keys and zero
            if key == 0 or key > 127:
                continue

            # ================================================================
            # ESC - Exit to launcher
            # ================================================================
            if key == 0x1B:
                self.running = False
                return

            # ================================================================
            # First keypress - Clear the help text
            # ================================================================
            if self.first_key:
                self.first_key = False
                Lcd.fillScreen(0x000000)
                self.draw_cursor()

            # ================================================================
            # ENTER - Insert new line
            # ================================================================
            if key == 0x0D or key == 0x0A:
                # Split current line at cursor position
                current = self.lines[self.cursor_row]
                # Text before cursor stays on this line
                self.lines[self.cursor_row] = current[: self.cursor_col]
                # Text after cursor goes to new line
                self.lines.insert(self.cursor_row + 1, current[self.cursor_col :])
                # Move cursor to start of new line
                self.cursor_row += 1
                self.cursor_col = 0
                self.redraw()

            # ================================================================
            # BACKSPACE - Delete character or merge lines
            # ================================================================
            elif key == 0x08:
                if self.cursor_col > 0:
                    # Normal backspace - delete character before cursor
                    current = self.lines[self.cursor_row]
                    # Remove character by slicing around it
                    self.lines[self.cursor_row] = (
                        current[: self.cursor_col - 1] + current[self.cursor_col :]
                    )
                    self.cursor_col -= 1
                    self.redraw()
                elif self.cursor_row > 0:
                    # At start of line - merge with previous line
                    # Remember where to put cursor (end of previous line)
                    prev_len = len(self.lines[self.cursor_row - 1])
                    # Append this line's content to previous line
                    self.lines[self.cursor_row - 1] += self.lines[self.cursor_row]
                    # Remove this line
                    self.lines.pop(self.cursor_row)
                    # Move cursor to merge point
                    self.cursor_row -= 1
                    self.cursor_col = prev_len
                    self.redraw()

            # ================================================================
            # PRINTABLE CHARACTER - Insert into text
            # ================================================================
            elif 0x20 <= key <= 0x7E:
                # Check if at edge of screen
                if self.cursor_col >= COLS:
                    self.flash_edge()
                    continue

                # Clear old cursor before drawing character
                self.clear_cursor()

                # Convert keycode to character
                char = chr(key)
                current = self.lines[self.cursor_row]

                # Insert character at cursor position
                # String slicing: before + new char + after
                self.lines[self.cursor_row] = (
                    current[: self.cursor_col] + char + current[self.cursor_col :]
                )

                # Draw just the new character (incremental update)
                Lcd.setCursor(self.cursor_col * CHAR_W, self.cursor_row * CHAR_H)
                Lcd.print(char)

                # Move cursor right
                self.cursor_col += 1
                self.draw_cursor()

    # =========================================================================
    # MAIN RUN METHOD
    # =========================================================================

    def run(self):
        """Main entry point - set up and run the editor."""
        self.running = True
        self.first_key = True

        # Register keyboard callback
        self.kb.set_keyevent_callback(self.on_key)

        # Set up display
        Lcd.fillScreen(0x000000)
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(2)
        Lcd.setTextColor(0xFFFFFF, 0x000000)  # White on black

        # Show initial help text
        Lcd.setCursor(0, 0)
        Lcd.print("ESC=exit")

        print("Notepad started. ESC to exit.")

        # Main loop - just process events
        while self.running:
            M5.update()  # Process hardware events (triggers keyboard callback)
            time.sleep(0.01)  # 10ms = 100 updates/second

        print("Notepad exited")
        return self


# =============================================================================
# STANDALONE EXECUTION
# =============================================================================

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

    Notepad(kb).run()
