"""
Animation Demo - Double Buffering Comparison
=============================================

Side-by-side comparison of animation techniques:
- LEFT: Direct LCD drawing (flickery - the wrong way)
- RIGHT: Canvas double buffering (smooth - the right way)

THE PROBLEM: FLICKER
--------------------
Direct LCD drawing:
    Lcd.fillScreen(BLACK)  # User sees black flash!
    Lcd.fillRect(...)      # Then sees the rectangle

THE SOLUTION: DOUBLE BUFFERING
------------------------------
Draw to invisible canvas, then copy to screen:
    canvas.fillScreen(BLACK)   # Invisible
    canvas.fillRect(...)       # Still invisible
    canvas.push(0, 0)          # Copy all at once - no flicker!

Watch the left side flicker while the right side stays smooth!

CONTROLS:
---------
- ESC = Return to launcher
"""

import asyncio
import random

from M5 import Lcd, Widgets

import sys

# Path setup for imports (need parent of lib/ for "from lib.x" imports)
for lib_path in ["/flash", "/remote"]:
    if lib_path not in sys.path:
        sys.path.insert(0, lib_path)

from lib.app_base import AppBase


# =============================================================================
# SCREEN CONSTANTS
# =============================================================================

SCREEN_W = 240
SCREEN_H = 135
HALF_W = SCREEN_W // 2


# =============================================================================
# ANIMATION DEMO APP
# =============================================================================


class AnimDemo(AppBase):
    """
    Side-by-side animation comparison: Direct LCD vs Canvas.

    Left half: Direct LCD drawing (you'll see flicker)
    Right half: Canvas double buffering (smooth!)
    """

    def __init__(self):
        super().__init__()
        self.name = "Animation Demo"

        # Canvas for right side (double buffered)
        self._canvas = None

        # Two sets of balls
        self._balls_left = []   # Direct LCD (flickery)
        self._balls_right = []  # Canvas (smooth)

    def on_launch(self):
        """Create canvas and balls."""
        # Canvas for RIGHT half only
        self._canvas = Lcd.newCanvas(HALF_W, SCREEN_H)
        self._canvas.setFont(Widgets.FONTS.ASCII7)

        # Left side balls (warm colors)
        self._balls_left = self._create_balls(
            count=3,
            colors=[Lcd.COLOR.RED, Lcd.COLOR.YELLOW, Lcd.COLOR.ORANGE]
        )

        # Right side balls (cool colors)
        self._balls_right = self._create_balls(
            count=3,
            colors=[Lcd.COLOR.GREEN, Lcd.COLOR.CYAN, Lcd.COLOR.BLUE]
        )

    def on_view(self):
        """Clear screen and draw first frame."""
        Lcd.fillScreen(Lcd.COLOR.BLACK)
        self._draw_frame()

    async def on_run(self):
        """Animation loop - updates both sides each frame."""
        while True:
            # Update physics
            self._update_balls(self._balls_left)
            self._update_balls(self._balls_right)

            # Draw frame
            self._draw_frame()

            # ~40 FPS
            await asyncio.sleep_ms(25)

    def on_exit(self):
        """Clean up canvas."""
        if self._canvas:
            self._canvas.delete()
            self._canvas = None

    # =========================================================================
    # DRAWING
    # =========================================================================

    def _draw_frame(self):
        """Draw one frame - both sides."""
        # =================================================================
        # LEFT SIDE: Direct LCD (FLICKERY!)
        # =================================================================
        # Clear left half - USER SEES THIS FLASH!
        Lcd.fillRect(0, 0, HALF_W, SCREEN_H, Lcd.COLOR.BLACK)

        # Label
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(1)
        Lcd.setTextColor(Lcd.COLOR.RED, Lcd.COLOR.BLACK)
        Lcd.setCursor(5, 5)
        Lcd.print("DIRECT LCD")

        # Draw balls directly to screen
        for ball in self._balls_left:
            Lcd.fillRect(
                int(ball["x"]), int(ball["y"]),
                ball["size"], ball["size"],
                ball["color"]
            )

        # =================================================================
        # RIGHT SIDE: Canvas (SMOOTH!)
        # =================================================================
        canvas = self._canvas

        # Clear canvas - invisible to user
        canvas.fillScreen(Lcd.COLOR.BLACK)

        # Label
        canvas.setFont(Widgets.FONTS.ASCII7)
        canvas.setTextSize(1)
        canvas.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        canvas.setCursor(5, 5)
        canvas.print("CANVAS")

        # Draw balls to canvas - still invisible
        for ball in self._balls_right:
            canvas.fillRect(
                int(ball["x"]), int(ball["y"]),
                ball["size"], ball["size"],
                ball["color"]
            )

        # THE MAGIC: Push entire canvas at once!
        canvas.push(HALF_W, 0)

        # =================================================================
        # DIVIDER AND LABELS
        # =================================================================
        Lcd.drawLine(HALF_W, 0, HALF_W, SCREEN_H, Lcd.COLOR.WHITE)

        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(5, SCREEN_H - 12)
        Lcd.print("Flickery")
        Lcd.setCursor(HALF_W + 5, SCREEN_H - 12)
        Lcd.print("Smooth!")
        Lcd.setCursor(SCREEN_W - 55, SCREEN_H - 12)
        Lcd.print("ESC=back")

    # =========================================================================
    # BALL PHYSICS
    # =========================================================================

    def _create_balls(self, count, colors):
        """Create ball objects."""
        balls = []
        for i in range(count):
            balls.append({
                "x": float(random.randint(5, HALF_W - 20)),
                "y": float(random.randint(20, SCREEN_H - 30)),
                "vx": random.choice([-2.5, -2.0, 2.0, 2.5]),
                "vy": random.choice([-2.0, -1.5, 1.5, 2.0]),
                "size": 12,
                "color": colors[i % len(colors)],
            })
        return balls

    def _update_balls(self, balls):
        """Update positions and bounce off walls."""
        for ball in balls:
            ball["x"] += ball["vx"]
            ball["y"] += ball["vy"]

            # Bounce off walls
            if ball["x"] <= 0 or ball["x"] >= HALF_W - ball["size"]:
                ball["vx"] = -ball["vx"]
                ball["x"] = max(0, min(ball["x"], HALF_W - ball["size"]))

            if ball["y"] <= 18 or ball["y"] >= SCREEN_H - ball["size"] - 15:
                ball["vy"] = -ball["vy"]
                ball["y"] = max(18, min(ball["y"], SCREEN_H - ball["size"] - 15))


if __name__ == "__main__":
    # Standalone mode - run this app directly, ESC exits to REPL
    import M5
    M5.begin()
    Lcd.setRotation(1)
    Lcd.setBrightness(40)

    from lib.framework import Framework

    fw = Framework()
    fw.install(AnimDemo())
    fw.start()
