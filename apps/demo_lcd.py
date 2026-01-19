# LCD Demo - Reference for display features on M5Stack Cardputer
# Press Enter/OK to advance sections, ESC to exit
# Covers brightness, shapes, and other LCD capabilities

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
            Lcd.setTextColor(0x07E0, 0x0000)
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

        Lcd.fillScreen(0x0000)
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(2)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 5)
        Lcd.print("1. Brightness")

        Lcd.setTextSize(1)
        Lcd.setTextColor(0x07FF, 0x0000)
        Lcd.setCursor(10, 28)
        Lcd.print("Lcd.setBrightness(0-255)")

        Lcd.setTextColor(0x07E0, 0x0000)
        Lcd.setCursor(10, 43)
        Lcd.print("Use , and . to adjust")

        # Draw brightness bar background
        bar_x, bar_y, bar_w, bar_h = 20, 65, 200, 20
        Lcd.drawRect(bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2, 0xFFFF)

        original_brightness = Lcd.getBrightness()
        current_brightness = original_brightness

        def draw_brightness():
            # Draw filled portion
            fill_w = int(current_brightness / 255 * bar_w)
            Lcd.fillRect(bar_x, bar_y, fill_w, bar_h, 0xFFE0)
            Lcd.fillRect(bar_x + fill_w, bar_y, bar_w - fill_w, bar_h, 0x0000)
            # Show value
            Lcd.setTextColor(0xFFFF, 0x0000)
            Lcd.setCursor(10, 95)
            Lcd.print(f"Brightness: {current_brightness:3}  ")

        draw_brightness()

        Lcd.setTextColor(0x07E0, 0x0000)
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

        Lcd.fillScreen(0x0000)
        Lcd.setTextSize(2)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 5)
        Lcd.print("2. Basic Shapes")

        Lcd.setTextSize(1)

        # Draw various shapes
        # Lines
        Lcd.drawLine(10, 30, 50, 70, 0xF800)  # Red diagonal
        Lcd.setTextColor(0xF800, 0x0000)
        Lcd.setCursor(10, 75)
        Lcd.print("Line")

        # Rectangle outline
        Lcd.drawRect(60, 30, 40, 40, 0x07E0)  # Green
        Lcd.setTextColor(0x07E0, 0x0000)
        Lcd.setCursor(60, 75)
        Lcd.print("Rect")

        # Filled rectangle
        Lcd.fillRect(110, 30, 40, 40, 0x001F)  # Blue
        Lcd.setTextColor(0x001F, 0x0000)
        Lcd.setCursor(110, 75)
        Lcd.print("Fill")

        # Circle outline
        Lcd.drawCircle(180, 50, 20, 0xFFE0)  # Yellow
        Lcd.setTextColor(0xFFE0, 0x0000)
        Lcd.setCursor(160, 75)
        Lcd.print("Circle")

        # Filled circle
        Lcd.fillCircle(220, 50, 15, 0xF81F)  # Magenta
        Lcd.setTextColor(0xF81F, 0x0000)
        Lcd.setCursor(205, 75)
        Lcd.print("Fill")

        # API reference
        Lcd.setTextColor(0x07FF, 0x0000)
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

        Lcd.fillScreen(0x0000)
        Lcd.setTextSize(2)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 5)
        Lcd.print("3. More Shapes")

        Lcd.setTextSize(1)

        # Triangle
        Lcd.fillTriangle(30, 70, 10, 30, 50, 30, 0xF800)
        Lcd.setTextColor(0xF800, 0x0000)
        Lcd.setCursor(10, 75)
        Lcd.print("Tri")

        # Rounded rectangle
        Lcd.fillRoundRect(60, 30, 50, 40, 8, 0x07E0)
        Lcd.setTextColor(0x07E0, 0x0000)
        Lcd.setCursor(60, 75)
        Lcd.print("Round")

        # Ellipse
        Lcd.fillEllipse(150, 50, 30, 20, 0x001F)
        Lcd.setTextColor(0x001F, 0x0000)
        Lcd.setCursor(130, 75)
        Lcd.print("Ellipse")

        # Arc
        Lcd.fillArc(210, 50, 10, 25, 0, 270, 0xFFE0)
        Lcd.setTextColor(0xFFE0, 0x0000)
        Lcd.setCursor(195, 75)
        Lcd.print("Arc")

        Lcd.setTextColor(0x07FF, 0x0000)
        Lcd.setCursor(10, 90)
        Lcd.print("Triangle/RoundRect/Ellipse/Arc")

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 4: Pixels and Animation
        # =====================================================================
        # Individual pixels and simple animation

        Lcd.fillScreen(0x0000)
        Lcd.setTextSize(2)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 5)
        Lcd.print("4. Pixels")

        Lcd.setTextSize(1)
        Lcd.setTextColor(0x07FF, 0x0000)
        Lcd.setCursor(10, 28)
        Lcd.print("Lcd.drawPixel(x, y, color)")

        # Draw pixel pattern
        import random

        for _ in range(200):
            x = random.randint(10, 230)
            y = random.randint(45, 100)
            color = random.choice([0xF800, 0x07E0, 0x001F, 0xFFE0, 0xF81F, 0x07FF])
            Lcd.drawPixel(x, y, color)

        Lcd.setTextColor(0x07E0, 0x0000)
        Lcd.setCursor(10, 105)
        Lcd.print("200 random pixels drawn")

        if not wait_for_key():
            self.running = False
            return self

        # =====================================================================
        # DEMO 5: QR Code
        # =====================================================================
        # Generate QR codes on screen

        Lcd.fillScreen(0x0000)
        Lcd.setTextSize(2)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 5)
        Lcd.print("5. QR Code")

        Lcd.setTextSize(1)
        Lcd.setTextColor(0x07FF, 0x0000)
        Lcd.setCursor(10, 28)
        Lcd.print("Lcd.drawQR(text,x,y,w,ver)")

        # Draw QR code
        qr_text = "Hello Cardputer!"
        Lcd.drawQR(qr_text, 150, 35, 90, 3)

        Lcd.setTextColor(0x07E0, 0x0000)
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

        Lcd.fillScreen(0x0000)
        Lcd.setTextSize(2)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 5)
        Lcd.print("6. Display Info")

        Lcd.setTextSize(1)
        Lcd.setTextColor(0x07FF, 0x0000)

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

        Lcd.fillScreen(0x0000)
        Lcd.setTextSize(2)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 5)
        Lcd.print("7. API Reference")

        Lcd.setTextSize(1)
        Lcd.setTextColor(0x07FF, 0x0000)
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
        Lcd.fillScreen(0x0000)
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(0x07E0, 0x0000)
        Lcd.drawCenterString("Demo Complete!", 120, 50)

        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(25, 80)
        Lcd.print("See demo_lcd.py for code")

        wait_for_key()

        self.running = False
        print("LCD Demo exited")
        return self
