# Animation Demo - Reference for smooth animation on M5Stack Cardputer
# Compares direct LCD drawing (flickery) vs canvas double buffering (smooth)
# Press Enter/OK to advance, ESC to exit

import random
import time

import M5
from M5 import Lcd, Widgets

SCREEN_W = 240
SCREEN_H = 135


class AnimDemo:
    def __init__(self, keyboard):
        self.kb = keyboard
        self.running = False

    def run(self):
        self.running = True
        exit_flag = False
        next_flag = False

        # =====================================================================
        # KEYBOARD HANDLING
        # =====================================================================
        # Use a local function with nonlocal to set flags
        # IMPORTANT: Never call blocking code (like run()) from inside callback
        # The callback runs in interrupt context - just set flags here

        def on_key(keyboard):
            nonlocal exit_flag, next_flag
            while keyboard._keyevents:
                event = keyboard._keyevents.pop(0)
                if event.keycode == 0x1B:  # ESC key
                    exit_flag = True
                elif event.keycode == 0x0D or event.keycode == 0x0A:  # Enter
                    next_flag = True

        self.kb.set_keyevent_callback(on_key)

        def wait_for_key():
            """Wait for Enter to continue or ESC to exit"""
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

        print("Animation Demo - Enter=Next, ESC=Exit")

        # =====================================================================
        # CREATE ANIMATED OBJECTS
        # =====================================================================
        # Each ball has position (x,y), velocity (vx,vy), size, and color
        # RGB565 colors: 0xF800=Red, 0x07E0=Green, 0x001F=Blue,
        #                0xFFE0=Yellow, 0xF81F=Magenta, 0x07FF=Cyan

        def create_balls(count=5):
            balls = []
            for i in range(count):
                balls.append(
                    {
                        "x": float(random.randint(20, SCREEN_W - 40)),
                        "y": float(random.randint(20, SCREEN_H - 40)),
                        "vx": random.choice([-3.0, -2.0, 2.0, 3.0]),
                        "vy": random.choice([-3.0, -2.0, 2.0, 3.0]),
                        "size": 15,
                        "color": [0xF800, 0x07E0, 0x001F, 0xFFE0, 0xF81F][i % 5],
                    }
                )
            return balls

        def update_balls(balls):
            """Update ball positions and bounce off walls"""
            for ball in balls:
                ball["x"] += ball["vx"]
                ball["y"] += ball["vy"]
                if ball["x"] <= 0 or ball["x"] >= SCREEN_W - ball["size"]:
                    ball["vx"] = -ball["vx"]
                if ball["y"] <= 0 or ball["y"] >= SCREEN_H - ball["size"]:
                    ball["vy"] = -ball["vy"]

        # =====================================================================
        # DEMO 1: Direct LCD Drawing (FLICKERY)
        # =====================================================================
        # Drawing directly to Lcd causes flicker because:
        # 1. fillScreen() clears everything - screen goes black
        # 2. Then we draw objects - they appear
        # 3. This clear/draw cycle is visible to the eye as flicker

        Lcd.fillScreen(0x0000)
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(2)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 5)
        Lcd.print("1. Direct Lcd")

        Lcd.setTextSize(1)
        Lcd.setTextColor(0xF800, 0x0000)  # Red warning
        Lcd.setCursor(10, 25)
        Lcd.print("Watch the flicker!")

        Lcd.setTextColor(0x07FF, 0x0000)
        Lcd.setCursor(10, 40)
        Lcd.print("Lcd.fillScreen() + Lcd.fillRect()")

        if not wait_for_key():
            self.running = False
            return self

        balls = create_balls(5)
        next_flag = False
        frame_count = 0

        # Run flickery animation until Enter or ESC
        while not exit_flag and not next_flag:
            M5.update()

            # THIS CAUSES FLICKER - clearing entire screen each frame
            Lcd.fillScreen(0x0000)

            # Draw title
            Lcd.setFont(Widgets.FONTS.ASCII7)
            Lcd.setTextSize(1)
            Lcd.setTextColor(0xF800, 0x0000)
            Lcd.setCursor(5, 5)
            Lcd.print("DIRECT LCD - FLICKERY")

            # Update and draw balls directly to Lcd
            update_balls(balls)
            for ball in balls:
                Lcd.fillRect(
                    int(ball["x"]), int(ball["y"]), ball["size"], ball["size"], ball["color"]
                )

            Lcd.setTextColor(0x07E0, 0x0000)
            Lcd.setCursor(0, SCREEN_H - 10)
            Lcd.print("Enter=Next  ESC=Exit")

            time.sleep(0.025)
            frame_count += 1

        if exit_flag:
            self.running = False
            return self

        # =====================================================================
        # DEMO 2: Canvas Double Buffering (SMOOTH)
        # =====================================================================
        # Lcd.newCanvas(w, h) creates an off-screen buffer
        # Draw everything to canvas first (invisible to user)
        # Then push() atomically copies entire buffer to screen
        # No flicker because screen update is instantaneous

        Lcd.fillScreen(0x0000)
        Lcd.setTextSize(2)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 5)
        Lcd.print("2. Canvas Buffer")

        Lcd.setTextSize(1)
        Lcd.setTextColor(0x07E0, 0x0000)  # Green = good
        Lcd.setCursor(10, 25)
        Lcd.print("Smooth! No flicker!")

        Lcd.setTextColor(0x07FF, 0x0000)
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
        canvas = Lcd.newCanvas(SCREEN_W, SCREEN_H)
        canvas.setFont(Widgets.FONTS.ASCII7)

        balls = create_balls(5)
        next_flag = False

        # Run smooth animation until Enter or ESC
        while not exit_flag and not next_flag:
            M5.update()

            # Draw everything to off-screen canvas (no flicker)
            canvas.fillScreen(0x0000)

            # Draw title to canvas
            canvas.setTextSize(1)
            canvas.setTextColor(0x07E0, 0x0000)
            canvas.setCursor(5, 5)
            canvas.print("CANVAS BUFFER - SMOOTH")

            # Update and draw balls to canvas
            update_balls(balls)
            for ball in balls:
                canvas.fillRect(
                    int(ball["x"]), int(ball["y"]), ball["size"], ball["size"], ball["color"]
                )

            canvas.setTextColor(0x07E0, 0x0000)
            canvas.setCursor(0, SCREEN_H - 10)
            canvas.print("Enter=Next  ESC=Exit")

            # Atomic blit to screen - this is the magic!
            canvas.push(0, 0)

            time.sleep(0.025)

        if exit_flag:
            canvas.delete()
            self.running = False
            return self

        # =====================================================================
        # DEMO 3: Side-by-Side Comparison
        # =====================================================================
        # Split screen: left half direct draw, right half canvas

        Lcd.fillScreen(0x0000)
        Lcd.setTextSize(2)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(10, 5)
        Lcd.print("3. Side-by-Side")

        Lcd.setTextSize(1)
        Lcd.setTextColor(0x07FF, 0x0000)
        Lcd.setCursor(10, 30)
        Lcd.print("Left=Direct  Right=Canvas")

        if not wait_for_key():
            canvas.delete()
            self.running = False
            return self

        # Create a smaller canvas for right half only
        canvas.delete()
        half_w = SCREEN_W // 2
        canvas = Lcd.newCanvas(half_w, SCREEN_H)
        canvas.setFont(Widgets.FONTS.ASCII7)

        # Create balls for each side
        balls_left = []
        balls_right = []
        for i in range(3):
            balls_left.append(
                {
                    "x": float(random.randint(5, half_w - 20)),
                    "y": float(random.randint(15, SCREEN_H - 25)),
                    "vx": random.choice([-2.0, 2.0]),
                    "vy": random.choice([-2.0, 2.0]),
                    "size": 12,
                    "color": [0xF800, 0xFFE0, 0xF81F][i],
                }
            )
            balls_right.append(
                {
                    "x": float(random.randint(5, half_w - 20)),
                    "y": float(random.randint(15, SCREEN_H - 25)),
                    "vx": random.choice([-2.0, 2.0]),
                    "vy": random.choice([-2.0, 2.0]),
                    "size": 12,
                    "color": [0x07E0, 0x07FF, 0x001F][i],
                }
            )

        next_flag = False

        while not exit_flag and not next_flag:
            M5.update()

            # LEFT SIDE: Direct draw (flickery)
            Lcd.fillRect(0, 0, half_w, SCREEN_H, 0x0000)
            Lcd.setTextSize(1)
            Lcd.setTextColor(0xF800, 0x0000)
            Lcd.setCursor(5, 5)
            Lcd.print("DIRECT")

            for ball in balls_left:
                ball["x"] += ball["vx"]
                ball["y"] += ball["vy"]
                if ball["x"] <= 0 or ball["x"] >= half_w - ball["size"]:
                    ball["vx"] = -ball["vx"]
                if ball["y"] <= 15 or ball["y"] >= SCREEN_H - ball["size"]:
                    ball["vy"] = -ball["vy"]
                Lcd.fillRect(
                    int(ball["x"]), int(ball["y"]), ball["size"], ball["size"], ball["color"]
                )

            # RIGHT SIDE: Canvas (smooth)
            canvas.fillScreen(0x0000)
            canvas.setTextSize(1)
            canvas.setTextColor(0x07E0, 0x0000)
            canvas.setCursor(5, 5)
            canvas.print("CANVAS")

            for ball in balls_right:
                ball["x"] += ball["vx"]
                ball["y"] += ball["vy"]
                if ball["x"] <= 0 or ball["x"] >= half_w - ball["size"]:
                    ball["vx"] = -ball["vx"]
                if ball["y"] <= 15 or ball["y"] >= SCREEN_H - ball["size"]:
                    ball["vy"] = -ball["vy"]
                canvas.fillRect(
                    int(ball["x"]), int(ball["y"]), ball["size"], ball["size"], ball["color"]
                )

            canvas.push(half_w, 0)  # Push to right half

            # Draw divider line
            Lcd.drawLine(half_w, 0, half_w, SCREEN_H, 0xFFFF)

            time.sleep(0.025)

        # =====================================================================
        # CLEANUP
        # =====================================================================
        # Always delete canvas when done to free memory

        canvas.delete()

        # Show completion
        Lcd.fillScreen(0x0000)
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(0x07E0, 0x0000)
        Lcd.drawCenterString("Demo Complete!", 120, 50)

        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextColor(0xFFFF, 0x0000)
        Lcd.setCursor(20, 80)
        Lcd.print("See demo_anim.py for code")

        wait_for_key()

        self.running = False
        print("Animation Demo exited")
        return self
