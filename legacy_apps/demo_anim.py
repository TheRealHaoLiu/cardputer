"""
Animation Demo - Double Buffering on M5Stack Cardputer
=======================================================

This demo teaches the MOST IMPORTANT graphics concept for smooth animation:
DOUBLE BUFFERING (also called off-screen rendering or canvas buffering).

THE PROBLEM: FLICKER
--------------------
When you animate by doing this:
    1. Clear screen (fillScreen)
    2. Draw objects at new positions

The user SEES the clear happen, then sees the draw. This creates flicker
because there's a moment where the screen is blank between frames.

THE SOLUTION: DOUBLE BUFFERING
------------------------------
Draw to an invisible buffer first, then copy the entire buffer to the
screen in one fast operation:
    1. Clear CANVAS (invisible, off-screen)
    2. Draw objects to CANVAS (still invisible)
    3. Copy entire CANVAS to screen (one atomic operation)

The user never sees an intermediate state - the screen updates all at once!

HOW TO USE CANVAS IN M5STACK:
-----------------------------
    # Create canvas (same size as screen)
    canvas = Lcd.newCanvas(240, 135)

    # Draw to canvas (same API as Lcd)
    canvas.fillScreen(Lcd.COLOR.BLACK)
    canvas.fillRect(x, y, w, h, color)
    canvas.print("Hello")

    # Copy canvas to screen (the magic!)
    canvas.push(0, 0)  # push to screen at position (0,0)

    # When done, free the memory
    canvas.delete()

CONCEPTS COVERED:
-----------------
1. Direct LCD Drawing - Why it flickers
2. Canvas/Double Buffering - How to avoid flicker
3. Animation Loop - Update positions, then redraw
4. Side-by-Side Comparison - See the difference yourself

CONTROLS:
---------
- Enter = Advance to next demo section
- ESC = Exit to launcher
"""

import random
import time

import M5
from M5 import Lcd, Widgets

SCREEN_W = 240
SCREEN_H = 135


