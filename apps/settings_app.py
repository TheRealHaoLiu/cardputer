"""
Settings App - Device Configuration
====================================

Tabbed settings interface for configuring the Cardputer.

This app demonstrates:
- Tab-based navigation UI pattern
- Consistent keyboard controls across tabs
- Menu-driven interaction (not complex key combos)

TABS:
    WiFi    - Network configuration
    Display - Brightness control
    Sound   - Volume control
    System  - Boot options, memory, reboot
    About   - Device information

CONTROLS:
    Tab     = Next tab
    ;/.     = Navigate menu items (up/down)
    Enter   = Select/confirm
    ESC     = Exit to launcher
"""

import asyncio
import sys

# Add lib paths for imports (needed on device)
for path in ["/flash", "/remote"]:
    if path not in sys.path:
        sys.path.insert(0, path)

from M5 import Lcd, Widgets

from lib.app_base import AppBase
from lib.keycode import HID_TAB, KEY_NAV_DOWN, KEY_NAV_LEFT, KEY_NAV_RIGHT, KEY_NAV_UP, KeyCode

# Tab indices for easy reference
TAB_WIFI = 0
TAB_DISPLAY = 1
TAB_SOUND = 2
TAB_SYSTEM = 3
TAB_ABOUT = 4

# =============================================================================
# Layout Constants
# =============================================================================
# Screen dimensions for Cardputer (landscape mode)
SCREEN_W = 240
SCREEN_H = 135

# Colors - using Lcd.COLOR for hardware compatibility
BLACK = Lcd.COLOR.BLACK
WHITE = Lcd.COLOR.WHITE
CYAN = Lcd.COLOR.CYAN
GREEN = Lcd.COLOR.GREEN
YELLOW = Lcd.COLOR.YELLOW
GRAY = 0x888888  # Medium gray for inactive elements
DARK_GRAY = 0x444444  # Dark gray for backgrounds

# Tab bar layout
TAB_Y = 0  # Tab bar starts at top of screen
TAB_H = 16  # Height of tab bar in pixels
TAB_NAMES = ["WiFi", "Display", "Sound", "System", "About"]

# Content area - between tab bar and footer
CONTENT_Y = TAB_H + 2
CONTENT_H = SCREEN_H - TAB_H - 14  # Leave room for footer

# Footer - navigation hints at bottom
FOOTER_Y = SCREEN_H - 12


# =============================================================================
# Settings App
# =============================================================================


