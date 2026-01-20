"""
Settings App Modules
====================

Shared constants and utilities for settings tabs.
"""

from M5 import Lcd

# =============================================================================
# Layout Constants
# =============================================================================
SCREEN_W = 240
SCREEN_H = 135

# Colors
BLACK = Lcd.COLOR.BLACK
WHITE = Lcd.COLOR.WHITE
CYAN = Lcd.COLOR.CYAN
GREEN = Lcd.COLOR.GREEN
YELLOW = Lcd.COLOR.YELLOW
RED = 0xFF0000
GRAY = 0x888888
DARK_GRAY = 0x444444

# Tab bar layout
TAB_Y = 0
TAB_H = 16
TAB_NAMES = ["WiFi", "Display", "Sound", "System", "About"]

# Content area
CONTENT_Y = TAB_H + 2
CONTENT_H = SCREEN_H - TAB_H - 14

# Footer
FOOTER_Y = SCREEN_H - 12


class TabBase:
    """
    Base class for settings tabs.

    Each tab should implement:
    - draw(app): Draw the tab content
    - handle_key(app, key): Handle key press, return True if handled
    """

    def draw(self, app):
        """Draw tab content. Override in subclass."""
        pass

    def handle_key(self, app, key):
        """Handle key press. Return True if handled. Override in subclass."""
        return False
