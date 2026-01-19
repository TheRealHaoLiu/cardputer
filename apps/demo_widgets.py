"""
Widgets Demo - High-Level UI Components
=======================================

The widgets module provides Label and Image classes that simplify
common UI patterns. Labels handle text with automatic clearing/redraw.

CONCEPTS COVERED:
-----------------
1. widgets.Label Basics - Creating and using labels
2. Text Alignment - LEFT/CENTER/RIGHT_ALIGNED
3. Dynamic Updates - set_text() auto-clears old content
4. Long Text Modes - Truncation (LONG_DOT) and wrapping (LONG_WARP)
5. UI Patterns - Title bars, cards, dashboards

WHY USE widgets.Label?
----------------------
When you update text with Lcd.print(), old text remains visible.
You have to manually clear the area first with fillRect().

widgets.Label handles this automatically:
    label.set_text("New text")  # Old text cleared, new text drawn

LABEL CONSTRUCTOR:
------------------
    label = widgets.Label(
        text,           # Initial text
        x, y,           # Position (meaning depends on alignment)
        w=width,        # Max width (optional)
        h=height,       # Max height (optional)
        font_align=..., # LEFT/CENTER/RIGHT_ALIGNED
        fg_color=...,   # Text color (RGB565)
        bg_color=...,   # Background color (MUST match actual background!)
        font=...,       # Font from Widgets.FONTS
    )

ALIGNMENT EXPLAINED:
--------------------
- LEFT_ALIGNED: x is LEFT edge of text
- CENTER_ALIGNED: x is CENTER point of text
- RIGHT_ALIGNED: x is RIGHT edge of text

LONG TEXT MODES:
----------------
- LONG_DOT: Truncate with "..." if too wide
- LONG_WARP: Wrap to multiple lines

IMPORTANT: bg_color must match your background exactly, or you'll
see rectangles when text updates!

CONTROLS:
---------
- Enter = Advance to next section
- ESC = Exit to launcher
"""

import time

import M5
import widgets
from M5 import Lcd, Widgets

SCREEN_W = 240
SCREEN_H = 135