class AnimDemo:
    """
    Interactive animation demo comparing direct LCD vs canvas rendering.

    The demo has 3 parts:
    1. Direct LCD drawing (flickery) - so you can see the problem
    2. Canvas double buffering (smooth) - the solution
    3. Side-by-side comparison - same animation, different technique
    """

    def __init__(self, keyboard):
        self.kb = keyboard
        self.running = False

    def run(self):
        self.running = True

        # =====================================================================
        # KEYBOARD SETUP
        # =====================================================================
        # Using flags for navigation between demo sections.
        # exit_flag = leave the demo entirely
        # next_flag = advance to next section

        exit_flag = False
        next_flag = False

        def on_key(keyboard):
            """
            Handle key events for demo navigation.

            IMPORTANT: We only set flags here, no heavy processing.
            This is called from interrupt context!
            """
            nonlocal exit_flag, next_flag
            while keyboard._keyevents:
                event = keyboard._keyevents.pop(0)
                if event.keycode == 0x1B:  # ESC key
                    exit_flag = True
                elif event.keycode == 0x0D or event.keycode == 0x0A:  # Enter
                    next_flag = True

        self.kb.set_keyevent_callback(on_key)

        # =====================================================================
        # HELPER FUNCTION: Wait for user input
        # =====================================================================

        def wait_for_key():
            """
            Wait for Enter (continue) or ESC (exit).
            Returns True if Enter was pressed, False if ESC.
            """
            nonlocal next_flag, exit_flag
            next_flag = False

            # Show prompt at bottom of screen
            Lcd.setFont(Widgets.FONTS.ASCII7)
            Lcd.setTextSize(1)
            Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)  # Green
            Lcd.setCursor(0, SCREEN_H - 10)
            Lcd.print("Enter=Next  ESC=Exit")

            # Wait for either flag
            while not next_flag and not exit_flag:
                M5.update()
                time.sleep(0.01)

            return not exit_flag  # True = continue, False = exit

        print("Animation Demo - Enter=Next, ESC=Exit")

        # =====================================================================
        # HELPER FUNCTION: Create animated balls
        # =====================================================================

        def create_balls(count=5):
            """
            Create a list of ball objects for animation.

            Each ball has:
            - x, y: Current position (float for smooth movement)
            - vx, vy: Velocity (pixels per frame)
            - size: Width/height in pixels
            - color: RGB565 color value

            WHY FLOATS FOR POSITION?
            ------------------------
            Using floats allows sub-pixel movement. A ball moving at 1.5 pixels
            per frame will smoothly alternate between 1 and 2 pixel jumps,
            looking smoother than integer-only movement.
            """
            balls = []
            colors = [
                Lcd.COLOR.RED,
                Lcd.COLOR.GREEN,
                Lcd.COLOR.BLUE,
                Lcd.COLOR.YELLOW,
                Lcd.COLOR.MAGENTA,
            ]
            for i in range(count):
                balls.append(
                    {
                        "x": float(random.randint(20, SCREEN_W - 40)),
                        "y": float(random.randint(20, SCREEN_H - 40)),
                        "vx": random.choice([-3.0, -2.0, 2.0, 3.0]),
                        "vy": random.choice([-3.0, -2.0, 2.0, 3.0]),
                        "size": 15,
                        "color": colors[i % len(colors)],
                    }
                )
            return balls

        def update_balls(balls):
            """
            Update ball positions and bounce off walls.

            BOUNCE LOGIC:
            -------------
            When a ball hits an edge, we reverse its velocity in that direction.
            This creates the classic "bouncing ball" effect.
            """
            for ball in balls:
                # Move ball by its velocity
                ball["x"] += ball["vx"]
                ball["y"] += ball["vy"]

                # Bounce off left/right edges
                if ball["x"] <= 0 or ball["x"] >= SCREEN_W - ball["size"]:
                    ball["vx"] = -ball["vx"]  # Reverse horizontal velocity

                # Bounce off top/bottom edges
                if ball["y"] <= 0 or ball["y"] >= SCREEN_H - ball["size"]:
                    ball["vy"] = -ball["vy"]  # Reverse vertical velocity

        # =====================================================================
        # DEMO 1: Direct LCD Drawing (FLICKERY)
        # =====================================================================
        # This demonstrates the WRONG way to do animation.
        # We clear the entire screen each frame, then redraw everything.
        # The user sees the screen go black between frames = FLICKER!

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)  # White
        Lcd.setCursor(10, 5)
        Lcd.print("1. Direct Lcd")

        Lcd.setTextSize(1)
        Lcd.setTextColor(Lcd.COLOR.RED, Lcd.COLOR.BLACK)  # Red = warning
        Lcd.setCursor(10, 25)
        Lcd.print("Watch the flicker!")

        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)  # Cyan = info
        Lcd.setCursor(10, 40)
        Lcd.print("Lcd.fillScreen() + Lcd.fillRect()")

        if not wait_for_key():
            self.running = False
            return self

        # Animate with direct LCD (flickery)
        balls = create_balls(5)
        next_flag = False

        while not exit_flag and not next_flag:
            M5.update()

            # THIS CAUSES FLICKER!
            # The screen goes black for a moment before we draw the balls.
            Lcd.fillScreen(Lcd.COLOR.BLACK)

            # Draw title (gets cleared and redrawn each frame)
            Lcd.setFont(Widgets.FONTS.ASCII7)
            Lcd.setTextSize(1)
            Lcd.setTextColor(Lcd.COLOR.RED, Lcd.COLOR.BLACK)  # Red
            Lcd.setCursor(5, 5)
            Lcd.print("DIRECT LCD - FLICKERY")

            # Update and draw balls directly to screen
            update_balls(balls)
            for ball in balls:
                Lcd.fillRect(
                    int(ball["x"]),
                    int(ball["y"]),
                    ball["size"],
                    ball["size"],
                    ball["color"],
                )

            Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
            Lcd.setCursor(0, SCREEN_H - 10)
            Lcd.print("Enter=Next  ESC=Exit")

            time.sleep(0.025)  # ~40 fps

        if exit_flag:
            self.running = False
            return self

        # =====================================================================
        # DEMO 2: Canvas Double Buffering (SMOOTH)
        # =====================================================================
        # This demonstrates the RIGHT way to do animation.
        # We draw to an off-screen canvas, then push it to the screen.
        # The screen update is atomic - no flicker!

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("2. Canvas Buffer")

        Lcd.setTextSize(1)
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)  # Green = good
        Lcd.setCursor(10, 25)
        Lcd.print("Smooth! No flicker!")

        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 40)
        Lcd.print("canvas = Lcd.newCanvas(w, h)")
        Lcd.setCursor(10, 52)
        Lcd.print("canvas.fillScreen() + fillRect()")
        Lcd.setCursor(10, 64)
        Lcd.print("canvas.push(x, y)")

        if not wait_for_key():
            self.running = False
            return self

        # Create canvas for double buffering
        # This allocates memory for an off-screen buffer
        canvas = Lcd.newCanvas(SCREEN_W, SCREEN_H)
        canvas.setFont(Widgets.FONTS.ASCII7)

        # Reset balls for fresh animation
        balls = create_balls(5)
        next_flag = False

        while not exit_flag and not next_flag:
            M5.update()

            # Draw everything to canvas (OFF-SCREEN, invisible to user)
            canvas.fillScreen(Lcd.COLOR.BLACK)

            # Draw title to canvas
            canvas.setTextSize(1)
            canvas.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)  # Green
            canvas.setCursor(5, 5)
            canvas.print("CANVAS BUFFER - SMOOTH")

            # Update and draw balls to canvas
            update_balls(balls)
            for ball in balls:
                canvas.fillRect(
                    int(ball["x"]),
                    int(ball["y"]),
                    ball["size"],
                    ball["size"],
                    ball["color"],
                )

            canvas.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
            canvas.setCursor(0, SCREEN_H - 10)
            canvas.print("Enter=Next  ESC=Exit")

            # THE MAGIC: Copy entire canvas to screen at once!
            # This is atomic - no intermediate states visible.
            canvas.push(0, 0)

            time.sleep(0.025)

        if exit_flag:
            canvas.delete()  # Free memory!
            self.running = False
            return self

        # =====================================================================
        # DEMO 3: Side-by-Side Comparison
        # =====================================================================
        # Split screen: left half uses direct draw, right half uses canvas.
        # Now you can directly compare the techniques!

        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("3. Side-by-Side")

        Lcd.setTextSize(1)
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 30)
        Lcd.print("Left=Direct  Right=Canvas")

        if not wait_for_key():
            canvas.delete()
            self.running = False
            return self

        # Create smaller canvas for right half only
        canvas.delete()
        half_w = SCREEN_W // 2
        canvas = Lcd.newCanvas(half_w, SCREEN_H)
        canvas.setFont(Widgets.FONTS.ASCII7)

        # Create separate ball sets for each side
        balls_left = []  # Will flicker (direct draw)
        balls_right = []  # Will be smooth (canvas)
        colors_left = [Lcd.COLOR.RED, Lcd.COLOR.YELLOW, Lcd.COLOR.MAGENTA]
        colors_right = [Lcd.COLOR.GREEN, Lcd.COLOR.CYAN, Lcd.COLOR.BLUE]

        for i in range(3):
            balls_left.append(
                {
                    "x": float(random.randint(5, half_w - 20)),
                    "y": float(random.randint(15, SCREEN_H - 25)),
                    "vx": random.choice([-2.0, 2.0]),
                    "vy": random.choice([-2.0, 2.0]),
                    "size": 12,
                    "color": colors_left[i],
                }
            )
            balls_right.append(
                {
                    "x": float(random.randint(5, half_w - 20)),
                    "y": float(random.randint(15, SCREEN_H - 25)),
                    "vx": random.choice([-2.0, 2.0]),
                    "vy": random.choice([-2.0, 2.0]),
                    "size": 12,
                    "color": colors_right[i],
                }
            )

        next_flag = False

        while not exit_flag and not next_flag:
            M5.update()

            # LEFT SIDE: Direct draw (flickery)
            # Clear just the left half
            Lcd.fillRect(0, 0, half_w, SCREEN_H, Lcd.COLOR.BLACK)
            Lcd.setTextSize(1)
            Lcd.setTextColor(Lcd.COLOR.RED, Lcd.COLOR.BLACK)  # Red label
            Lcd.setCursor(5, 5)
            Lcd.print("DIRECT")

            # Update and draw left balls
            for ball in balls_left:
                ball["x"] += ball["vx"]
                ball["y"] += ball["vy"]
                if ball["x"] <= 0 or ball["x"] >= half_w - ball["size"]:
                    ball["vx"] = -ball["vx"]
                if ball["y"] <= 15 or ball["y"] >= SCREEN_H - ball["size"]:
                    ball["vy"] = -ball["vy"]
                Lcd.fillRect(
                    int(ball["x"]),
                    int(ball["y"]),
                    ball["size"],
                    ball["size"],
                    ball["color"],
                )

            # RIGHT SIDE: Canvas (smooth)
            canvas.fillScreen(Lcd.COLOR.BLACK)
            canvas.setTextSize(1)
            canvas.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)  # Green label
            canvas.setCursor(5, 5)
            canvas.print("CANVAS")

            # Update and draw right balls
            for ball in balls_right:
                ball["x"] += ball["vx"]
                ball["y"] += ball["vy"]
                if ball["x"] <= 0 or ball["x"] >= half_w - ball["size"]:
                    ball["vx"] = -ball["vx"]
                if ball["y"] <= 15 or ball["y"] >= SCREEN_H - ball["size"]:
                    ball["vy"] = -ball["vy"]
                canvas.fillRect(
                    int(ball["x"]),
                    int(ball["y"]),
                    ball["size"],
                    ball["size"],
                    ball["color"],
                )

            # Push canvas to RIGHT half of screen
            canvas.push(half_w, 0)

            # Draw divider line
            Lcd.drawLine(half_w, 0, half_w, SCREEN_H, Lcd.COLOR.WHITE)

            time.sleep(0.025)

        # =====================================================================
        # CLEANUP
        # =====================================================================
        # IMPORTANT: Always delete canvas when done to free memory!
        # MicroPython has limited RAM, and canvases use a lot of it.

        canvas.delete()

        # Show completion message
        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.drawCenterString("Demo Complete!", 120, 50)

        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(20, 80)
        Lcd.print("See demo_anim.py for code")

        wait_for_key()

        self.running = False
        print("Animation Demo exited")
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

    AnimDemo(kb).run()
