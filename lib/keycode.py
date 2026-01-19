"""
KeyCode constants and utilities for keyboard handling.

Provides unified access to key codes from the firmware's unit.KeyCode,
with fallback definitions for non-device testing.
"""

# Try to import KeyCode constants from firmware
# Fall back to our own definitions if not available
try:
    from unit import KeyCode
except ImportError:

    class KeyCode:
        """Key code constants for special keys (ASCII codes)."""

        KEYCODE_ESC = 0x1B  # Escape key
        KEYCODE_ENTER = 0x0D  # Enter/Return key
        KEYCODE_TAB = 0x09  # Tab key (but see HID_TAB below)
        KEYCODE_BACKSPACE = 0x08  # Backspace key
        KEYCODE_DEL = 0x7F  # Delete key
        KEYCODE_SPACE = 0x20  # Space key
        KEYCODE_UP = 0x26  # Up arrow
        KEYCODE_DOWN = 0x28  # Down arrow
        KEYCODE_LEFT = 0x25  # Left arrow
        KEYCODE_RIGHT = 0x27  # Right arrow
        KEYCODE_UNKNOWN = 0x00  # Unknown key


# Keyboard quirks:
# Tab sends HID scancode 0x2B instead of ASCII 0x09
# This overlaps with '+' (Shift+=), so check shift state to differentiate
HID_TAB = 0x2B

# Modifier key masks from firmware
try:
    from hardware.keyboard.asciimap import (
        KEY_MOD_LALT,
        KEY_MOD_LCTRL,
        KEY_MOD_LMETA,
        KEY_MOD_LSHIFT,
        KEY_MOD_RALT,
        KEY_MOD_RCTRL,
        KEY_MOD_RMETA,
        KEY_MOD_RSHIFT,
    )
except ImportError:
    # Fallback values for non-device testing
    KEY_MOD_LCTRL = 0x01
    KEY_MOD_LSHIFT = 0x02
    KEY_MOD_LALT = 0x04
    KEY_MOD_LMETA = 0x08
    KEY_MOD_RCTRL = 0x10
    KEY_MOD_RSHIFT = 0x20
    KEY_MOD_RALT = 0x40
    KEY_MOD_RMETA = 0x80


def get_key_name(key, is_shifted=False):
    """
    Get human-readable name for special keys.

    Args:
        key: The key code
        is_shifted: Whether shift is currently held

    Returns:
        String name for special keys, or None for regular keys
    """
    # Tab sends 0x2B (same as '+'), differentiate by shift state
    if key == HID_TAB and not is_shifted:
        return "TAB"
    names = {
        KeyCode.KEYCODE_ESC: "ESC",
        KeyCode.KEYCODE_ENTER: "ENTER",
        KeyCode.KEYCODE_BACKSPACE: "BKSP",
        KeyCode.KEYCODE_TAB: "TAB",
        KeyCode.KEYCODE_DEL: "DEL",
        KeyCode.KEYCODE_SPACE: "SPACE",
        KeyCode.KEYCODE_UP: "UP",
        KeyCode.KEYCODE_DOWN: "DOWN",
        KeyCode.KEYCODE_LEFT: "LEFT",
        KeyCode.KEYCODE_RIGHT: "RIGHT",
    }
    return names.get(key)


def decode_modifiers(mask):
    """
    Decode modifier bitmask to readable string.

    Args:
        mask: The modifier bitmask from KeyboardI2C._modifier_mask

    Returns:
        String like "Ctrl+Shft" or empty string if no modifiers
    """
    mods = []
    if mask & KEY_MOD_LCTRL:
        mods.append("Ctrl")
    if mask & KEY_MOD_LSHIFT:
        mods.append("Shft")
    if mask & KEY_MOD_LALT:
        mods.append("Alt")
    if mask & KEY_MOD_LMETA:
        mods.append("Opt")
    # Right-side modifiers (not on Cardputer, but included for completeness)
    if mask & KEY_MOD_RCTRL:
        mods.append("RCtrl")
    if mask & KEY_MOD_RSHIFT:
        mods.append("RShft")
    if mask & KEY_MOD_RALT:
        mods.append("RAlt")
    if mask & KEY_MOD_RMETA:
        mods.append("ROpt")
    return "+".join(mods) if mods else ""