class WidgetsDemo:
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
            Lcd.setTextColor(0x07E0, 0x0000)  # Green
            Lcd.setCursor(0, SCREEN_H - 10)
            Lcd.print("Enter=Next  ESC=Exit")
            while not next_flag and not exit_flag:
                M5.update()
                time.sleep(0.01)
            return not exit_flag

        print("Widgets Demo - Enter=Next, ESC=Exit")

        # =====================================================================
        # DEMO 1: widgets.Label Basics
        # =====================================================================
        # widgets.Label wraps Lcd text drawing with automatic clearing/redraw
        # Key benefit: set_text() clears old text before drawing new

        Lcd.fillScreen(0x0000)
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 5)
        Lcd.print("1. widgets.Label")

        Lcd.setFont(Widgets.FONTS.DejaVu12)
        Lcd.setTextColor(0x07FF, 0x0000)  # Cyan
        Lcd.setCursor(10, 30)
        Lcd.print("import widgets")

        Lcd.setTextColor(0xFFE0, 0x0000)  # Yellow
        Lcd.setCursor(10, 48)
        Lcd.print("lbl = widgets.Label(")
        Lcd.setCursor(20, 63)
        Lcd.print("text, x, y, w, h,")
        Lcd.setCursor(20, 78)
        Lcd.print("font_align, fg_color,")
        Lcd.setCursor(20, 93)
        Lcd.print("bg_color, font)")

        Lcd.setTextColor(0x07E0, 0x0000)  # Green
        Lcd.setCursor(10, 111)
        Lcd.print("lbl.set_text('new') # auto clears")

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 2: Label Alignments
        # =====================================================================
        # LEFT_ALIGNED: x is left edge of text
        # CENTER_ALIGNED: x is center point of text
        # RIGHT_ALIGNED: x is right edge of text

        Lcd.fillScreen(0x0000)
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 5)
        Lcd.print("2. Alignments")

        # Draw reference lines to show alignment points
        Lcd.drawLine(10, 28, 10, 115, 0x4208)  # Left marker
        Lcd.drawLine(120, 28, 120, 115, 0x4208)  # Center marker
        Lcd.drawLine(230, 28, 230, 115, 0x4208)  # Right marker

        # LEFT_ALIGNED - x=10 is the LEFT edge
        left_label = widgets.Label(
            "LEFT x=10",
            10,
            35,  # x is left edge
            w=100,
            font_align=widgets.Label.LEFT_ALIGNED,
            fg_color=0xF800,  # Red
            bg_color=0x0000,
            font=Widgets.FONTS.DejaVu12,
        )
        left_label.set_text("LEFT x=10")

        # CENTER_ALIGNED - x=120 is the CENTER point
        center_label = widgets.Label(
            "CENTER x=120",
            120,
            60,  # x is center point
            w=150,
            font_align=widgets.Label.CENTER_ALIGNED,
            fg_color=0x07E0,  # Green
            bg_color=0x0000,
            font=Widgets.FONTS.DejaVu12,
        )
        center_label.set_text("CENTER x=120")

        # RIGHT_ALIGNED - x=230 is the RIGHT edge
        right_label = widgets.Label(
            "RIGHT x=230",
            230,
            85,  # x is right edge
            w=150,
            font_align=widgets.Label.RIGHT_ALIGNED,
            fg_color=0xFFE0,  # Yellow (visible)
            bg_color=0x0000,
            font=Widgets.FONTS.DejaVu12,
        )
        right_label.set_text("RIGHT x=230")

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 3: Dynamic Label Updates
        # =====================================================================
        # set_text() automatically clears the old text area
        # No need to manually fillRect before updating!

        Lcd.fillScreen(0x0000)
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 5)
        Lcd.print("3. Dynamic Update")

        # Show explanation
        Lcd.setFont(Widgets.FONTS.DejaVu12)
        Lcd.setTextColor(0x07FF, 0x0000)
        Lcd.setCursor(10, 30)
        Lcd.print("set_text() auto-clears old text")

        # Counter label - will be updated
        counter_label = widgets.Label(
            "Count: 0",
            SCREEN_W // 2,
            60,
            w=150,
            font_align=widgets.Label.CENTER_ALIGNED,
            fg_color=0xFFE0,  # Yellow
            bg_color=0x0000,
            font=Widgets.FONTS.DejaVu18,
        )
        counter_label.set_text("Count: 0")

        # Varying width text to show clearing works
        width_label = widgets.Label(
            "Width varies",
            SCREEN_W // 2,
            90,
            w=200,
            font_align=widgets.Label.CENTER_ALIGNED,
            fg_color=0xF81F,  # Magenta
            bg_color=0x0000,
            font=Widgets.FONTS.DejaVu12,
        )
        width_label.set_text("Short")

        texts = ["Short", "Medium text", "This is longer text", "Tiny", "Hello World"]

        # Animate counter
        count = 0
        while not exit_flag and not next_flag:
            M5.update()
            counter_label.set_text(f"Count: {count}")
            width_label.set_text(texts[count % len(texts)])
            count += 1
            time.sleep(0.2)

        if exit_flag:
            self.running = False
            return self

        # =====================================================================
        # DEMO 4: Long Text Modes
        # =====================================================================
        # LONG_DOT: Truncates text with "..." when too wide
        # LONG_WARP: Wraps text to multiple lines

        Lcd.fillScreen(0x0000)
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 5)
        Lcd.print("4. Long Text")

        long_text = "This is a very long text string that won't fit"

        # LONG_DOT - truncates with ellipsis
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(1)
        Lcd.setTextColor(0x07FF, 0x0000)
        Lcd.setCursor(10, 30)
        Lcd.print("LONG_DOT: truncate with ...")

        dot_label = widgets.Label(
            long_text,
            10,
            42,
            w=140,
            h=15,
            font_align=widgets.Label.LEFT_ALIGNED,
            fg_color=0xFFE0,  # Yellow
            bg_color=0x0000,
            font=Widgets.FONTS.DejaVu12,
        )
        dot_label.set_long_mode(widgets.Label.LONG_DOT)
        dot_label.set_text(long_text)

        # LONG_WARP - wraps to next line
        # Must reset font after widgets.Label changes it
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(1)
        Lcd.setTextColor(0x07FF, 0x0000)
        Lcd.setCursor(10, 62)
        Lcd.print("LONG_WARP: wrap to next line")

        wrap_label = widgets.Label(
            long_text,
            10,
            74,
            w=220,
            h=50,
            font_align=widgets.Label.LEFT_ALIGNED,
            fg_color=0xFFE0,  # Yellow (same as LONG_DOT)
            bg_color=0x0000,
            font=Widgets.FONTS.DejaVu12,
        )
        wrap_label.set_long_mode(widgets.Label.LONG_WARP)
        wrap_label.set_text(long_text)

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 5: Title Bar Pattern
        # =====================================================================
        # Common UI pattern: colored bar at top with centered title
        # Note: bg_color must match the bar color exactly

        Lcd.fillScreen(0x0000)

        # Draw title bar (18px high)
        TITLE_BAR_COLOR = 0x001F  # Blue
        Lcd.fillRect(0, 0, SCREEN_W, 20, TITLE_BAR_COLOR)

        # Title label - bg_color MUST match bar
        title = widgets.Label(
            "Title Bar Demo",
            SCREEN_W // 2,
            3,
            w=200,
            font_align=widgets.Label.CENTER_ALIGNED,
            fg_color=0xFFFF,  # White text
            bg_color=TITLE_BAR_COLOR,  # Match bar!
            font=Widgets.FONTS.DejaVu18,
        )
        title.set_text("Title Bar Demo")

        # Explanation
        Lcd.setFont(Widgets.FONTS.DejaVu12)
        Lcd.setTextColor(0x07FF, 0x0000)
        Lcd.setCursor(10, 30)
        Lcd.print("Pattern:")

        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextColor(0xFFE0, 0x0000)
        y = 48
        code = [
            "BAR_COLOR = 0x001F",
            "Lcd.fillRect(0,0,240,20,BAR_COLOR)",
            "",
            "title = widgets.Label(",
            "  'Title', 120, 3,",
            "  font_align=CENTER_ALIGNED,",
            "  bg_color=BAR_COLOR)  # Must match!",
        ]
        for line in code:
            Lcd.setCursor(10, y)
            Lcd.print(line)
            y += 10

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 6: Card UI Pattern
        # =====================================================================
        # Combining Lcd shapes + widgets.Label for card-style UI
        # Good for dashboards, status displays, settings

        Lcd.fillScreen(0x1082)  # Dark blue background

        # Title bar
        Lcd.fillRect(0, 0, SCREEN_W, 18, 0x4A69)
        title = widgets.Label(
            "Card UI Pattern",
            SCREEN_W // 2,
            2,
            w=200,
            font_align=widgets.Label.CENTER_ALIGNED,
            fg_color=0xFFFF,
            bg_color=0x4A69,
            font=Widgets.FONTS.DejaVu12,
        )
        title.set_text("Card UI Pattern")

        # Helper to draw a card
        def draw_card(x, y, w, h, label_text, value_text, value_color):
            # Card background with border
            Lcd.fillRoundRect(x, y, w, h, 4, 0x2104)
            Lcd.drawRoundRect(x, y, w, h, 4, 0x4208)

            # Label (small, gray)
            Lcd.setFont(Widgets.FONTS.ASCII7)
            Lcd.setTextColor(0x7BEF, 0x2104)
            Lcd.setCursor(x + 5, y + 5)
            Lcd.print(label_text)

            # Value (using widgets.Label for easy updates)
            val = widgets.Label(
                value_text,
                x + w // 2,
                y + 20,
                w=w - 10,
                font_align=widgets.Label.CENTER_ALIGNED,
                fg_color=value_color,
                bg_color=0x2104,
                font=Widgets.FONTS.DejaVu18,
            )
            val.set_text(value_text)
            return val

        # Draw cards
        card1 = draw_card(5, 24, 72, 45, "Battery", "85%", 0x07E0)
        card2 = draw_card(84, 24, 72, 45, "Signal", "4/5", 0xFFE0)
        card3 = draw_card(163, 24, 72, 45, "Temp", "32C", 0x07FF)

        # Code explanation
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextColor(0x7BEF, 0x1082)
        Lcd.setCursor(10, 78)
        Lcd.print("Pattern: fillRoundRect + drawRoundRect")
        Lcd.setCursor(10, 90)
        Lcd.print("+ widgets.Label for updateable values")
        Lcd.setCursor(10, 102)
        Lcd.print("card_val.set_text('new value')")

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 7: API Reference
        # =====================================================================

        Lcd.fillScreen(0x0000)
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 5)
        Lcd.print("7. API Reference")

        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(1)
        Lcd.setTextColor(0x07FF, 0x0000)
        y = 28
        apis = [
            "widgets.Label(text,x,y,w,h,font_align,",
            "              fg_color,bg_color,font)",
            "  .set_text(text)     # clears & redraws",
            "  .set_long_mode(LONG_DOT|LONG_WARP)",
            "  .set_text_color(fg, bg)",
            "  .set_pos(x, y)",
            "",
            "Alignments: LEFT/CENTER/RIGHT_ALIGNED",
        ]
        for api in apis:
            Lcd.setCursor(5, y)
            Lcd.print(api)
            y += 11

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
        Lcd.setCursor(15, 80)
        Lcd.print("See demo_widgets.py for code")

        wait_for_key()

        self.running = False
        print("Widgets Demo exited")
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

    WidgetsDemo(kb).run()
