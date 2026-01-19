"""
LCD Demo - Graphics and Display Features on M5Stack Cardputer
=============================================================

Learn to draw shapes, control brightness, generate QR codes,
and query display properties.

CONCEPTS COVERED:
-----------------
1. Brightness Control - setBrightness(0-255)
2. Basic Shapes - Lines, rectangles, circles
3. Advanced Shapes - Triangles, rounded rects, ellipses, arcs
4. Pixel Drawing - Individual pixel manipulation
5. QR Codes - Generate QR codes on screen
6. Display Info - Query dimensions, rotation, color depth

SHAPE DRAWING API:
------------------
Lines and Points:
    Lcd.drawPixel(x, y, color)
    Lcd.drawLine(x1, y1, x2, y2, color)

Rectangles:
    Lcd.drawRect(x, y, w, h, color)        # Outline
    Lcd.fillRect(x, y, w, h, color)        # Filled
    Lcd.drawRoundRect(x, y, w, h, r, color)
    Lcd.fillRoundRect(x, y, w, h, r, color)

Circles and Ellipses:
    Lcd.drawCircle(x, y, r, color)
    Lcd.fillCircle(x, y, r, color)
    Lcd.drawEllipse(x, y, rx, ry, color)
    Lcd.fillEllipse(x, y, rx, ry, color)

Triangles:
    Lcd.drawTriangle(x1, y1, x2, y2, x3, y3, color)
    Lcd.fillTriangle(x1, y1, x2, y2, x3, y3, color)

Arcs:
    Lcd.drawArc(x, y, r1, r2, start_angle, end_angle, color)
    Lcd.fillArc(x, y, r1, r2, start_angle, end_angle, color)

QR Codes:
    Lcd.drawQR(text, x, y, width, version)  # version 1-40

Display Info:
    Lcd.width(), Lcd.height()
    Lcd.getRotation(), Lcd.getBrightness()
    Lcd.getColorDepth()

CONTROLS:
---------
- , (comma) = Decrease brightness
- . (period) = Increase brightness
- Enter = Advance to next section
- ESC = Exit to launcher
"""

import time

import M5
from M5 import Lcd, Widgets

SCREEN_W = 240
SCREEN_H = 135


