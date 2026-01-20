"""
WiFi Tab - Network configuration
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
    SCREEN_W,
    WHITE,
    YELLOW,
    TabBase,
)


class WiFiTab(TabBase):
    """WiFi configuration tab."""

    def __init__(self):
        self.enabled = False
        self.networks = []
        self.selected = 0
        self.scanning = False
        self.connected_ssid = None
        self.password = ""
        self.input_mode = False
        self._wlan = None

    def _get_wlan(self):
        """Get or create WLAN instance."""
        if self._wlan is None:
            try:
                import network
                self._wlan = network.WLAN(network.STA_IF)
            except Exception as e:
                print(f"[wifi] WLAN init failed: {e}")
        return self._wlan

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

    def draw(self, app):
        """Draw WiFi tab content."""
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(1)

        wlan = self._get_wlan()
        if wlan:
            self.enabled = wlan.active()
            if wlan.isconnected():
                self.connected_ssid = wlan.config("essid")
            else:
                self.connected_ssid = None

        if self.input_mode:
            self._draw_password_input()
            return

        # WiFi status line
        Lcd.setTextColor(CYAN, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 3)
        Lcd.print("WiFi:")
        if self.enabled:
            if self.connected_ssid:
                Lcd.setTextColor(GREEN, BLACK)
                Lcd.setCursor(50, CONTENT_Y + 3)
                Lcd.print(self.connected_ssid[:25])
            else:
                Lcd.setTextColor(YELLOW, BLACK)
                Lcd.setCursor(50, CONTENT_Y + 3)
                Lcd.print("Not connected")
        else:
            Lcd.setTextColor(GRAY, BLACK)
            Lcd.setCursor(50, CONTENT_Y + 3)
            Lcd.print("Off")

        # Network list
        list_y = CONTENT_Y + 16
        max_visible = 3

        if self.scanning:
            Lcd.setTextColor(YELLOW, BLACK)
            Lcd.setCursor(80, list_y + 15)
            Lcd.print("Scanning...")
        elif not self.networks:
            Lcd.setTextColor(GRAY, BLACK)
            Lcd.setCursor(50, list_y + 15)
            Lcd.print("Press [S] to scan")
        else:
            start_idx = max(0, self.selected - max_visible + 1)
            for i in range(min(max_visible, len(self.networks) - start_idx)):
                idx = start_idx + i
                ssid, rssi, security = self.networks[idx]
                ny = list_y + i * 16

                if idx == self.selected:
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

                if ssid == self.connected_ssid:
                    Lcd.setTextColor(GREEN, DARK_GRAY if idx == self.selected else BLACK)
                    Lcd.setCursor(185, ny + 3)
                    Lcd.print("*")

        # Controls
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(5, CONTENT_Y + 70)
        if self.enabled:
            Lcd.print("[S]can  [O]ff")
        else:
            Lcd.print("[O]n")

        if self.connected_ssid:
            Lcd.setCursor(5, CONTENT_Y + 82)
            Lcd.print("[D]isconnect  [F]orget saved")
        elif self.enabled:
            saved_ssid, _ = self._load_credentials()
            if saved_ssid:
                Lcd.setTextColor(CYAN, BLACK)
                Lcd.setCursor(5, CONTENT_Y + 82)
                Lcd.print(f"Saved: {saved_ssid[:20]}")
                Lcd.setTextColor(GRAY, BLACK)
                Lcd.setCursor(5, CONTENT_Y + 94)
                Lcd.print("[C]onnect saved  [F]orget")

    def _draw_password_input(self):
        """Draw password input screen."""
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(1)

        ssid = self.networks[self.selected][0] if self.selected < len(self.networks) else "Network"

        Lcd.setTextColor(CYAN, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 5)
        Lcd.print(f"Connect to: {ssid[:18]}")

        Lcd.setTextColor(WHITE, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 25)
        Lcd.print("Password:")

        Lcd.fillRect(10, CONTENT_Y + 40, SCREEN_W - 20, 16, DARK_GRAY)
        Lcd.drawRect(10, CONTENT_Y + 40, SCREEN_W - 20, 16, WHITE)
        Lcd.setCursor(14, CONTENT_Y + 44)
        display_pw = "*" * len(self.password) + "_"
        Lcd.print(display_pw[:30])

        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 65)
        Lcd.print("[Enter] Connect  [ESC] Cancel")
        Lcd.setCursor(10, CONTENT_Y + 78)
        Lcd.print("[Bksp] Delete")

    def _redraw(self, app):
        """Redraw tab content."""
        Lcd.fillRect(0, CONTENT_Y, SCREEN_W, CONTENT_H, BLACK)
        self.draw(app)

    def toggle(self, app):
        """Toggle WiFi on/off."""
        wlan = self._get_wlan()
        if wlan:
            self.enabled = not self.enabled
            wlan.active(self.enabled)
            if not self.enabled:
                self.networks = []
                self.connected_ssid = None
            print(f"[wifi] {'enabled' if self.enabled else 'disabled'}")
        self._redraw(app)

    def scan(self, app):
        """Scan for networks."""
        wlan = self._get_wlan()
        if not wlan:
            return

        if not wlan.active():
            print("[wifi] Activating for scan...")
            wlan.active(True)
            self.enabled = True
            import time
            time.sleep_ms(500)

        self.scanning = True
        self._redraw(app)

        try:
            networks = wlan.scan()
            self.networks = []
            for net in networks:
                ssid = net[0].decode("utf-8") if isinstance(net[0], bytes) else net[0]
                rssi = net[3]
                security = net[4]
                if ssid:
                    self.networks.append((ssid, rssi, security))
            self.networks.sort(key=lambda x: x[1], reverse=True)
            self.selected = 0
            print(f"[wifi] Found {len(self.networks)} networks")
        except Exception as e:
            print(f"[wifi] Scan failed: {e}")
        finally:
            self.scanning = False
            self._redraw(app)

    def connect(self, app):
        """Connect to selected network."""
        if not self.networks or self.selected >= len(self.networks):
            return

        ssid, rssi, security = self.networks[self.selected]
        if security == 0:
            self._do_connect(app, ssid, "")
        else:
            self.password = ""
            self.input_mode = True
            self._redraw(app)

    def _do_connect(self, app, ssid, password):
        """Actually connect to network."""
        wlan = self._get_wlan()
        if not wlan:
            return

        print(f"[wifi] Connecting to {ssid}...")
        Lcd.fillRect(0, CONTENT_Y, SCREEN_W, CONTENT_H, BLACK)
        Lcd.setTextColor(YELLOW, BLACK)
        Lcd.setCursor(60, CONTENT_Y + 40)
        Lcd.print("Connecting...")

        import time
        connected = False

        try:
            if wlan.isconnected():
                wlan.disconnect()
                time.sleep_ms(300)

            wlan.connect(ssid, password)

            for i in range(100):
                if wlan.isconnected():
                    time.sleep_ms(1000)
                    if wlan.isconnected():
                        connected = True
                        break
                time.sleep_ms(100)

            if connected:
                self.connected_ssid = ssid
                print(f"[wifi] Connected to {ssid}")
                self._save_credentials(ssid, password)
            else:
                self.connected_ssid = None
                try:
                    wlan.disconnect()
                except:
                    pass
                print("[wifi] Connection failed")
                Lcd.fillRect(0, CONTENT_Y, SCREEN_W, CONTENT_H, BLACK)
                Lcd.setTextColor(0xFF0000, BLACK)
                Lcd.setCursor(50, CONTENT_Y + 40)
                Lcd.print("Connection failed!")
                time.sleep_ms(1500)

        except Exception as e:
            print(f"[wifi] Connect failed: {e}")
            self.connected_ssid = None

        self.input_mode = False
        self._redraw(app)

    def disconnect(self, app):
        """Disconnect from current network."""
        wlan = self._get_wlan()
        if wlan and wlan.isconnected():
            wlan.disconnect()
            self.connected_ssid = None
            print("[wifi] Disconnected")
        self._redraw(app)

    def _save_credentials(self, ssid, password):
        """Save credentials to NVS."""
        try:
            import esp32
            nvs = esp32.NVS("wifi")
            nvs.set_blob("ssid", ssid.encode("utf-8"))
            nvs.set_blob("password", password.encode("utf-8"))
            nvs.commit()
            print(f"[wifi] Credentials saved for {ssid}")
        except Exception as e:
            print(f"[wifi] Failed to save credentials: {e}")

    def _load_credentials(self):
        """Load credentials from NVS."""
        try:
            import esp32
            nvs = esp32.NVS("wifi")
            ssid_buf = bytearray(64)
            ssid_len = nvs.get_blob("ssid", ssid_buf)
            ssid = ssid_buf[:ssid_len].decode("utf-8") if ssid_len else None
            pwd_buf = bytearray(64)
            pwd_len = nvs.get_blob("password", pwd_buf)
            password = pwd_buf[:pwd_len].decode("utf-8") if pwd_len else ""
            if ssid:
                return ssid, password
        except Exception as e:
            print(f"[wifi] No saved credentials: {e}")
        return None, None

    def forget(self, app):
        """Forget saved credentials."""
        try:
            import esp32
            nvs = esp32.NVS("wifi")
            nvs.erase_key("ssid")
            nvs.erase_key("password")
            nvs.commit()
            print("[wifi] Credentials forgotten")
        except Exception as e:
            print(f"[wifi] Failed to forget: {e}")
        self._redraw(app)

    def handle_key(self, app, key):
        """Handle key press."""
        from libs.keycode import KEY_NAV_DOWN, KEY_NAV_UP, KeyCode

        if self.input_mode:
            if key == KeyCode.KEYCODE_ESC:
                self.input_mode = False
                self.password = ""
                self._redraw(app)
                return True

            if key == KeyCode.KEYCODE_BACKSPACE:
                if self.password:
                    self.password = self.password[:-1]
                    self._redraw(app)
                return True

            if key == KeyCode.KEYCODE_ENTER:
                ssid = self.networks[self.selected][0]
                self._do_connect(app, ssid, self.password)
                return True

            if 32 <= key <= 126:
                self.password += chr(key)
                self._redraw(app)
                return True

            return True

        # Normal mode
        if key == ord("o") or key == ord("O"):
            self.toggle(app)
            return True

        if key == ord("s") or key == ord("S"):
            self.scan(app)
            return True

        if key == KEY_NAV_UP:
            if self.networks and self.selected > 0:
                self.selected -= 1
                self._redraw(app)
            return True

        if key == KEY_NAV_DOWN:
            if self.networks and self.selected < len(self.networks) - 1:
                self.selected += 1
                self._redraw(app)
            return True

        if key == KeyCode.KEYCODE_ENTER:
            if self.networks:
                self.connect(app)
            return True

        if key == ord("d") or key == ord("D"):
            self.disconnect(app)
            return True

        if key == ord("f") or key == ord("F"):
            self.forget(app)
            return True

        if key == ord("c") or key == ord("C"):
            saved_ssid, saved_pwd = self._load_credentials()
            if saved_ssid:
                wlan = self._get_wlan()
                if wlan and not wlan.active():
                    print("[wifi] Activating for saved connection...")
                    wlan.active(True)
                    self.enabled = True
                    import time
                    time.sleep_ms(500)
                self._do_connect(app, saved_ssid, saved_pwd)
            return True

        return False
