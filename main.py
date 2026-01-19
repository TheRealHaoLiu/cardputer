"""
Cardputer Framework Main Entry Point
=====================================

This is the main entry point that runs when the device boots.
It initializes the hardware, sets up the app framework, and starts the launcher.

ARCHITECTURE OVERVIEW:
----------------------
The framework follows a simple app-based architecture:

    Framework
        └── manages multiple Apps
            └── each App inherits from AppBase
                └── implements lifecycle methods (on_view, on_run, etc.)

The Framework:
- Maintains a list of installed apps
- Runs an async event loop
- Polls the keyboard and routes input to the current app
- Handles ESC key to return to launcher

ADDING NEW APPS:
----------------
1. Create a new file in apps/ (copy hello_world.py as template)
2. Import your app class here
3. Call fw.install(YourApp()) in main()

CONTROLS:
---------
- ; (semicolon) or UP arrow = Navigate up in menu
- . (period) or DOWN arrow = Navigate down in menu
- Enter = Launch selected app
- ESC = Return to launcher from any app
"""

# =============================================================================
# PATH SETUP
# =============================================================================
# MicroPython needs to know where to find our modules.
# We add both /flash (deployed) and /remote (development mount) paths.
# This allows the same code to work in both modes.

import sys

for path in ["/flash/lib", "/remote/lib", "/flash/apps", "/remote/apps"]:
    if path not in sys.path:
        sys.path.insert(0, path)  # Insert at front so our code takes priority

# =============================================================================
# HARDWARE INITIALIZATION
# =============================================================================
# M5.begin() must be called before using any M5Stack hardware.
# This initializes the display, speaker, and other peripherals.

import M5
from M5 import Lcd

M5.begin()  # Initialize M5Stack hardware

# LCD Setup
# ---------
# The Cardputer's LCD is 240x135 pixels.
# Rotation 1 = landscape mode (wider than tall)
# Brightness 40 is moderate (range 0-255)

Lcd.setRotation(1)  # Landscape orientation
Lcd.setBrightness(40)  # Moderate brightness (saves battery)
Lcd.fillScreen(Lcd.COLOR.BLACK)  # Clear to black

# =============================================================================
# FRAMEWORK AND APP IMPORTS
# =============================================================================
# Import the framework components and all apps.
# Apps must be imported AFTER path setup above.

from lib.framework import Framework
from apps.launcher import LauncherApp
from apps.hello_world import HelloWorld
from apps.anim_demo import AnimDemo

# To add a new app:
# 1. Create apps/my_app.py (inherit from AppBase)
# 2. Add: from apps.my_app import MyApp
# 3. Add: fw.install(MyApp()) in main() below


# =============================================================================
# MAIN FUNCTION
# =============================================================================


def main():
    """
    Set up the framework and start the main event loop.

    This function:
    1. Creates the Framework instance
    2. Creates and installs the launcher (home screen)
    3. Installs all apps
    4. Starts the framework (blocks forever)
    """
    print("Starting Cardputer Framework...")

    # Create the framework instance
    # The framework manages apps and runs the main event loop
    fw = Framework()

    # Create and install the launcher
    # The launcher is special - it's both an app AND the home screen
    # install_launcher() tells the framework "ESC returns here"
    # install() adds it to the app list so it appears in menus
    launcher = LauncherApp()
    fw.install_launcher(launcher)
    fw.install(launcher)

    # Install apps
    # Each app is an instance of an AppBase subclass
    # The launcher will show all installed apps (except itself)
    fw.install(HelloWorld())
    fw.install(AnimDemo())

    # Add more apps here:
    # fw.install(MyOtherApp())

    print(f"Installed {len(fw.get_apps()) - 1} apps")  # -1 excludes launcher
    print("Framework ready. ESC returns to launcher.")

    # Start the framework
    # This runs forever - it's the main event loop
    # It polls keyboard, routes events to apps, handles ESC, etc.
    fw.start()


# =============================================================================
# ENTRY POINT
# =============================================================================
# In MicroPython, main.py runs automatically on boot.
# We also handle being exec()'d during development (mpremote mount).

if __name__ == "__main__":
    main()
else:
    # When exec()'d via mpremote, __name__ is not "__main__"
    main()