class LcdDemo:
    def __init__(self, keyboard):
        self.kb = keyboard
        self.running = False

    def run(self):
        self.running = True
        exit_flag = False
        next_flag = False
        bright_up = False
        bright_down = False

        def on_key(keyboard):
            nonlocal exit_flag, next_flag, bright_up, bright_down
            while keyboard._keyevents:
                event = keyboard._keyevents.pop(0)
                if event.keycode == 0x1B:  # ESC
                    exit_flag = True
                elif event.keycode == 0x0D or event.keycode == 0x0A:  # Enter
                    next_flag = True
                elif event.keycode == ord(","):
                    bright_down = True
                elif event.keycode == ord("."):
                    bright_up = True

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

        print("LCD Demo - Enter=Next, ESC=Exit")

        # =====================================================================
        # DEMO 1: Brightness Control
        # =====================================================================
        # Lcd.setBrightness(0-255) - set screen brightness
        # Lcd.getBrightness() - get current brightness

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("1. Brightness")

        Lcd.setTextSize(1)
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 28)
        Lcd.print("Lcd.setBrightness(0-255)")

        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 43)
        Lcd.print("Use , and . to adjust")

        # Draw brightness bar background
        bar_x, bar_y, bar_w, bar_h = 20, 65, 200, 20
        Lcd.drawRect(bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2, Lcd.COLOR.WHITE)

        original_brightness = Lcd.getBrightness()
        current_brightness = original_brightness

        def draw_brightness():
            # Draw filled portion
            fill_w = int(current_brightness / 255 * bar_w)
            Lcd.fillRect(bar_x, bar_y, fill_w, bar_h, Lcd.COLOR.YELLOW)
            Lcd.fillRect(bar_x + fill_w, bar_y, bar_w - fill_w, bar_h, Lcd.COLOR.BLACK)
            # Show value
            Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
            Lcd.setCursor(10, 95)
            Lcd.print(f"Brightness: {current_brightness:3}  ")

        draw_brightness()

        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(0, SCREEN_H - 10)
        Lcd.print(",=Down .=Up Enter=Next")

        next_flag = False
        while not exit_flag and not next_flag:
            M5.update()

            # Check for brightness adjustment flags (set by callback)
            if bright_down:
                bright_down = False
                current_brightness = max(0, current_brightness - 10)
                Lcd.setBrightness(current_brightness)
                draw_brightness()
            if bright_up:
                bright_up = False
                current_brightness = min(255, current_brightness + 10)
                Lcd.setBrightness(current_brightness)
                draw_brightness()

            time.sleep(0.02)

        # Restore original brightness
        Lcd.setBrightness(original_brightness)

        if exit_flag:
            self.running = False
            return self

        # =====================================================================
        # DEMO 2: Basic Shapes
        # =====================================================================
        # Lines, rectangles, circles

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("2. Basic Shapes")

        Lcd.setTextSize(1)

        # Draw various shapes
        # Lines
        Lcd.drawLine(10, 30, 50, 70, Lcd.COLOR.RED)  # Red diagonal
        Lcd.setTextColor(Lcd.COLOR.RED, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 75)
        Lcd.print("Line")

        # Rectangle outline
        Lcd.drawRect(60, 30, 40, 40, Lcd.COLOR.GREEN)  # Green
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(60, 75)
        Lcd.print("Rect")

        # Filled rectangle
        Lcd.fillRect(110, 30, 40, 40, Lcd.COLOR.BLUE)  # Blue
        Lcd.setTextColor(Lcd.COLOR.BLUE, Lcd.COLOR.BLACK)
        Lcd.setCursor(110, 75)
        Lcd.print("Fill")

        # Circle outline
        Lcd.drawCircle(180, 50, 20, Lcd.COLOR.YELLOW)  # Yellow
        Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
        Lcd.setCursor(160, 75)
        Lcd.print("Circle")

        # Filled circle
        Lcd.fillCircle(220, 50, 15, Lcd.COLOR.MAGENTA)  # Magenta
        Lcd.setTextColor(Lcd.COLOR.MAGENTA, Lcd.COLOR.BLACK)
        Lcd.setCursor(205, 75)
        Lcd.print("Fill")

        # API reference
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 90)
        Lcd.print("drawLine/Rect/Circle()")
        Lcd.setCursor(10, 102)
        Lcd.print("fillRect/Circle()")

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 3: More Shapes
        # =====================================================================
        # Triangles, rounded rects, ellipses

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("3. More Shapes")

        Lcd.setTextSize(1)

        # Triangle
        Lcd.fillTriangle(30, 70, 10, 30, 50, 30, Lcd.COLOR.RED)
        Lcd.setTextColor(Lcd.COLOR.RED, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 75)
        Lcd.print("Tri")

        # Rounded rectangle
        Lcd.fillRoundRect(60, 30, 50, 40, 8, Lcd.COLOR.GREEN)
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(60, 75)
        Lcd.print("Round")

        # Ellipse
        Lcd.fillEllipse(150, 50, 30, 20, Lcd.COLOR.BLUE)
        Lcd.setTextColor(Lcd.COLOR.BLUE, Lcd.COLOR.BLACK)
        Lcd.setCursor(130, 75)
        Lcd.print("Ellipse")

        # Arc
        Lcd.fillArc(210, 50, 10, 25, 0, 270, Lcd.COLOR.YELLOW)
        Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
        Lcd.setCursor(195, 75)
        Lcd.print("Arc")

        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 90)
        Lcd.print("Triangle/RoundRect/Ellipse/Arc")

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 4: Pixels and Animation
        # =====================================================================
        # Individual pixels and simple animation

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("4. Pixels")

        Lcd.setTextSize(1)
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 28)
        Lcd.print("Lcd.drawPixel(x, y, color)")

        # Draw pixel pattern
        import random

        for _ in range(200):
            x = random.randint(10, 230)
            y = random.randint(45, 100)
            color = random.choice([Lcd.COLOR.RED, Lcd.COLOR.GREEN, Lcd.COLOR.BLUE, Lcd.COLOR.YELLOW, Lcd.COLOR.MAGENTA, Lcd.COLOR.CYAN])
            Lcd.drawPixel(x, y, color)

        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 105)
        Lcd.print("200 random pixels drawn")

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 5: QR Code
        # =====================================================================
        # Generate QR codes on screen

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("5. QR Code")

        Lcd.setTextSize(1)
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 28)
        Lcd.print("Lcd.drawQR(text,x,y,w,ver)")

        # Draw QR code
        qr_text = "Hello Cardputer!"
        Lcd.drawQR(qr_text, 150, 35, 90, 3)

        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 50)
        Lcd.print("Text:")
        Lcd.setCursor(10, 62)
        Lcd.print(f'"{qr_text}"')

        Lcd.setCursor(10, 82)
        Lcd.print("ver=1-40 (size)")
        Lcd.setCursor(10, 94)
        Lcd.print("w=pixel width")

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 6: Display Info
        # =====================================================================
        # Screen dimensions and other info

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("6. Display Info")

        Lcd.setTextSize(1)
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)

        y = 30
        infos = [
            f"Width: {Lcd.width()}px",
            f"Height: {Lcd.height()}px",
            f"Rotation: {Lcd.getRotation()}",
            f"Brightness: {Lcd.getBrightness()}",
            f"Color depth: {Lcd.getColorDepth()}bpp",
        ]

        for info in infos:
            Lcd.setCursor(10, y)
            Lcd.print(info)
            y += 15

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 7: API Reference
        # =====================================================================

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("7. API Reference")

        Lcd.setTextSize(1)
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        y = 28
        apis = [
            "setBrightness(0-255)",
            "drawLine/Rect/Circle()",
            "fillRect/Circle/Triangle()",
            "drawRoundRect/Ellipse/Arc()",
            "drawPixel(x,y,color)",
            "drawQR(text,x,y,w,ver)",
            "width()/height()/getRotation()",
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
        Lcd.setCursor(25, 80)
        Lcd.print("See demo_lcd.py for code")

        wait_for_key()

        self.running = False
        print("LCD Demo exited")
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

    LcdDemo(kb).run()