class SettingsApp(AppBase):
    """
    Tabbed settings application.

    This is a container that manages multiple "tabs" of settings.
    Each tab will be implemented as a separate drawing/handling section.
    """

    def __init__(self):
        super().__init__()
        self.name = "Settings"
        self._current_tab = 0  # Index of active tab (0 = WiFi)

        # Display tab state
        self._brightness = 128  # Current brightness (0-255)
        self._brightness_saved = 128  # Last saved brightness value

        # Sound tab state
        self._volume = 128  # Current volume (0-255)
        self._volume_saved = 128  # Last saved volume
        self._muted = False  # Mute state
        self._speaker = None  # Speaker instance (lazy init)

        # System tab state
        self._boot_option = 1  # 0=main.py, 1=Launcher, 2=Setup
        self._boot_option_saved = 1
        self._boot_labels = ["main.py", "Launcher", "Setup"]

        # WiFi tab state
        self._wifi_enabled = False
        self._wifi_networks = []  # List of (ssid, rssi, security) tuples
        self._wifi_selected = 0  # Selected network index
        self._wifi_scanning = False
        self._wifi_connected_ssid = None
        self._wifi_password = ""  # Password being entered
        self._wifi_input_mode = False  # True when entering password
        self._wlan = None  # WLAN instance

        print("[settings] App initialized")

    def on_launch(self):
        """Called when app becomes active."""
        # Read current brightness from LCD
        try:
            self._brightness = Lcd.getBrightness()
            self._brightness_saved = self._brightness
        except Exception:
            pass  # Keep default if read fails
        print("[settings] Launched, starting on tab:", TAB_NAMES[self._current_tab])

    def on_view(self):
        """
        Draw the complete settings interface.

        Draws directly to LCD for simplicity.
        """
        print("[settings] Drawing view, tab:", TAB_NAMES[self._current_tab])

        # Clear screen
        Lcd.fillScreen(BLACK)

        # Draw all UI elements
        self._draw_tabs()
        self._draw_content()
        self._draw_footer()

        print("[settings] View drawn")

    def _draw_tabs(self):
        """
        Draw the tab bar at the top of the screen.

        Each tab is a clickable area showing the tab name.
        The active tab is highlighted with inverted colors.
        """
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(1)

        # Calculate width for each tab (divide screen evenly)
        tab_w = SCREEN_W // len(TAB_NAMES)

        for i, name in enumerate(TAB_NAMES):
            x = i * tab_w

            if i == self._current_tab:
                # Active tab - white background, black text
                Lcd.fillRect(x, TAB_Y, tab_w, TAB_H, WHITE)
                Lcd.setTextColor(BLACK, WHITE)
            else:
                # Inactive tab - dark background, gray text
                Lcd.fillRect(x, TAB_Y, tab_w, TAB_H, DARK_GRAY)
                Lcd.setTextColor(GRAY, DARK_GRAY)

            # Center the tab name text
            # ASCII7 font is 6 pixels wide per character at size 1
            text_x = x + (tab_w - len(name) * 6) // 2
            text_y = TAB_Y + 4  # Vertical padding
            Lcd.setCursor(text_x, text_y)
            Lcd.print(name)

        # Draw separator line below tabs
        Lcd.drawLine(0, TAB_H, SCREEN_W, TAB_H, GRAY)

    def _draw_content(self):
        """
        Draw the content area for the current tab.

        Dispatches to tab-specific drawing methods.
        """
        if self._current_tab == TAB_WIFI:
            self._draw_wifi_tab()
        elif self._current_tab == TAB_DISPLAY:
            self._draw_display_tab()
        elif self._current_tab == TAB_SOUND:
            self._draw_sound_tab()
        elif self._current_tab == TAB_SYSTEM:
            self._draw_system_tab()
        elif self._current_tab == TAB_ABOUT:
            self._draw_about_tab()
        else:
            self._draw_placeholder()

    def _draw_placeholder(self):
        """Draw placeholder content for unimplemented tabs."""
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(2)
        Lcd.setTextColor(WHITE, BLACK)

        # Show tab name centered in content area
        tab_name = TAB_NAMES[self._current_tab]
        # Size 2 font = 12 pixels per character
        text_w = len(tab_name) * 12
        x = (SCREEN_W - text_w) // 2
        y = CONTENT_Y + (CONTENT_H - 16) // 2  # Center vertically

        Lcd.setCursor(x, y)
        Lcd.print(tab_name)

        # Show placeholder message
        Lcd.setTextSize(1)
        Lcd.setTextColor(GRAY, BLACK)
        msg = "(not implemented)"
        msg_w = len(msg) * 6
        Lcd.setCursor((SCREEN_W - msg_w) // 2, y + 20)
        Lcd.print(msg)

    def _draw_display_tab(self):
        """
        Draw the Display tab content.

        Shows brightness slider with current value and controls.
        """
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(1)

        # Title
        Lcd.setTextColor(CYAN, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 5)
        Lcd.print("Brightness")

        # Current value as percentage
        pct = (self._brightness * 100) // 255
        value_str = f"{pct}%"
        Lcd.setTextColor(WHITE, BLACK)
        Lcd.setCursor(SCREEN_W - 10 - len(value_str) * 6, CONTENT_Y + 5)
        Lcd.print(value_str)

        # Slider bar background
        bar_x = 10
        bar_y = CONTENT_Y + 22
        bar_w = SCREEN_W - 20
        bar_h = 14
        Lcd.fillRect(bar_x, bar_y, bar_w, bar_h, DARK_GRAY)

        # Slider bar fill (proportional to brightness)
        fill_w = (self._brightness * (bar_w - 2)) // 255
        if fill_w > 0:
            Lcd.fillRect(bar_x + 1, bar_y + 1, fill_w, bar_h - 2, GREEN)

        # Slider border
        Lcd.drawRect(bar_x, bar_y, bar_w, bar_h, WHITE)

        # Presets row
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 45)
        Lcd.print("Presets:")
        Lcd.setTextColor(WHITE, BLACK)
        Lcd.setCursor(70, CONTENT_Y + 45)
        Lcd.print("[1]25% [2]50% [3]75% [4]100%")

        # Controls row
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 60)
        Lcd.print("[,/] Adjust  [S] Save  [0] Off")

        # Save indicator
        if self._brightness != self._brightness_saved:
            Lcd.setTextColor(YELLOW, BLACK)
            Lcd.setCursor(10, CONTENT_Y + 78)
            Lcd.print("* Unsaved changes")
        else:
            Lcd.setTextColor(GREEN, BLACK)
            Lcd.setCursor(10, CONTENT_Y + 78)
            Lcd.print("  Saved")

    def _draw_footer(self):
        """
        Draw footer with navigation hints.

        Shows available keyboard controls so user knows how to navigate.
        """
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(1)
        Lcd.setTextColor(GRAY, BLACK)

        Lcd.setCursor(5, FOOTER_Y)
        Lcd.print("Tab=Next  Enter=Select  ESC=Exit")

    def _switch_tab(self, direction):
        """
        Switch to next or previous tab.

        Args:
            direction: 1 for next tab, -1 for previous tab

        Wraps around at the ends (last tab -> first tab).
        """
        old_tab = self._current_tab
        self._current_tab = (self._current_tab + direction) % len(TAB_NAMES)
        print(f"[settings] Tab switch: {TAB_NAMES[old_tab]} -> {TAB_NAMES[self._current_tab]}")

        # Redraw the entire view to show new tab
        self.on_view()

    # -------------------------------------------------------------------------
    # WiFi Tab Methods
    # -------------------------------------------------------------------------

    def _get_wlan(self):
        """Get or create WLAN instance."""
        if self._wlan is None:
            try:
                import network
                self._wlan = network.WLAN(network.STA_IF)
            except Exception as e:
                print(f"[settings] WLAN init failed: {e}")
        return self._wlan

    def _rssi_to_bars(self, rssi):
        """Convert RSSI to signal bar count (1-4)."""
        if rssi > -50:
            return 4
        elif rssi > -60:
            return 3
        elif rssi > -70:
            return 2
        else:
            return 1

    def _draw_signal_bars(self, x, y, bars):
        """Draw signal strength bars at position."""
        bar_w = 3
        gap = 1
        max_h = 10
        for i in range(4):
            h = (i + 1) * 2 + 2  # Heights: 4, 6, 8, 10
            bx = x + i * (bar_w + gap)
            by = y + (max_h - h)
            color = GREEN if i < bars else DARK_GRAY
            Lcd.fillRect(bx, by, bar_w, h, color)

    def _draw_wifi_tab(self):
        """
        Draw the WiFi tab content.

        Shows WiFi status, network list, and controls.
        """
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(1)

        wlan = self._get_wlan()
        if wlan:
            self._wifi_enabled = wlan.active()
            if wlan.isconnected():
                self._wifi_connected_ssid = wlan.config("essid")
            else:
                self._wifi_connected_ssid = None

        # Password input mode - special display
        if self._wifi_input_mode:
            self._draw_wifi_password_input()
            return

        # WiFi status line
        Lcd.setTextColor(CYAN, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 3)
        Lcd.print("WiFi:")
        if self._wifi_enabled:
            if self._wifi_connected_ssid:
                Lcd.setTextColor(GREEN, BLACK)
                Lcd.setCursor(50, CONTENT_Y + 3)
                Lcd.print(self._wifi_connected_ssid[:25])
            else:
                Lcd.setTextColor(YELLOW, BLACK)
                Lcd.setCursor(50, CONTENT_Y + 3)
                Lcd.print("Not connected")
        else:
            Lcd.setTextColor(GRAY, BLACK)
            Lcd.setCursor(50, CONTENT_Y + 3)
            Lcd.print("Off")

        # Network list area
        list_y = CONTENT_Y + 16
        list_h = 50
        max_visible = 3

        if self._wifi_scanning:
            Lcd.setTextColor(YELLOW, BLACK)
            Lcd.setCursor(80, list_y + 15)
            Lcd.print("Scanning...")
        elif not self._wifi_networks:
            Lcd.setTextColor(GRAY, BLACK)
            Lcd.setCursor(50, list_y + 15)
            Lcd.print("Press [S] to scan")
        else:
            # Draw visible networks
            start_idx = max(0, self._wifi_selected - max_visible + 1)
            for i in range(min(max_visible, len(self._wifi_networks) - start_idx)):
                idx = start_idx + i
                ssid, rssi, security = self._wifi_networks[idx]
                ny = list_y + i * 16

                # Selection highlight
                if idx == self._wifi_selected:
                    Lcd.fillRect(5, ny, SCREEN_W - 10, 14, DARK_GRAY)
                    Lcd.setTextColor(WHITE, DARK_GRAY)
                else:
                    Lcd.setTextColor(GRAY, BLACK)

                # Signal bars
                bars = self._rssi_to_bars(rssi)
                self._draw_signal_bars(10, ny + 2, bars)

                # SSID (truncate if needed)
                ssid_display = ssid[:16] if len(ssid) > 16 else ssid
                Lcd.setCursor(30, ny + 3)
                Lcd.print(ssid_display)

                # Security indicator
                sec_str = "Open" if security == 0 else "WPA"
                Lcd.setCursor(150, ny + 3)
                Lcd.print(sec_str)

                # Connected indicator
                if ssid == self._wifi_connected_ssid:
                    Lcd.setTextColor(GREEN, DARK_GRAY if idx == self._wifi_selected else BLACK)
                    Lcd.setCursor(185, ny + 3)
                    Lcd.print("*")

        # Controls
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(5, CONTENT_Y + 70)
        if self._wifi_enabled:
            Lcd.print("[S]can  [O]ff")
        else:
            Lcd.print("[O]n")

        # Show disconnect/forget options if connected
        if self._wifi_connected_ssid:
            Lcd.setCursor(5, CONTENT_Y + 82)
            Lcd.print("[D]isconnect  [F]orget saved")
        elif self._wifi_enabled:
            # Only show saved network options when WiFi is on
            saved_ssid, _ = self._load_wifi_credentials()
            if saved_ssid:
                Lcd.setTextColor(CYAN, BLACK)
                Lcd.setCursor(5, CONTENT_Y + 82)
                Lcd.print(f"Saved: {saved_ssid[:20]}")
                Lcd.setTextColor(GRAY, BLACK)
                Lcd.setCursor(5, CONTENT_Y + 94)
                Lcd.print("[C]onnect saved  [F]orget")

    def _draw_wifi_password_input(self):
        """Draw password input screen."""
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(1)

        if self._wifi_selected < len(self._wifi_networks):
            ssid = self._wifi_networks[self._wifi_selected][0]
        else:
            ssid = "Network"

        Lcd.setTextColor(CYAN, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 5)
        Lcd.print(f"Connect to: {ssid[:18]}")

        Lcd.setTextColor(WHITE, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 25)
        Lcd.print("Password:")

        # Password field with cursor
        Lcd.fillRect(10, CONTENT_Y + 40, SCREEN_W - 20, 16, DARK_GRAY)
        Lcd.drawRect(10, CONTENT_Y + 40, SCREEN_W - 20, 16, WHITE)
        Lcd.setCursor(14, CONTENT_Y + 44)
        # Show masked password
        display_pw = "*" * len(self._wifi_password) + "_"
        Lcd.print(display_pw[:30])

        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 65)
        Lcd.print("[Enter] Connect  [ESC] Cancel")
        Lcd.setCursor(10, CONTENT_Y + 78)
        Lcd.print("[Bksp] Delete")

    def _wifi_toggle(self):
        """Toggle WiFi on/off."""
        wlan = self._get_wlan()
        if wlan:
            self._wifi_enabled = not self._wifi_enabled
            wlan.active(self._wifi_enabled)
            if not self._wifi_enabled:
                self._wifi_networks = []
                self._wifi_connected_ssid = None
            print(f"[settings] WiFi {'enabled' if self._wifi_enabled else 'disabled'}")
        self._redraw_wifi()

    def _wifi_scan(self):
        """Scan for WiFi networks."""
        wlan = self._get_wlan()
        if not wlan:
            return

        # Ensure WiFi is active before scanning
        if not wlan.active():
            print("[settings] Activating WiFi for scan...")
            wlan.active(True)
            self._wifi_enabled = True
            # Give it a moment to activate
            import time
            time.sleep_ms(500)

        self._wifi_scanning = True
        self._redraw_wifi()

        try:
            networks = wlan.scan()
            self._wifi_networks = []
            for net in networks:
                ssid = net[0].decode("utf-8") if isinstance(net[0], bytes) else net[0]
                rssi = net[3]
                security = net[4]
                if ssid:  # Skip hidden networks
                    self._wifi_networks.append((ssid, rssi, security))
            # Sort by signal strength
            self._wifi_networks.sort(key=lambda x: x[1], reverse=True)
            self._wifi_selected = 0
            print(f"[settings] Found {len(self._wifi_networks)} networks")
        except Exception as e:
            print(f"[settings] Scan failed: {e}")
        finally:
            self._wifi_scanning = False
            self._redraw_wifi()

    def _wifi_connect(self):
        """Connect to selected network."""
        if not self._wifi_networks or self._wifi_selected >= len(self._wifi_networks):
            return

        ssid, rssi, security = self._wifi_networks[self._wifi_selected]

        if security == 0:
            # Open network - connect directly
            self._do_wifi_connect(ssid, "")
        else:
            # Secured network - enter password mode
            self._wifi_password = ""
            self._wifi_input_mode = True
            self._redraw_wifi()

    def _do_wifi_connect(self, ssid, password):
        """Actually connect to network."""
        wlan = self._get_wlan()
        if not wlan:
            return

        print(f"[settings] Connecting to {ssid}...")
        Lcd.fillRect(0, CONTENT_Y, SCREEN_W, CONTENT_H, BLACK)
        Lcd.setTextColor(YELLOW, BLACK)
        Lcd.setCursor(60, CONTENT_Y + 40)
        Lcd.print("Connecting...")

        import time
        connected = False

        try:
            # Disconnect first if already connected
            if wlan.isconnected():
                wlan.disconnect()
                time.sleep_ms(300)

            wlan.connect(ssid, password)

            # Wait for connection (with timeout) - 10 seconds
            for i in range(100):
                if wlan.isconnected():
                    # Got initial connection, wait a bit to confirm it's stable
                    time.sleep_ms(1000)
                    if wlan.isconnected():
                        connected = True
                        break
                    # Connection dropped, keep waiting
                time.sleep_ms(100)

            if connected:
                self._wifi_connected_ssid = ssid
                print(f"[settings] Connected to {ssid}")
                self._save_wifi_credentials(ssid, password)
            else:
                self._wifi_connected_ssid = None
                # Make sure we're disconnected
                try:
                    wlan.disconnect()
                except:
                    pass
                print("[settings] Connection failed")
                # Show error briefly
                Lcd.fillRect(0, CONTENT_Y, SCREEN_W, CONTENT_H, BLACK)
                Lcd.setTextColor(0xFF0000, BLACK)  # Red
                Lcd.setCursor(50, CONTENT_Y + 40)
                Lcd.print("Connection failed!")
                time.sleep_ms(1500)

        except Exception as e:
            print(f"[settings] Connect failed: {e}")
            self._wifi_connected_ssid = None

        self._wifi_input_mode = False
        self._redraw_wifi()

    def _save_wifi_credentials(self, ssid, password):
        """Save WiFi credentials to NVS for auto-reconnect."""
        try:
            import esp32
            nvs = esp32.NVS("wifi")
            # Store SSID and password as blobs (strings)
            nvs.set_blob("ssid", ssid.encode("utf-8"))
            nvs.set_blob("password", password.encode("utf-8"))
            nvs.commit()
            print(f"[settings] WiFi credentials saved for {ssid}")
        except Exception as e:
            print(f"[settings] Failed to save WiFi credentials: {e}")

    def _load_wifi_credentials(self):
        """Load saved WiFi credentials from NVS."""
        try:
            import esp32
            nvs = esp32.NVS("wifi")
            # Read SSID
            ssid_buf = bytearray(64)
            ssid_len = nvs.get_blob("ssid", ssid_buf)
            ssid = ssid_buf[:ssid_len].decode("utf-8") if ssid_len else None
            # Read password
            pwd_buf = bytearray(64)
            pwd_len = nvs.get_blob("password", pwd_buf)
            password = pwd_buf[:pwd_len].decode("utf-8") if pwd_len else ""
            if ssid:
                print(f"[settings] Loaded saved WiFi: {ssid}")
                return ssid, password
        except Exception as e:
            print(f"[settings] No saved WiFi credentials: {e}")
        return None, None

    def _forget_wifi(self):
        """Clear saved WiFi credentials from NVS."""
        try:
            import esp32
            nvs = esp32.NVS("wifi")
            nvs.erase_key("ssid")
            nvs.erase_key("password")
            nvs.commit()
            print("[settings] WiFi credentials forgotten")
        except Exception as e:
            print(f"[settings] Failed to forget WiFi: {e}")

    def _wifi_disconnect(self):
        """Disconnect from current network."""
        wlan = self._get_wlan()
        if wlan and wlan.isconnected():
            wlan.disconnect()
            self._wifi_connected_ssid = None
            print("[settings] Disconnected")
        self._redraw_wifi()

    def _redraw_wifi(self):
        """Redraw WiFi tab content."""
        Lcd.fillRect(0, CONTENT_Y, SCREEN_W, CONTENT_H, BLACK)
        self._draw_wifi_tab()

    def _handle_wifi_keys(self, key):
        """
        Handle keyboard input for WiFi tab.

        Args:
            key: The key code pressed

        Returns:
            True if key was handled, False otherwise
        """
        # Password input mode
        if self._wifi_input_mode:
            # ESC - cancel
            if key == KeyCode.KEYCODE_ESC:
                self._wifi_input_mode = False
                self._wifi_password = ""
                self._redraw_wifi()
                return True

            # Backspace - delete last char
            if key == KeyCode.KEYCODE_BACKSPACE:
                if self._wifi_password:
                    self._wifi_password = self._wifi_password[:-1]
                    self._redraw_wifi()
                return True

            # Enter - connect
            if key == KeyCode.KEYCODE_ENTER:
                ssid = self._wifi_networks[self._wifi_selected][0]
                self._do_wifi_connect(ssid, self._wifi_password)
                return True

            # Printable character - add to password
            if 32 <= key <= 126:
                self._wifi_password += chr(key)
                self._redraw_wifi()
                return True

            return True  # Consume all keys in input mode

        # Normal mode
        # O - toggle WiFi on/off
        if key == ord("o") or key == ord("O"):
            self._wifi_toggle()
            return True

        # S - scan (will auto-enable WiFi if needed)
        if key == ord("s") or key == ord("S"):
            self._wifi_scan()
            return True

        # ; - navigate up
        if key == KEY_NAV_UP:
            if self._wifi_networks and self._wifi_selected > 0:
                self._wifi_selected -= 1
                self._redraw_wifi()
            return True

        # . - navigate down
        if key == KEY_NAV_DOWN:
            if self._wifi_networks and self._wifi_selected < len(self._wifi_networks) - 1:
                self._wifi_selected += 1
                self._redraw_wifi()
            return True

        # Enter - connect to selected
        if key == KeyCode.KEYCODE_ENTER:
            if self._wifi_networks:
                self._wifi_connect()
            return True

        # D - disconnect
        if key == ord("d") or key == ord("D"):
            self._wifi_disconnect()
            return True

        # F - forget saved network
        if key == ord("f") or key == ord("F"):
            self._forget_wifi()
            self._redraw_wifi()
            return True

        # C - connect to saved network (auto-enables WiFi)
        if key == ord("c") or key == ord("C"):
            saved_ssid, saved_pwd = self._load_wifi_credentials()
            if saved_ssid:
                # Ensure WiFi is active before connecting
                wlan = self._get_wlan()
                if wlan and not wlan.active():
                    print("[settings] Activating WiFi for saved connection...")
                    wlan.active(True)
                    self._wifi_enabled = True
                    import time
                    time.sleep_ms(500)
                self._do_wifi_connect(saved_ssid, saved_pwd)
            return True

        return False

    # -------------------------------------------------------------------------
    # Display Tab Methods
    # -------------------------------------------------------------------------

    def _set_brightness(self, value):
        """
        Set brightness to a specific value.

        Args:
            value: Brightness level (0-255), will be clamped
        """
        self._brightness = max(0, min(255, value))
        Lcd.setBrightness(self._brightness)
        print(f"[settings] Brightness set to {self._brightness}")

    def _adjust_brightness(self, delta):
        """
        Adjust brightness by a delta amount.

        Args:
            delta: Amount to change (+/- value)
        """
        self._set_brightness(self._brightness + delta)
        # Redraw just the content area
        Lcd.fillRect(0, CONTENT_Y, SCREEN_W, CONTENT_H, BLACK)
        self._draw_display_tab()

    def _save_brightness(self):
        """Save brightness to NVS for persistence."""
        try:
            import esp32
            nvs = esp32.NVS("settings")
            nvs.set_i32("brightness", self._brightness)
            nvs.commit()
            self._brightness_saved = self._brightness
            print(f"[settings] Brightness saved: {self._brightness}")
        except Exception as e:
            print(f"[settings] NVS save failed: {e}")
        # Redraw to update saved indicator
        Lcd.fillRect(0, CONTENT_Y, SCREEN_W, CONTENT_H, BLACK)
        self._draw_display_tab()

    def _screen_off(self):
        """Turn off screen, any key restores."""
        print("[settings] Screen off")
        Lcd.setBrightness(0)

    def _handle_display_keys(self, key):
        """
        Handle keyboard input for Display tab.

        Args:
            key: The key code pressed

        Returns:
            True if key was handled, False otherwise
        """
        # , (comma) - decrease brightness
        if key == KEY_NAV_LEFT:
            self._adjust_brightness(-15)
            return True

        # / (slash) - increase brightness
        if key == KEY_NAV_RIGHT:
            self._adjust_brightness(15)
            return True

        # Number keys 1-4 for presets
        if key == ord("1"):
            self._set_brightness(64)  # 25%
            Lcd.fillRect(0, CONTENT_Y, SCREEN_W, CONTENT_H, BLACK)
            self._draw_display_tab()
            return True
        if key == ord("2"):
            self._set_brightness(128)  # 50%
            Lcd.fillRect(0, CONTENT_Y, SCREEN_W, CONTENT_H, BLACK)
            self._draw_display_tab()
            return True
        if key == ord("3"):
            self._set_brightness(191)  # 75%
            Lcd.fillRect(0, CONTENT_Y, SCREEN_W, CONTENT_H, BLACK)
            self._draw_display_tab()
            return True
        if key == ord("4"):
            self._set_brightness(255)  # 100%
            Lcd.fillRect(0, CONTENT_Y, SCREEN_W, CONTENT_H, BLACK)
            self._draw_display_tab()
            return True

        # 0 - screen off
        if key == ord("0"):
            self._screen_off()
            return True

        # S - save to NVS
        if key == ord("s") or key == ord("S"):
            self._save_brightness()
            return True

        return False

    # -------------------------------------------------------------------------
    # Sound Tab Methods
    # -------------------------------------------------------------------------

    def _draw_sound_tab(self):
        """
        Draw the Sound tab content.

        Shows volume slider with mute toggle and controls.
        """
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(1)

        # Title and mute indicator
        Lcd.setTextColor(CYAN, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 5)
        Lcd.print("Volume")

        # Mute indicator
        if self._muted:
            Lcd.setTextColor(YELLOW, BLACK)
            Lcd.setCursor(70, CONTENT_Y + 5)
            Lcd.print("[MUTED]")
        else:
            Lcd.setTextColor(GREEN, BLACK)
            Lcd.setCursor(70, CONTENT_Y + 5)
            Lcd.print("[ON]")

        # Current value as percentage
        pct = (self._volume * 100) // 255
        value_str = f"{pct}%"
        Lcd.setTextColor(WHITE, BLACK)
        Lcd.setCursor(SCREEN_W - 10 - len(value_str) * 6, CONTENT_Y + 5)
        Lcd.print(value_str)

        # Slider bar background
        bar_x = 10
        bar_y = CONTENT_Y + 22
        bar_w = SCREEN_W - 20
        bar_h = 14
        Lcd.fillRect(bar_x, bar_y, bar_w, bar_h, DARK_GRAY)

        # Slider bar fill (proportional to volume, grayed if muted)
        fill_w = (self._volume * (bar_w - 2)) // 255
        fill_color = GRAY if self._muted else GREEN
        if fill_w > 0:
            Lcd.fillRect(bar_x + 1, bar_y + 1, fill_w, bar_h - 2, fill_color)

        # Slider border
        Lcd.drawRect(bar_x, bar_y, bar_w, bar_h, WHITE)

        # Controls row 1
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 45)
        Lcd.print("[,/] Adjust  [M] Mute  [T] Test")

        # Controls row 2
        Lcd.setCursor(10, CONTENT_Y + 60)
        Lcd.print("[S] Save")

        # Save indicator
        if self._volume != self._volume_saved:
            Lcd.setTextColor(YELLOW, BLACK)
            Lcd.setCursor(10, CONTENT_Y + 78)
            Lcd.print("* Unsaved changes")
        else:
            Lcd.setTextColor(GREEN, BLACK)
            Lcd.setCursor(10, CONTENT_Y + 78)
            Lcd.print("  Saved")

    def _get_speaker(self):
        """Get or create speaker instance."""
        if self._speaker is None:
            try:
                from M5 import Speaker
                self._speaker = Speaker
            except ImportError:
                print("[settings] Speaker not available")
        return self._speaker

    def _set_volume(self, value):
        """
        Set volume to a specific value.

        Args:
            value: Volume level (0-255), will be clamped
        """
        self._volume = max(0, min(255, value))
        speaker = self._get_speaker()
        if speaker:
            # Speaker volume is 0-255
            speaker.setVolume(0 if self._muted else self._volume)
        print(f"[settings] Volume set to {self._volume}")

    def _adjust_volume(self, delta):
        """
        Adjust volume by a delta amount.

        Args:
            delta: Amount to change (+/- value)
        """
        self._set_volume(self._volume + delta)
        # Play feedback tone
        if not self._muted:
            self._play_tone(880, 50)  # Short beep
        # Redraw just the content area
        Lcd.fillRect(0, CONTENT_Y, SCREEN_W, CONTENT_H, BLACK)
        self._draw_sound_tab()

    def _toggle_mute(self):
        """Toggle mute state."""
        self._muted = not self._muted
        speaker = self._get_speaker()
        if speaker:
            speaker.setVolume(0 if self._muted else self._volume)
        print(f"[settings] Muted: {self._muted}")
        Lcd.fillRect(0, CONTENT_Y, SCREEN_W, CONTENT_H, BLACK)
        self._draw_sound_tab()

    def _play_tone(self, freq, duration_ms):
        """Play a test tone."""
        speaker = self._get_speaker()
        if speaker and not self._muted:
            try:
                speaker.tone(freq, duration_ms)
            except Exception as e:
                print(f"[settings] Tone failed: {e}")

    def _play_test_tone(self):
        """Play 440Hz test tone."""
        print("[settings] Playing test tone")
        self._play_tone(440, 500)

    def _save_volume(self):
        """Save volume to NVS for persistence."""
        try:
            import esp32
            nvs = esp32.NVS("settings")
            nvs.set_i32("volume", self._volume)
            nvs.commit()
            self._volume_saved = self._volume
            print(f"[settings] Volume saved: {self._volume}")
        except Exception as e:
            print(f"[settings] NVS save failed: {e}")
        # Redraw to update saved indicator
        Lcd.fillRect(0, CONTENT_Y, SCREEN_W, CONTENT_H, BLACK)
        self._draw_sound_tab()

    def _handle_sound_keys(self, key):
        """
        Handle keyboard input for Sound tab.

        Args:
            key: The key code pressed

        Returns:
            True if key was handled, False otherwise
        """
        # , (comma) - decrease volume
        if key == KEY_NAV_LEFT:
            self._adjust_volume(-15)
            return True

        # / (slash) - increase volume
        if key == KEY_NAV_RIGHT:
            self._adjust_volume(15)
            return True

        # M - toggle mute
        if key == ord("m") or key == ord("M"):
            self._toggle_mute()
            return True

        # T - test tone
        if key == ord("t") or key == ord("T"):
            self._play_test_tone()
            return True

        # S - save to NVS
        if key == ord("s") or key == ord("S"):
            self._save_volume()
            return True

        return False

    # -------------------------------------------------------------------------
    # System Tab Methods
    # -------------------------------------------------------------------------

    def _draw_system_tab(self):
        """
        Draw the System tab content.

        Shows boot option, memory info, storage info, and reboot option.
        """
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(1)

        # Boot mode option
        Lcd.setTextColor(CYAN, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 5)
        Lcd.print("Boot Mode:")
        Lcd.setTextColor(WHITE, BLACK)
        boot_label = self._boot_labels[self._boot_option]
        Lcd.setCursor(90, CONTENT_Y + 5)
        Lcd.print(f"[{boot_label}]")

        # Memory info
        try:
            import gc
            gc.collect()
            free_mem = gc.mem_free()
            alloc_mem = gc.mem_alloc()
            total_mem = free_mem + alloc_mem
            Lcd.setTextColor(GRAY, BLACK)
            Lcd.setCursor(10, CONTENT_Y + 25)
            Lcd.print("Memory:")
            Lcd.setTextColor(WHITE, BLACK)
            Lcd.setCursor(70, CONTENT_Y + 25)
            Lcd.print(f"{free_mem:,} / {total_mem:,} free")
        except Exception:
            Lcd.setTextColor(GRAY, BLACK)
            Lcd.setCursor(10, CONTENT_Y + 25)
            Lcd.print("Memory: (unavailable)")

        # Storage info
        try:
            import os
            stat = os.statvfs("/flash")
            block_size = stat[0]
            total_blocks = stat[2]
            free_blocks = stat[3]
            total_kb = (total_blocks * block_size) // 1024
            used_kb = ((total_blocks - free_blocks) * block_size) // 1024
            Lcd.setTextColor(GRAY, BLACK)
            Lcd.setCursor(10, CONTENT_Y + 40)
            Lcd.print("Storage:")
            Lcd.setTextColor(WHITE, BLACK)
            Lcd.setCursor(70, CONTENT_Y + 40)
            Lcd.print(f"{used_kb} KB / {total_kb} KB used")
        except Exception:
            Lcd.setTextColor(GRAY, BLACK)
            Lcd.setCursor(10, CONTENT_Y + 40)
            Lcd.print("Storage: (unavailable)")

        # Controls
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 60)
        Lcd.print("[Enter] Change boot  [S] Save  [R] Reboot")

        # Save indicator
        if self._boot_option != self._boot_option_saved:
            Lcd.setTextColor(YELLOW, BLACK)
            Lcd.setCursor(10, CONTENT_Y + 78)
            Lcd.print("* Unsaved changes")
        else:
            Lcd.setTextColor(GREEN, BLACK)
            Lcd.setCursor(10, CONTENT_Y + 78)
            Lcd.print("  Saved")

    def _cycle_boot_option(self):
        """Cycle through boot options."""
        self._boot_option = (self._boot_option + 1) % len(self._boot_labels)
        print(f"[settings] Boot option: {self._boot_labels[self._boot_option]}")
        Lcd.fillRect(0, CONTENT_Y, SCREEN_W, CONTENT_H, BLACK)
        self._draw_system_tab()

    def _save_boot_option(self):
        """Save boot option to NVS."""
        try:
            import esp32
            nvs = esp32.NVS("settings")
            nvs.set_i32("boot_option", self._boot_option)
            nvs.commit()
            self._boot_option_saved = self._boot_option
            print(f"[settings] Boot option saved: {self._boot_option}")
        except Exception as e:
            print(f"[settings] NVS save failed: {e}")
        Lcd.fillRect(0, CONTENT_Y, SCREEN_W, CONTENT_H, BLACK)
        self._draw_system_tab()

    def _reboot(self):
        """Reboot the device."""
        print("[settings] Rebooting...")
        Lcd.fillScreen(BLACK)
        Lcd.setTextColor(WHITE, BLACK)
        Lcd.setCursor(80, 60)
        Lcd.print("Rebooting...")
        try:
            import machine
            machine.reset()
        except Exception as e:
            print(f"[settings] Reboot failed: {e}")

    def _handle_system_keys(self, key):
        """
        Handle keyboard input for System tab.

        Args:
            key: The key code pressed

        Returns:
            True if key was handled, False otherwise
        """
        # Enter - cycle boot option
        if key == KeyCode.KEYCODE_ENTER:
            self._cycle_boot_option()
            return True

        # S - save boot option
        if key == ord("s") or key == ord("S"):
            self._save_boot_option()
            return True

        # R - reboot
        if key == ord("r") or key == ord("R"):
            self._reboot()
            return True

        return False

    # -------------------------------------------------------------------------
    # About Tab Methods
    # -------------------------------------------------------------------------

    def _draw_about_tab(self):
        """
        Draw the About tab content.

        Shows device information: model, chip, MicroPython version,
        MAC address, and uptime.
        """
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(1)

        y = CONTENT_Y + 5
        line_h = 14

        # Device model
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, y)
        Lcd.print("Device:")
        Lcd.setTextColor(WHITE, BLACK)
        Lcd.setCursor(80, y)
        Lcd.print("M5Stack Cardputer")

        # Chip info
        y += line_h
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, y)
        Lcd.print("Chip:")
        Lcd.setTextColor(WHITE, BLACK)
        Lcd.setCursor(80, y)
        Lcd.print("ESP32-S3 @ 240MHz")

        # MicroPython version
        y += line_h
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, y)
        Lcd.print("uPython:")
        Lcd.setTextColor(WHITE, BLACK)
        Lcd.setCursor(80, y)
        try:
            import sys
            ver = sys.version.split()[0] if hasattr(sys, "version") else "unknown"
            Lcd.print(ver[:20])  # Truncate if too long
        except Exception:
            Lcd.print("unknown")

        # MAC address
        y += line_h
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, y)
        Lcd.print("MAC:")
        Lcd.setTextColor(WHITE, BLACK)
        Lcd.setCursor(80, y)
        try:
            import network
            wlan = network.WLAN(network.STA_IF)
            mac = wlan.config("mac")
            mac_str = ":".join(f"{b:02X}" for b in mac)
            Lcd.print(mac_str)
        except Exception:
            Lcd.print("(unavailable)")

        # Uptime
        y += line_h
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, y)
        Lcd.print("Uptime:")
        Lcd.setTextColor(WHITE, BLACK)
        Lcd.setCursor(80, y)
        try:
            import time
            ticks = time.ticks_ms()
            secs = ticks // 1000
            mins = secs // 60
            hours = mins // 60
            secs = secs % 60
            mins = mins % 60
            Lcd.print(f"{hours}h {mins}m {secs}s")
        except Exception:
            Lcd.print("(unavailable)")

        # Battery level
        y += line_h
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, y)
        Lcd.print("Battery:")
        Lcd.setCursor(80, y)
        try:
            from M5 import Power
            level = Power.getBatteryLevel()
            charging = Power.isCharging()
            # Color based on level
            if level > 50:
                Lcd.setTextColor(GREEN, BLACK)
            elif level > 20:
                Lcd.setTextColor(YELLOW, BLACK)
            else:
                Lcd.setTextColor(0xFF0000, BLACK)  # Red
            status = " (charging)" if charging else ""
            Lcd.print(f"{level}%{status}")
        except Exception:
            Lcd.setTextColor(WHITE, BLACK)
            Lcd.print("(unavailable)")

    async def _kb_event_handler(self, event, fw):
        """
        Handle keyboard events.

        This is called by the framework for every key press.
        We handle tab navigation here; tab-specific keys are
        dispatched to their respective handlers.
        """
        key = event.key
        print(f"[settings] Key pressed: {key} (0x{key:02X})")

        # ESC - let framework handle exit (don't set event.status)
        if key == KeyCode.KEYCODE_ESC:
            print("[settings] ESC pressed, exiting to launcher")
            return

        # Any key restores screen if brightness is 0 (screen off mode)
        if self._brightness == 0 and self._current_tab == TAB_DISPLAY:
            self._set_brightness(self._brightness_saved or 128)
            self.on_view()
            event.status = True
            return

        # Tab key (HID scancode 0x2B) - next tab
        if key == HID_TAB:
            print("[settings] Tab key - switching to next tab")
            self._switch_tab(1)
            event.status = True
            return

        # ; (semicolon) - previous tab (when not in tab with list navigation)
        if key == KEY_NAV_UP and self._current_tab not in [TAB_WIFI]:
            print("[settings] ; key - switching to previous tab")
            self._switch_tab(-1)
            event.status = True
            return

        # . (period) - next tab (when not in tab with list navigation)
        if key == KEY_NAV_DOWN and self._current_tab not in [TAB_WIFI]:
            print("[settings] . key - switching to next tab")
            self._switch_tab(1)
            event.status = True
            return

        # Dispatch to tab-specific handlers
        if self._current_tab == TAB_WIFI:
            if self._handle_wifi_keys(key):
                event.status = True
                return
        elif self._current_tab == TAB_DISPLAY:
            if self._handle_display_keys(key):
                event.status = True
                return
        elif self._current_tab == TAB_SOUND:
            if self._handle_sound_keys(key):
                event.status = True
                return
        elif self._current_tab == TAB_SYSTEM:
            if self._handle_system_keys(key):
                event.status = True
                return

        # Mark event as handled to prevent framework from processing it
        event.status = True

    async def on_run(self):
        """
        Background task loop.

        Currently does nothing - just keeps the app alive.
        Later tabs may use this for periodic updates (e.g., WiFi scan).
        """
        while True:
            await asyncio.sleep_ms(100)


# =============================================================================
# App Export
# =============================================================================
# Export for framework auto-discovery
App = SettingsApp

# Allow running directly for testing: python apps/settings_app.py
if __name__ == "__main__":
    import M5

    M5.begin()
    Lcd.setRotation(1)  # Landscape mode
    Lcd.setBrightness(80)

    from lib.framework import Framework

    fw = Framework()
    fw.install(SettingsApp())
    fw.start()
