"""
Shapes Demo - LCD Drawing Primitives
=====================================

Demonstrates the LCD graphics API on M5Stack Cardputer. Learn to draw
lines, rectangles, circles, triangles, ellipses, and arcs.

LCD DRAWING API SUMMARY:
------------------------
Lines and Points:
    Lcd.drawPixel(x, y, color)
    Lcd.drawLine(x1, y1, x2, y2, color)

Rectangles:
    Lcd.drawRect(x, y, w, h, color)          # Outline
    Lcd.fillRect(x, y, w, h, color)          # Filled
    Lcd.drawRoundRect(x, y, w, h, r, color)  # Rounded outline
    Lcd.fillRoundRect(x, y, w, h, r, color)  # Rounded filled

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

CONTROLS:
---------
    Left/Right or ,/. = Previous/Next shape
    F = Toggle filled/outline mode
    C = Cycle colors
    ESC = Exit to launcher
"""

import asyncio
import sys

for path in ["/flash", "/remote"]:
    if path not in sys.path:
        sys.path.insert(0, path)

from M5 import Lcd, Widgets

from libs.app_base import AppBase
from libs.keycode import KeyCode

SCREEN_W = 240
SCREEN_H = 135

# Available colors for cycling
COLORS = [
    ("Red", Lcd.COLOR.RED),
    ("Green", Lcd.COLOR.GREEN),
    ("Blue", Lcd.COLOR.BLUE),
    ("Yellow", Lcd.COLOR.YELLOW),
    ("Magenta", Lcd.COLOR.MAGENTA),
    ("Cyan", Lcd.COLOR.CYAN),
    ("Orange", Lcd.COLOR.ORANGE),
    ("White", Lcd.COLOR.WHITE),
]

# Shape definitions
SHAPES = [
    "Line",
    "Rectangle",
    "Round Rect",
    "Circle",
    "Ellipse",
    "Triangle",
    "Arc",
    "Pixels",
]


class ShapesDemo(AppBase):
    """Interactive shape drawing demo."""

    def __init__(self):
        super().__init__()
        self.name = "Shapes Demo"
        self._shape_idx = 0
        self._color_idx = 0
        self._filled = True

    def on_view(self):
        """Draw the current shape."""
        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.ASCII7)

        # Title
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("Shapes Demo")

        # Current shape name
        shape_name = SHAPES[self._shape_idx]
        color_name, color = COLORS[self._color_idx]
        fill_text = "Filled" if self._filled else "Outline"

        Lcd.setTextSize(1)
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 28)
        Lcd.print(f"{shape_name} - {color_name} - {fill_text}")

        # Draw the shape in the center area
        self._draw_current_shape()

        # Controls
        Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 110)
        Lcd.print("</>:Shape  F:Fill  C:Color")

        # Footer
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(0, SCREEN_H - 12)
        Lcd.print(f"ESC=Exit    [{self._shape_idx + 1}/{len(SHAPES)}]")

    def _draw_current_shape(self):
        """Draw the currently selected shape."""
        _, color = COLORS[self._color_idx]
        shape = SHAPES[self._shape_idx]

        # Drawing area: centered, leaving room for text
        cx, cy = 120, 70  # Center of drawing area

        if shape == "Line":
            # Draw several lines radiating from center
            Lcd.drawLine(cx - 40, cy - 20, cx + 40, cy + 20, color)
            Lcd.drawLine(cx - 40, cy + 20, cx + 40, cy - 20, color)
            Lcd.drawLine(cx, cy - 25, cx, cy + 25, color)
            Lcd.drawLine(cx - 45, cy, cx + 45, cy, color)

        elif shape == "Rectangle":
            if self._filled:
                Lcd.fillRect(cx - 50, cy - 25, 100, 50, color)
            else:
                Lcd.drawRect(cx - 50, cy - 25, 100, 50, color)

        elif shape == "Round Rect":
            if self._filled:
                Lcd.fillRoundRect(cx - 50, cy - 25, 100, 50, 10, color)
            else:
                Lcd.drawRoundRect(cx - 50, cy - 25, 100, 50, 10, color)

        elif shape == "Circle":
            if self._filled:
                Lcd.fillCircle(cx, cy, 30, color)
            else:
                Lcd.drawCircle(cx, cy, 30, color)

        elif shape == "Ellipse":
            if self._filled:
                Lcd.fillEllipse(cx, cy, 50, 25, color)
            else:
                Lcd.drawEllipse(cx, cy, 50, 25, color)

        elif shape == "Triangle":
            # Equilateral-ish triangle
            if self._filled:
                Lcd.fillTriangle(cx, cy - 30, cx - 40, cy + 25, cx + 40, cy + 25, color)
            else:
                Lcd.drawTriangle(cx, cy - 30, cx - 40, cy + 25, cx + 40, cy + 25, color)

        elif shape == "Arc":
            # Arc from 0 to 270 degrees
            if self._filled:
                Lcd.fillArc(cx, cy, 15, 35, 0, 270, color)
            else:
                Lcd.drawArc(cx, cy, 15, 35, 0, 270, color)

        elif shape == "Pixels":
            # Draw random pixels in a pattern
            import random

            for _ in range(100):
                x = random.randint(cx - 50, cx + 50)
                y = random.randint(cy - 30, cy + 30)
                Lcd.drawPixel(x, y, color)

    async def _kb_event_handler(self, event, fw):
        """Handle keyboard events."""
        key = event.key

        # Don't handle ESC
        if key == KeyCode.KEYCODE_ESC:
            return

        # Next shape
        if key == ord(".") or key == ord(">") or key == KeyCode.KEYCODE_RIGHT:
            self._shape_idx = (self._shape_idx + 1) % len(SHAPES)
            self.on_view()
            event.status = True
            return

        # Previous shape
        if key == ord(",") or key == ord("<") or key == KeyCode.KEYCODE_LEFT:
            self._shape_idx = (self._shape_idx - 1) % len(SHAPES)
            self.on_view()
            event.status = True
            return

        # Toggle filled/outline
        if key == ord("f") or key == ord("F"):
            self._filled = not self._filled
            self.on_view()
            event.status = True
            return

        # Cycle colors
        if key == ord("c") or key == ord("C"):
            self._color_idx = (self._color_idx + 1) % len(COLORS)
            self.on_view()
            event.status = True
            return

        event.status = True

    async def on_run(self):
        """Background task."""
        while True:
            await asyncio.sleep_ms(100)


# Export for framework discovery
App = ShapesDemo

if __name__ == "__main__":
    import M5

    M5.begin()
    Lcd.setRotation(1)
    Lcd.setBrightness(40)

    from libs.framework import Framework

    fw = Framework()
    fw.install(ShapesDemo())
    fw.start()
