"""
Text Demo - Text Rendering on M5Stack Cardputer
================================================

Learn how to display text on the Cardputer's LCD. This demo covers all the
essential text rendering techniques you'll need.

CONCEPTS COVERED:
-----------------
1. Fonts - Built-in fonts and when to use each
2. Font Scaling - setTextSize() for larger text
3. Colors - 24-bit RGB color format
4. Text Measurement - textWidth() and fontHeight() for layout
5. Alignment - drawString, drawCenterString, drawRightString
6. Formatted Output - f-strings and printf()
7. Scrolling Text - Marquee effect using canvas as viewport

AVAILABLE FONTS (Widgets.FONTS):
--------------------------------
- ASCII7: Monospace 6x9 pixels - best for terminals/code
- DejaVu9/12/18/24/40/56/72: Proportional fonts at various sizes
- EFontCN24, EFontJA24, EFontKR24: CJK (Chinese/Japanese/Korean) fonts

COLOR CONSTANTS (Lcd.COLOR):
----------------------------
Use built-in color constants for cleaner code:
    Lcd.COLOR.BLACK, Lcd.COLOR.WHITE
    Lcd.COLOR.RED, Lcd.COLOR.GREEN, Lcd.COLOR.BLUE
    Lcd.COLOR.YELLOW, Lcd.COLOR.MAGENTA, Lcd.COLOR.CYAN
    Lcd.COLOR.ORANGE, Lcd.COLOR.PINK, Lcd.COLOR.PURPLE
Colors are 24-bit RGB (0xRRGGBB) - the library handles conversion.

CONTROLS:
---------
- Enter = Advance to next section
- ESC = Exit to launcher
"""

import time

import M5
from M5 import Lcd, Widgets

SCREEN_W = 240
SCREEN_H = 135


