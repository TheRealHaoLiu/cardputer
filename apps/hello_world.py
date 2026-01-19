"""
Hello World - App Template for Cardputer ADV
=============================================

This is the MINIMAL APP TEMPLATE. Copy this file to create new apps.
It demonstrates the required structure and patterns for Cardputer apps.

CONCEPTS COVERED:
-----------------
1. App Class Structure - __init__ and run() methods
2. Keyboard Callbacks - Non-blocking input handling
3. Flag-Based Communication - Between callback and main loop
4. The Main Loop Pattern - M5.update() and sleep
5. Graceful Exit - How to return to the launcher

TO CREATE A NEW APP:
--------------------
1. Copy this file: cp apps/hello_world.py apps/my_app.py
2. Rename the class: class MyApp:
3. Update __name__ == "__main__" block: MyApp(kb).run()
4. Add to APP_REGISTRY in main.py:
   ("my_app", "MyApp", "My App"),

RUNNING STANDALONE (without launcher):
--------------------------------------
    uv run poe run apps/hello_world.py

RUNNING FROM LAUNCHER:
----------------------
    uv run poe run
    # Then select from menu

APP LIFECYCLE:
--------------
1. Launcher imports your module and gets your class
2. Launcher calls YourClass(keyboard) - store the keyboard!
3. Launcher calls instance.run() - your main logic here
4. When run() returns, launcher takes over again

KEYBOARD HANDLING PATTERN:
--------------------------
The keyboard uses callbacks - a function that gets called when keys are pressed.
But there's a critical rule: NEVER DO SLOW OPERATIONS IN CALLBACKS!

Why? Callbacks run in an "interrupt context" - they pause normal execution.
If you do something slow (like drawing to the screen), you can cause:
- Visual glitches
- Missed key events
- System hangs

THE SOLUTION: Use flags!
1. In the callback: just set a flag (self.exit_requested = True)
2. In the main loop: check flags and do the actual work

This pattern is used throughout embedded programming.
"""

import time  # For sleep() to prevent busy-waiting

import M5  # M5Stack hardware layer - MUST call M5.update() in main loop
from M5 import Lcd, Widgets  # LCD drawing and fonts

# =============================================================================
# SCREEN CONSTANTS
# =============================================================================
# The Cardputer ADV has a 240x135 pixel LCD in landscape orientation.
# Define these once and reuse throughout your app.

SCREEN_W = 240  # Screen width in pixels
SCREEN_H = 135  # Screen height in pixels


