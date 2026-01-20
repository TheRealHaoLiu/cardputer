"""
WiFi Tab - Network configuration with independent STA and AP control.

Sub-tab UI:
- [S]TA - Station mode (connect to existing networks)
- [A]P - Access Point mode (create a hotspot)

Each interface can be toggled on/off independently with [O].
"""

from M5 import Lcd, Widgets

from . import (
    BLACK,
    CONTENT_H,
    CONTENT_Y,
    CYAN,
    DARK_GRAY,
    GRAY,
    GREEN,
    RED,
    SCREEN_W,
    WHITE,
    YELLOW,
    TabBase,
)

# Sub-tab indices
SUBTAB_STA = 0
SUBTAB_AP = 1

# View states
VIEW_MAIN = 0  # Main sub-tab view
VIEW_STA_PASSWORD = 1  # STA password input
VIEW_AP_EDITOR = 2  # AP config editor


class WiFiTab(TabBase):
    """WiFi configuration tab with independent STA/AP control."""

    def __init__(self):
        self._wifi = None
        self._subtab = SUBTAB_STA
        self._view = VIEW_MAIN
        # STA state
        self._networks = []
        self._selected = 0
        self._scanning = False
        self._password = ""
        # AP editor state
        self._ap_field = 0  # 0=SSID, 1=Password
        self._ap_ssid_edit = ""
        self._ap_password_edit = ""

    def _get_wifi(self):
        """Get WiFiManager instance (always fresh for hot-reload support)."""
        try:
            from wifi_manager import get_wifi_manager

            wifi = get_wifi_manager()
            # Load config on first access (check if already loaded)
            if self._wifi is None:
                wifi.load_config()
                self._wifi = wifi
            return wifi
        except Exception as e:
            print(f"[wifi_tab] WiFiManager init failed: {e}")
            return None

    # -------------------------------------------------------------------------
    # Drawing
    # -------------------------------------------------------------------------

    def _redraw(self, app):
        """Clear content area and redraw."""
        Lcd.fillRect(0, CONTENT_Y, SCREEN_W, CONTENT_H, BLACK)
        self.draw(app)

    def draw(self, app):
        """Draw WiFi tab content based on current sub-tab and view."""
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(1)

        wifi = self._get_wifi()
        if not wifi:
            Lcd.setTextColor(RED, BLACK)
            Lcd.setCursor(10, CONTENT_Y + 30)
            Lcd.print("WiFi unavailable")
            return

        if self._view == VIEW_STA_PASSWORD:
            self._draw_sta_password()
        elif self._view == VIEW_AP_EDITOR:
            self._draw_ap_editor()
        else:
            self._draw_subtab_bar()
            if self._subtab == SUBTAB_STA:
                self._draw_sta_view(wifi)
            else:
                self._draw_ap_view(wifi)

    def _draw_subtab_bar(self):
        """Draw sub-tab navigation bar."""
        y = CONTENT_Y + 2

        # [S]TA label
        if self._subtab == SUBTAB_STA:
            # Highlighted: inverted colors
            Lcd.fillRect(5, y - 1, 32, 12, WHITE)
            Lcd.setTextColor(BLACK, WHITE)
        else:
            Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(7, y)
        Lcd.print("[S]TA")

        # [A]P label
        if self._subtab == SUBTAB_AP:
            # Highlighted: inverted colors
            Lcd.fillRect(45, y - 1, 26, 12, WHITE)
            Lcd.setTextColor(BLACK, WHITE)
        else:
            Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(47, y)
        Lcd.print("[A]P")

    # -------------------------------------------------------------------------
    # STA Views
    # -------------------------------------------------------------------------

    def _draw_sta_view(self, wifi):
        """Draw STA sub-tab content based on state."""
        sta_on = wifi.sta_is_enabled()

        if not sta_on:
            self._draw_sta_off_view()
        elif wifi.sta_is_connected():
            self._draw_sta_connected_view(wifi)
        else:
            self._draw_sta_disconnected_view(wifi)

    def _draw_sta_off_view(self):
        """Draw STA disabled view."""
        y = CONTENT_Y + 18

        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(5, y)
        Lcd.print("Status: Off")

        Lcd.setCursor(50, y + 25)
        Lcd.print("WiFi radio disabled")
        Lcd.setCursor(45, y + 40)
        Lcd.print("Press [O] to enable")

        # Controls
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(5, CONTENT_Y + 80)
        Lcd.print("[O]n")

    def _draw_sta_disconnected_view(self, wifi):
        """Draw STA on but not connected view."""
        y = CONTENT_Y + 18

        Lcd.setTextColor(YELLOW, BLACK)
        Lcd.setCursor(5, y)
        Lcd.print("Status: Not connected")

        # Network list
        self._draw_network_list(y + 14)

        # Controls
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(5, CONTENT_Y + 80)
        Lcd.print("[O]ff [S]can [C]onnect saved")

    def _draw_sta_connected_view(self, wifi):
        """Draw STA connected view."""
        y = CONTENT_Y + 18

        ip = wifi.sta_get_ip() or ""
        Lcd.setTextColor(GREEN, BLACK)
        Lcd.setCursor(5, y)
        Lcd.print("Status: Connected")
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(110, y)
        Lcd.print(f"IP: {ip}")

        # Network list
        self._draw_network_list(y + 14)

        # Controls
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(5, CONTENT_Y + 80)
        Lcd.print("[O]ff [S]can [D]isconnect")

    def _draw_network_list(self, start_y):
        """Draw the scanned network list."""
        wifi = self._get_wifi()
        max_visible = 3

        if self._scanning:
            Lcd.setTextColor(YELLOW, BLACK)
            Lcd.setCursor(80, start_y + 15)
            Lcd.print("Scanning...")
            return

        if not self._networks:
            Lcd.setTextColor(GRAY, BLACK)
            Lcd.setCursor(50, start_y + 15)
            Lcd.print("Press [S] to scan")
            return

        start_idx = max(0, self._selected - max_visible + 1)
        for i in range(min(max_visible, len(self._networks) - start_idx)):
            idx = start_idx + i
            ssid, rssi, security = self._networks[idx]
            ny = start_y + i * 16

            if idx == self._selected:
                Lcd.fillRect(5, ny, SCREEN_W - 10, 14, DARK_GRAY)
                Lcd.setTextColor(WHITE, DARK_GRAY)
            else:
                Lcd.setTextColor(GRAY, BLACK)

            bars = self._rssi_to_bars(rssi)
            self._draw_signal_bars(10, ny + 2, bars)

            ssid_display = ssid[:16] if len(ssid) > 16 else ssid
            Lcd.setCursor(30, ny + 3)
            Lcd.print(ssid_display)

            sec_str = "Open" if security == 0 else "WPA"
            Lcd.setCursor(150, ny + 3)
            Lcd.print(sec_str)

            # Mark connected network
            connected_ssid = wifi.sta_get_ssid() if wifi.sta_is_connected() else None
            if ssid == connected_ssid:
                Lcd.setTextColor(GREEN, DARK_GRAY if idx == self._selected else BLACK)
                Lcd.setCursor(185, ny + 3)
                Lcd.print("*")

    def _draw_sta_password(self):
        """Draw STA password input screen."""
        ssid = (
            self._networks[self._selected][0] if self._selected < len(self._networks) else "Network"
        )

        Lcd.setTextColor(CYAN, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 5)
        Lcd.print(f"Connect to: {ssid[:18]}")

        Lcd.setTextColor(WHITE, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 25)
        Lcd.print("Password:")

        Lcd.fillRect(10, CONTENT_Y + 40, SCREEN_W - 20, 16, DARK_GRAY)
        Lcd.drawRect(10, CONTENT_Y + 40, SCREEN_W - 20, 16, WHITE)
        Lcd.setCursor(14, CONTENT_Y + 44)
        display_pw = "*" * len(self._password) + "_"
        Lcd.print(display_pw[:30])

        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 65)
        Lcd.print("[Enter] Connect  [ESC] Cancel")
        Lcd.setCursor(10, CONTENT_Y + 78)
        Lcd.print("[Bksp] Delete")

    # -------------------------------------------------------------------------
    # AP Views
    # -------------------------------------------------------------------------

    def _draw_ap_view(self, wifi):
        """Draw AP sub-tab content based on state."""
        ap_on = wifi.ap_is_enabled()

        if not ap_on:
            self._draw_ap_off_view(wifi)
        else:
            clients = wifi.ap_get_clients()
            if clients:
                self._draw_ap_with_clients_view(wifi, clients)
            else:
                self._draw_ap_no_clients_view(wifi)

    def _draw_ap_off_view(self, wifi):
        """Draw AP disabled view."""
        y = CONTENT_Y + 18

        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(5, y)
        Lcd.print("Status: Off")

        Lcd.setCursor(5, y + 14)
        Lcd.print(f"SSID: {wifi.ap_get_ssid()[:22]}")

        pw = wifi.ap_get_password()
        Lcd.setCursor(5, y + 26)
        if pw:
            Lcd.print(f"Pass: {'*' * min(len(pw), 20)}")
        else:
            Lcd.print("Pass: (open)")

        Lcd.setCursor(50, y + 45)
        Lcd.print("Press [O] to start")

        # Controls
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(5, CONTENT_Y + 80)
        Lcd.print("[O]n [E]dit")

    def _draw_ap_no_clients_view(self, wifi):
        """Draw AP on with no clients view."""
        y = CONTENT_Y + 18

        ssid = wifi.ap_get_ssid()
        ip = wifi.ap_get_ip()
        Lcd.setTextColor(GREEN, BLACK)
        Lcd.setCursor(5, y)
        Lcd.print(f"SSID: {ssid[:18]}")
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(150, y)
        Lcd.print(f"IP: {ip}")

        Lcd.setCursor(5, y + 14)
        Lcd.print("Clients: 0")

        Lcd.setCursor(40, y + 35)
        Lcd.print("Waiting for connections...")

        # Controls
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(5, CONTENT_Y + 80)
        Lcd.print("[O]ff [E]dit [R]efresh")

    def _draw_ap_with_clients_view(self, wifi, clients):
        """Draw AP on with connected clients view."""
        y = CONTENT_Y + 18

        ssid = wifi.ap_get_ssid()
        ip = wifi.ap_get_ip()
        Lcd.setTextColor(GREEN, BLACK)
        Lcd.setCursor(5, y)
        Lcd.print(f"SSID: {ssid[:18]}")
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(150, y)
        Lcd.print(f"IP: {ip}")

        Lcd.setTextColor(CYAN, BLACK)
        Lcd.setCursor(5, y + 14)
        Lcd.print(f"Clients: {len(clients)}")

        # Client list (clients is a list of MAC strings)
        for i, mac in enumerate(clients[:3]):
            Lcd.setTextColor(GRAY, BLACK)
            Lcd.setCursor(10, y + 26 + i * 10)
            Lcd.print(mac)

        # Controls
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(5, CONTENT_Y + 80)
        Lcd.print("[O]ff [E]dit [R]efresh")

    def _draw_ap_editor(self):
        """Draw AP configuration editor."""
        Lcd.setTextColor(CYAN, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 5)
        Lcd.print("AP Configuration")

        y = CONTENT_Y + 25

        # SSID field
        if self._ap_field == 0:
            Lcd.fillRect(5, y - 2, SCREEN_W - 10, 14, DARK_GRAY)
            Lcd.setTextColor(WHITE, DARK_GRAY)
        else:
            Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, y)
        Lcd.print(
            f"SSID: {self._ap_ssid_edit[:20]}_"
            if self._ap_field == 0
            else f"SSID: {self._ap_ssid_edit[:22]}"
        )

        y += 18

        # Password field
        if self._ap_field == 1:
            Lcd.fillRect(5, y - 2, SCREEN_W - 10, 14, DARK_GRAY)
            Lcd.setTextColor(WHITE, DARK_GRAY)
        else:
            Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, y)
        pw_display = "*" * len(self._ap_password_edit)
        if self._ap_field == 1:
            Lcd.print(f"Pass: {pw_display[:20]}_")
        else:
            Lcd.print(f"Pass: {pw_display[:22]}" if pw_display else "Pass: (open)")

        # Controls
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 65)
        Lcd.print("[Enter] Apply  [ESC] Cancel")
        Lcd.setCursor(10, CONTENT_Y + 78)
        Lcd.print("[Up/Down] Switch field")

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _rssi_to_bars(self, rssi):
        """Convert RSSI to signal bar count (1-4)."""
        if rssi > -50:
            return 4
        elif rssi > -60:
            return 3
        elif rssi > -70:
            return 2
        return 1

    def _draw_signal_bars(self, x, y, bars):
        """Draw signal strength bars at position."""
        bar_w = 3
        gap = 1
        max_h = 10
        for i in range(4):
            h = (i + 1) * 2 + 2
            bx = x + i * (bar_w + gap)
            by = y + (max_h - h)
            color = GREEN if i < bars else DARK_GRAY
            Lcd.fillRect(bx, by, bar_w, h, color)

    # -------------------------------------------------------------------------
    # STA Actions
    # -------------------------------------------------------------------------

    def _sta_toggle(self, app):
        """Toggle STA on/off."""
        wifi = self._get_wifi()
        if not wifi:
            return

        if wifi.sta_is_enabled():
            wifi.sta_disable()
        else:
            wifi.sta_enable()
        wifi.save_config()
        self._redraw(app)

    def _scan(self, app):
        """Scan for networks."""
        wifi = self._get_wifi()
        if not wifi:
            return

        self._scanning = True
        self._redraw(app)

        try:
            self._networks = wifi.sta_scan()
            self._selected = 0
            print(f"[wifi_tab] Found {len(self._networks)} networks")
        except Exception as e:
            print(f"[wifi_tab] Scan failed: {e}")
        finally:
            self._scanning = False
            self._redraw(app)

    def _connect_selected(self, app):
        """Connect to selected network."""
        if not self._networks or self._selected >= len(self._networks):
            return

        ssid, rssi, security = self._networks[self._selected]
        if security == 0:
            self._do_connect(app, ssid, "")
        else:
            self._password = ""
            self._view = VIEW_STA_PASSWORD
            self._redraw(app)

    def _do_connect(self, app, ssid, password):
        """Perform the actual connection."""
        wifi = self._get_wifi()
        if not wifi:
            return

        Lcd.fillRect(0, CONTENT_Y, SCREEN_W, CONTENT_H, BLACK)
        Lcd.setTextColor(YELLOW, BLACK)
        Lcd.setCursor(60, CONTENT_Y + 40)
        Lcd.print("Connecting...")

        success = wifi.sta_connect(ssid, password)

        if success:
            wifi.save_config()
        else:
            Lcd.fillRect(0, CONTENT_Y, SCREEN_W, CONTENT_H, BLACK)
            Lcd.setTextColor(RED, BLACK)
            Lcd.setCursor(50, CONTENT_Y + 40)
            Lcd.print("Connection failed!")
            import time

            time.sleep_ms(1500)

        self._view = VIEW_MAIN
        self._password = ""
        self._redraw(app)

    def _connect_saved(self, app):
        """Connect to saved network."""
        wifi = self._get_wifi()
        if not wifi:
            return

        ssid, password = wifi.get_sta_credentials()
        print(f"[wifi_tab] Connect saved: ssid={ssid}")
        if ssid:
            self._do_connect(app, ssid, password or "")
        else:
            # No saved network - show brief message
            Lcd.fillRect(0, CONTENT_Y, SCREEN_W, CONTENT_H, BLACK)
            Lcd.setTextColor(YELLOW, BLACK)
            Lcd.setCursor(50, CONTENT_Y + 40)
            Lcd.print("No saved network")
            import time

            time.sleep_ms(1000)
            self._redraw(app)

    def _disconnect(self, app):
        """Disconnect from current network."""
        wifi = self._get_wifi()
        if wifi:
            wifi.sta_disconnect()
            self._redraw(app)

    # -------------------------------------------------------------------------
    # AP Actions
    # -------------------------------------------------------------------------

    def _ap_toggle(self, app):
        """Toggle AP on/off."""
        wifi = self._get_wifi()
        if not wifi:
            return

        if wifi.ap_is_enabled():
            wifi.ap_disable()
        else:
            wifi.ap_enable()
        wifi.save_config()
        self._redraw(app)

    def _open_ap_editor(self, app):
        """Open AP configuration editor."""
        wifi = self._get_wifi()
        if wifi:
            self._ap_ssid_edit = wifi.ap_get_ssid()
            self._ap_password_edit = wifi.ap_get_password() or ""
        self._ap_field = 0
        self._view = VIEW_AP_EDITOR
        self._redraw(app)

    def _apply_ap_config(self, app):
        """Apply AP configuration changes."""
        wifi = self._get_wifi()
        if wifi:
            # Validate SSID
            if not self._ap_ssid_edit.strip():
                return  # Don't allow empty SSID

            # Reject password that's too short for WPA2 (1-7 chars)
            pw = self._ap_password_edit
            if pw and len(pw) < 8:
                Lcd.fillRect(0, CONTENT_Y, SCREEN_W, CONTENT_H, BLACK)
                Lcd.setTextColor(RED, BLACK)
                Lcd.setCursor(20, CONTENT_Y + 35)
                Lcd.print("Password must be")
                Lcd.setCursor(20, CONTENT_Y + 50)
                Lcd.print("8+ chars or empty")
                import time

                time.sleep_ms(1500)
                self._redraw(app)
                return  # Don't save, stay in editor

            wifi.ap_set_config(self._ap_ssid_edit, self._ap_password_edit)
            wifi.save_config()

        self._view = VIEW_MAIN
        self._redraw(app)

    # -------------------------------------------------------------------------
    # Key handling
    # -------------------------------------------------------------------------

    def handle_key(self, app, key):
        """Handle key press."""
        if self._view == VIEW_STA_PASSWORD:
            return self._handle_password_key(app, key)
        elif self._view == VIEW_AP_EDITOR:
            return self._handle_ap_editor_key(app, key)
        else:
            return self._handle_main_key(app, key)

    def _handle_main_key(self, app, key):
        """Handle keys in main view (sub-tab navigation)."""
        wifi = self._get_wifi()
        if not wifi:
            return False

        # Sub-tab switching: S for STA, A for AP
        if key == ord("s") or key == ord("S"):
            if self._subtab == SUBTAB_STA:
                # Already in STA, [S] means scan
                if wifi.sta_is_enabled():
                    self._scan(app)
                    return True
            else:
                # Switch to STA sub-tab
                self._subtab = SUBTAB_STA
                self._redraw(app)
                return True

        if key == ord("a") or key == ord("A"):
            if self._subtab != SUBTAB_AP:
                self._subtab = SUBTAB_AP
                self._redraw(app)
            return True

        # [O] - Toggle on/off for current interface
        if key == ord("o") or key == ord("O"):
            if self._subtab == SUBTAB_STA:
                self._sta_toggle(app)
            else:
                self._ap_toggle(app)
            return True

        # Context-specific keys
        if self._subtab == SUBTAB_STA:
            return self._handle_sta_keys(app, key, wifi)
        else:
            return self._handle_ap_keys(app, key)

    def _handle_sta_keys(self, app, key, wifi):
        """Handle keys in STA sub-tab."""
        from keycode import KEY_NAV_DOWN, KEY_NAV_UP, KeyCode

        if not wifi.sta_is_enabled():
            return False

        if key == KEY_NAV_UP:
            if self._networks and self._selected > 0:
                self._selected -= 1
                self._redraw(app)
            return True

        if key == KEY_NAV_DOWN:
            if self._networks and self._selected < len(self._networks) - 1:
                self._selected += 1
                self._redraw(app)
            return True

        if key == KeyCode.KEYCODE_ENTER:
            if self._networks:
                self._connect_selected(app)
            return True

        if key == ord("c") or key == ord("C"):
            self._connect_saved(app)
            return True

        if key == ord("d") or key == ord("D"):
            self._disconnect(app)
            return True

        return False

    def _handle_ap_keys(self, app, key):
        """Handle keys in AP sub-tab."""
        if key == ord("e") or key == ord("E"):
            self._open_ap_editor(app)
            return True
        if key == ord("r") or key == ord("R"):
            # Refresh AP view (updates client list)
            self._redraw(app)
            return True
        return False

    def _handle_password_key(self, app, key):
        """Handle keys in password input view."""
        from keycode import KeyCode

        # ESC returns to STA view (not exit WiFi tab)
        if key == KeyCode.KEYCODE_ESC:
            self._view = VIEW_MAIN
            self._password = ""
            self._redraw(app)
            return True

        if key == KeyCode.KEYCODE_BACKSPACE:
            if self._password:
                self._password = self._password[:-1]
                self._redraw(app)
            return True

        if key == KeyCode.KEYCODE_ENTER:
            ssid = self._networks[self._selected][0]
            self._do_connect(app, ssid, self._password)
            return True

        if 32 <= key <= 126:
            self._password += chr(key)
            self._redraw(app)
            return True

        return True

    def _handle_ap_editor_key(self, app, key):
        """Handle keys in AP editor view."""
        from keycode import KEY_NAV_DOWN, KEY_NAV_UP, KeyCode

        # ESC returns to AP view (not exit WiFi tab)
        if key == KeyCode.KEYCODE_ESC:
            self._view = VIEW_MAIN
            self._redraw(app)
            return True

        if key in (KEY_NAV_UP, KEY_NAV_DOWN):
            self._ap_field = 1 - self._ap_field
            self._redraw(app)
            return True

        if key == KeyCode.KEYCODE_ENTER:
            self._apply_ap_config(app)
            return True

        if key == KeyCode.KEYCODE_BACKSPACE:
            if self._ap_field == 0:
                if self._ap_ssid_edit:
                    self._ap_ssid_edit = self._ap_ssid_edit[:-1]
            else:
                if self._ap_password_edit:
                    self._ap_password_edit = self._ap_password_edit[:-1]
            self._redraw(app)
            return True

        if 32 <= key <= 126:
            if self._ap_field == 0:
                if len(self._ap_ssid_edit) < 32:
                    self._ap_ssid_edit += chr(key)
            else:
                if len(self._ap_password_edit) < 63:
                    self._ap_password_edit += chr(key)
            self._redraw(app)
            return True

        return True