class TextDemo:
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
            """Wait for Enter to continue or ESC to exit"""
            nonlocal next_flag, exit_flag
            next_flag = False
            # Show prompt
            Lcd.setFont(Widgets.FONTS.ASCII7)
            Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)  # Green
            Lcd.setCursor(0, SCREEN_H - 10)
            Lcd.print("Enter=Next  ESC=Exit")
            while not next_flag and not exit_flag:
                M5.update()
                time.sleep(0.01)
            return not exit_flag

        print("Text Demo - Enter=Next, ESC=Exit")

        # =====================================================================
        # DEMO 1: Available Fonts
        # =====================================================================
        # Built-in fonts in Widgets.FONTS:
        #   ASCII7      - 6x9 pixels, monospace (best for terminals/editors)
        #   DejaVu9/12/18/24/40/56/72 - proportional fonts
        #   EFontCN24, EFontJA24, EFontKR24 - CJK fonts

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 10)
        Lcd.print("1. Basic Text")

        Lcd.setFont(Widgets.FONTS.DejaVu12)
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 40)
        Lcd.print("setFont(Widgets.FONTS.xxx)")
        Lcd.setCursor(10, 55)
        Lcd.print("setTextColor(fg, bg)")
        Lcd.setCursor(10, 70)
        Lcd.print("setCursor(x, y)")
        Lcd.setCursor(10, 85)
        Lcd.print("print(text)")

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 2: Font Scaling (for monospace)
        # =====================================================================
        # setTextSize(n) scales the font by n times
        # ASCII7 at size 1 = 6x9 pixels per character
        # ASCII7 at size 2 = 12x18 pixels per character
        # ASCII7 at size 3 = 18x27 pixels per character

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)

        Lcd.setTextSize(1)
        Lcd.setCursor(0, 0)
        Lcd.print("2. setTextSize()")

        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(0, 15)
        Lcd.print("Size 1: 6x9px")

        Lcd.setTextSize(2)
        Lcd.setCursor(0, 30)
        Lcd.print("Size 2: 12x18")

        Lcd.setTextSize(3)
        Lcd.setCursor(0, 60)
        Lcd.print("Size 3")

        Lcd.setTextSize(1)

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 3: Color Constants (Lcd.COLOR.*)
        # =====================================================================
        # Use Lcd.COLOR.* constants for cleaner, more readable code.
        # Available: BLACK, WHITE, RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN,
        #            ORANGE, PINK, PURPLE, NAVY, DARKGREEN, DARKCYAN, etc.

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.DejaVu12)

        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 0)
        Lcd.print("3. Lcd.COLOR Constants")

        colors = [
            (Lcd.COLOR.RED, "Lcd.COLOR.RED"),
            (Lcd.COLOR.GREEN, "Lcd.COLOR.GREEN"),
            (Lcd.COLOR.BLUE, "Lcd.COLOR.BLUE"),
            (Lcd.COLOR.YELLOW, "Lcd.COLOR.YELLOW"),
            (Lcd.COLOR.MAGENTA, "Lcd.COLOR.MAGENTA"),
            (Lcd.COLOR.CYAN, "Lcd.COLOR.CYAN"),
        ]

        y = 18
        for color, name in colors:
            Lcd.setTextColor(color, Lcd.COLOR.BLACK)
            Lcd.setCursor(10, y)
            Lcd.print(name)
            y += 15

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 4: Text Measurement
        # =====================================================================
        # textWidth(text) - returns pixel width of string
        # fontHeight() - returns pixel height of current font

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.DejaVu12)
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 0)
        Lcd.print("4. Text Measurement")

        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)

        text = "Centered!"
        width = Lcd.textWidth(text)
        height = Lcd.fontHeight()

        # Center on screen
        x = (SCREEN_W - width) // 2
        y = (SCREEN_H - height) // 2

        Lcd.setCursor(x, y)
        Lcd.print(text)

        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 20)
        Lcd.print(f"textWidth()={width}")
        Lcd.setCursor(10, 30)
        Lcd.print(f"fontHeight()={height}")

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 5: Drawing Methods
        # =====================================================================
        # drawString(text, x, y) - left aligned at x
        # drawCenterString(text, x, y) - centered at x
        # drawRightString(text, x, y) - right aligned at x

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.DejaVu12)
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 0)
        Lcd.print("5. Draw Methods")

        Lcd.setFont(Widgets.FONTS.DejaVu12)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)

        # Draw vertical line at x=120 (center)
        Lcd.drawLine(120, 20, 120, 110, Lcd.COLOR.RED)

        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.drawString("drawString", 120, 30)

        Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
        Lcd.drawCenterString("drawCenterString", 120, 55)

        Lcd.setTextColor(Lcd.COLOR.MAGENTA, Lcd.COLOR.BLACK)
        Lcd.drawRightString("drawRightString", 120, 80)

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 6: Formatted Output
        # =====================================================================
        # Use f-strings or printf() for formatting

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.DejaVu12)
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 0)
        Lcd.print("6. Formatted Output")

        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)

        score = 42
        lives = 3

        Lcd.setCursor(10, 25)
        Lcd.print(f"Score: {score}")

        Lcd.setCursor(10, 50)
        Lcd.print(f"Lives: {lives}")

        Lcd.setCursor(10, 75)
        Lcd.printf("Hex: 0x%04X", score)

        Lcd.setTextSize(1)

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 7: Scrolling Text (Marquee)
        # =====================================================================
        # Technique: Use a canvas as a "viewport" for the scrolling text
        # - Canvas acts as a clipping region (text outside canvas is hidden)
        # - Draw text at negative x position to scroll it left
        # - Draw a second copy of text for seamless looping
        # - Use drawString() instead of print() to avoid text wrapping

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.DejaVu12)
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 0)
        Lcd.print("7. Scrolling Text")

        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 18)
        Lcd.print("Marquee effect with canvas:")

        # The text to scroll (add trailing spaces for gap between loops)
        scroll_text = "This is scrolling marquee text! Hello world!     "

        # Get font metrics for sizing the canvas
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        text_width = Lcd.textWidth(scroll_text)
        font_height = Lcd.fontHeight()

        # Canvas dimensions and position (centered on screen)
        canvas_w = 180  # Width of visible scroll area
        canvas_h = font_height + 2  # Height = font + minimal padding
        canvas_x = (SCREEN_W - canvas_w) // 2  # Center horizontally
        canvas_y = 50  # Position below title
        text_y = 1  # 1px from top of canvas

        # Draw border around scroll area
        Lcd.drawRect(canvas_x - 2, canvas_y - 2, canvas_w + 4, canvas_h + 4, Lcd.COLOR.WHITE)

        # Create canvas for smooth animation (double buffering)
        # Canvas size determines the visible "viewport" for scrolling
        scroll_canvas = Lcd.newCanvas(canvas_w, canvas_h)
        scroll_canvas.setFont(Widgets.FONTS.DejaVu18)
        scroll_canvas.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)

        # Scroll offset starts at 0 (text visible from left edge)
        scroll_offset = 0

        # Reset flag before entering scroll loop
        next_flag = False
        scrolling = True
        while scrolling:
            M5.update()

            # Check for exit/next using flags set by on_key callback
            # (Don't access _keyevents directly - callback already handles it)
            if exit_flag:
                scroll_canvas.delete()
                self.running = False
                return self
            if next_flag:
                next_flag = False
                scrolling = False
                continue

            # Clear canvas each frame
            scroll_canvas.fillScreen(Lcd.COLOR.BLACK)

            # Draw text at -scroll_offset (moves left as offset increases)
            # Text drawn at negative x is clipped by canvas boundary
            x1 = -scroll_offset
            scroll_canvas.drawString(scroll_text, x1, text_y)

            # Draw second copy for seamless loop
            # When first copy scrolls off left, second copy appears from right
            x2 = x1 + text_width
            if x2 < canvas_w:
                scroll_canvas.drawString(scroll_text, x2, text_y)

            # Push canvas to screen position
            scroll_canvas.push(canvas_x, canvas_y)

            # Increase offset (text moves left)
            scroll_offset += 2
            # Reset when we've scrolled one full text width (seamless loop)
            if scroll_offset >= text_width:
                scroll_offset = 0

            time.sleep(0.025)

        scroll_canvas.delete()

        # Show explanation
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(1)
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 80)
        Lcd.print("Key concepts:")
        Lcd.setCursor(10, 92)
        Lcd.print("- Canvas = clipping viewport")
        Lcd.setCursor(10, 104)
        Lcd.print("- drawString at -offset")
        Lcd.setCursor(10, 116)
        Lcd.print("- 2nd copy for seamless loop")

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
        Lcd.setCursor(30, 80)
        Lcd.print("See demo_text.py for code")

        wait_for_key()

        self.running = False
        print("Text Demo exited")
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

    TextDemo(kb).run()