class HelloWorld:
    """
    Minimal app template for Cardputer ADV.

    REQUIRED INTERFACE:
    -------------------
    1. __init__(self, keyboard) - Constructor, receives keyboard instance
    2. run(self) - Main entry point, called by launcher

    OPTIONAL BUT RECOMMENDED:
    -------------------------
    - self.running flag - To track if app is active
    - self.kb - Store keyboard reference for later use
    """

    def __init__(self, keyboard):
        """
        Initialize the app.

        This is called by the launcher when your app is selected.
        Store any references you'll need in run().

        Args:
            keyboard: KeyboardI2C instance from the launcher.
                     Use this to register key callbacks.

        WHAT TO DO HERE:
        ----------------
        - Store the keyboard reference
        - Initialize any state variables
        - DON'T draw to screen yet (wait for run())
        - DON'T register callbacks yet (wait for run())
        """
        self.kb = keyboard  # Store keyboard for later use
        self.running = False  # Track if app is currently running

    def run(self):
        """
        Main app entry point. Called by launcher when app is selected.

        This method should:
        1. Set up keyboard callbacks
        2. Draw the initial UI
        3. Enter a main loop
        4. Clean up and return when done

        Returns:
            self - Must return self for launcher compatibility.
                  (This allows method chaining if needed)
        """
        self.running = True

        # =====================================================================
        # KEYBOARD SETUP
        # =====================================================================
        # We use the FLAG PATTERN for keyboard handling:
        # 1. Define flags (just regular Python variables)
        # 2. Define a callback that sets flags
        # 3. Check flags in the main loop
        #
        # WHY USE nonlocal?
        # -----------------
        # The callback function is defined inside run(), but needs to modify
        # variables also defined in run(). Python requires 'nonlocal' to
        # indicate we want to modify the outer variable, not create a new one.

        exit_flag = False  # Set to True when ESC is pressed

        def on_key(keyboard):
            """
            Keyboard callback - called when ANY key is pressed.

            Args:
                keyboard: The KeyboardI2C instance (same as self.kb)

            IMPORTANT RULES:
            ----------------
            1. Keep this function FAST - no Lcd drawing, no delays
            2. Just set flags or store data
            3. Do the real work in the main loop

            keyboard._keyevents is a list of KeyEvent objects.
            We need to pop events from this list to process them.
            """
            nonlocal exit_flag  # We need to modify exit_flag from outer scope

            # Process ALL pending key events (there might be multiple)
            while keyboard._keyevents:
                event = keyboard._keyevents.pop(0)  # Get first event

                # Check for ESC key (0x1B = 27 in decimal)
                if event.keycode == 0x1B:
                    exit_flag = True

                # Handle other keys here...
                # Example:
                # elif event.keycode == ord('a'):
                #     a_pressed = True
                # elif event.keycode == 0x0D:  # Enter
                #     enter_pressed = True

        # Register our callback - keyboard will call on_key() when keys pressed
        self.kb.set_keyevent_callback(on_key)

        # =====================================================================
        # DRAW INITIAL UI
        # =====================================================================
        # Draw your app's interface here.
        # This runs once at startup - update the display in the main loop
        # if you need dynamic content.

        # Clear screen to black
        # Use Lcd.COLOR.* constants for colors (e.g., Lcd.COLOR.BLACK, Lcd.COLOR.GREEN)
        Lcd.fillScreen(Lcd.COLOR.BLACK)

        # Draw title using a nice font
        # Available fonts in Widgets.FONTS:
        #   ASCII7 - Monospace, 6x9 base (good for text editors)
        #   DejaVu9/12/18/24/40/56/72 - Proportional, various sizes
        Lcd.setFont(Widgets.FONTS.DejaVu18)
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        # drawCenterString centers text at the given X coordinate
        Lcd.drawCenterString("Hello World!", SCREEN_W // 2, 40)

        # Draw subtitle
        Lcd.setFont(Widgets.FONTS.DejaVu12)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.drawCenterString("This is an app template", SCREEN_W // 2, 70)

        # Draw footer with controls
        # ASCII7 at size 1 is tiny but readable for hints
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
        Lcd.setCursor(0, SCREEN_H - 10)  # Bottom of screen
        Lcd.print("ESC=Exit")

        # =====================================================================
        # MAIN LOOP
        # =====================================================================
        # Every app needs a main loop that:
        # 1. Calls M5.update() - REQUIRED for hardware events
        # 2. Checks flags set by keyboard callback
        # 3. Updates display if needed
        # 4. Sleeps briefly to prevent busy-waiting
        #
        # The loop continues until exit_flag is True (ESC pressed)

        while not exit_flag:
            # M5.update() processes hardware events:
            # - Triggers keyboard callbacks
            # - Updates internal state
            # - MUST be called regularly!
            M5.update()

            # Your app logic goes here...
            # - Check flags from keyboard callback
            # - Update game state
            # - Animate things
            # - etc.

            # Sleep to prevent busy-waiting
            # 0.02 seconds = 20ms = 50 updates per second
            # Adjust based on your app's needs:
            # - Games: 0.016 (60 fps) to 0.033 (30 fps)
            # - UI: 0.02 to 0.05 is usually fine
            # - Battery-conscious: 0.1 or higher
            time.sleep(0.02)

        # =====================================================================
        # CLEANUP
        # =====================================================================
        # We're exiting - clean up any resources.
        # The launcher will reset the keyboard callback, so we don't need to.

        self.running = False
        print("Hello World exited")  # Visible in REPL/logs for debugging
        return self  # Required - launcher expects this


# =============================================================================
# STANDALONE EXECUTION
# =============================================================================
# This block runs when you execute the file directly:
#   uv run poe run apps/hello_world.py
#
# It won't run when imported by the launcher (because __name__ != "__main__").
#
# This is useful for testing a single app without going through the menu.

if __name__ == "__main__":
    # We need to do the same hardware init that main.py does

    import M5
    import machine
    from hardware import KeyboardI2C
    from M5 import Lcd

    # Initialize M5Stack hardware
    M5.begin()

    # Set up LCD
    Lcd.setRotation(1)  # Landscape mode
    Lcd.setBrightness(40)  # Medium brightness

    # Set up I2C keyboard (Cardputer ADV specific!)
    # SCL=9, SDA=8, INT=11 are the Cardputer ADV pins
    i2c1 = machine.I2C(1, scl=machine.Pin(9), sda=machine.Pin(8), freq=400000)
    intr_pin = machine.Pin(11, mode=machine.Pin.IN, pull=None)
    kb = KeyboardI2C(i2c1, intr_pin=intr_pin, mode=KeyboardI2C.ASCII_MODE)

    # Create and run the app
    HelloWorld(kb).run()
