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
2. The launcher auto-discovers apps from the apps/ directory

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
# MicroPython adds the script's directory to sys.path automatically.
# So when running /remote/main.py, /remote is already in path and
# "from libs.framework" finds /remote/libs/framework.py.
#
# We only need to add the apps directory for dynamic app discovery.

import os
import sys

# Detect run mode and add apps path for dynamic discovery
try:
    os.stat("/remote/apps")
    if "/remote/apps" not in sys.path:
        sys.path.insert(0, "/remote/apps")
except OSError:
    if "/flash/apps" not in sys.path:
        sys.path.insert(0, "/flash/apps")

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

from apps.launcher import LauncherApp
from libs.framework import Framework

# Apps are discovered automatically from the apps/ directory.
# To add a new app, just create apps/my_app.py (inherit from AppBase).
# The launcher will find and load it automatically.


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

    # Apps are discovered automatically when the launcher starts.
    # See lib/framework.py discover_apps() for the discovery logic.

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
