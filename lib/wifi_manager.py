"""
WiFi Manager - Reusable WiFi management library.

Handles STA (station) and AP (access point) interfaces independently
with NVS persistence. Used by wifi_tab.py, boot.py, and other apps
needing WiFi functionality.
"""

import network
from wifi_constants import (
    DEFAULT_AP_IP,
    DEFAULT_AP_PASSWORD,
    DEFAULT_AP_SSID,
    NVS_KEY_AP_ENABLED,
    NVS_KEY_AP_PASSWORD,
    NVS_KEY_AP_SSID,
    NVS_KEY_STA_ENABLED,
    NVS_KEY_STA_PASSWORD,
    NVS_KEY_STA_SSID,
    NVS_NAMESPACE,
)


class WiFiManager:
    """Manages WiFi STA and AP interfaces independently."""

    def __init__(self):
        self._sta = None
        self._ap = None
        self._sta_enabled = False
        self._ap_enabled = False
        # Cached credentials (loaded from NVS)
        self._sta_ssid = None
        self._sta_password = None
        self._ap_ssid = DEFAULT_AP_SSID
        self._ap_password = DEFAULT_AP_PASSWORD

    # -------------------------------------------------------------------------
    # Interface accessors (lazy initialization)
    # -------------------------------------------------------------------------

    def _get_sta(self):
        """Get or create STA interface."""
        if self._sta is None:
            self._sta = network.WLAN(network.STA_IF)
        return self._sta

    def _get_ap(self):
        """Get or create AP interface."""
        if self._ap is None:
            self._ap = network.WLAN(network.AP_IF)
        return self._ap

    # -------------------------------------------------------------------------
    # STA enable/disable
    # -------------------------------------------------------------------------

    def sta_enable(self):
        """Enable STA interface (radio on)."""
        sta = self._get_sta()
        sta.active(True)
        self._sta_enabled = True
        print("[wifi] STA enabled")

    def sta_disable(self):
        """Disable STA interface (radio off, disconnects if connected)."""
        sta = self._get_sta()
        if sta.isconnected():
            sta.disconnect()
        sta.active(False)
        self._sta_enabled = False
        print("[wifi] STA disabled")

    def sta_is_enabled(self):
        """Check if STA interface is enabled."""
        sta = self._get_sta()
        return sta.active()

    # -------------------------------------------------------------------------
    # STA operations
    # -------------------------------------------------------------------------

    def sta_scan(self):
        """
        Scan for available networks.

        Returns:
            List of tuples: (ssid, rssi, security)
            Sorted by signal strength (strongest first).
        """
        sta = self._get_sta()
        if not sta.active():
            sta.active(True)
            self._sta_enabled = True
            import time

            time.sleep_ms(500)

        try:
            networks = sta.scan()
            result = []
            for net in networks:
                ssid = net[0].decode("utf-8") if isinstance(net[0], bytes) else net[0]
                rssi = net[3]
                security = net[4]
                if ssid:
                    result.append((ssid, rssi, security))
            result.sort(key=lambda x: x[1], reverse=True)
            return result
        except Exception as e:
            print(f"[wifi] Scan failed: {e}")
            return []

    def sta_connect(self, ssid, password, timeout_ms=10000):
        """
        Connect to a network in STA mode.

        Args:
            ssid: Network SSID
            password: Network password (empty string for open networks)
            timeout_ms: Connection timeout in milliseconds

        Returns:
            True if connected, False otherwise
        """
        sta = self._get_sta()
        if not sta.active():
            sta.active(True)
            import time

            time.sleep_ms(100)

        # Always mark as enabled when connecting
        self._sta_enabled = True

        import time

        # Disconnect if already connected
        if sta.isconnected():
            sta.disconnect()
            time.sleep_ms(300)

        print(f"[wifi] Connecting to {ssid}...")
        sta.connect(ssid, password)

        # Wait for connection
        iterations = timeout_ms // 100
        for _ in range(iterations):
            if sta.isconnected():
                # Double-check connection is stable
                time.sleep_ms(500)
                if sta.isconnected():
                    print(f"[wifi] Connected to {ssid}")
                    self._sta_ssid = ssid
                    self._sta_password = password
                    return True
            time.sleep_ms(100)

        # Connection failed - contextlib.suppress not available in MicroPython
        try:  # noqa: SIM105
            sta.disconnect()
        except Exception:
            pass
        print(f"[wifi] Connection to {ssid} failed")
        return False

    def sta_disconnect(self):
        """Disconnect from current network."""
        sta = self._get_sta()
        if sta.isconnected():
            sta.disconnect()
            print("[wifi] Disconnected")

    def sta_is_connected(self):
        """Check if connected to a network."""
        sta = self._get_sta()
        return sta.active() and sta.isconnected()

    def sta_get_ip(self):
        """Get STA IP address or None if not connected."""
        sta = self._get_sta()
        if sta.isconnected():
            return sta.ifconfig()[0]
        return None

    def sta_get_ssid(self):
        """Get connected SSID or None."""
        sta = self._get_sta()
        if sta.isconnected():
            try:
                return sta.config("essid")
            except Exception:
                return self._sta_ssid
        return None

    def get_sta_credentials(self):
        """Get saved STA credentials. Returns (ssid, password) or (None, None)."""
        return self._sta_ssid, self._sta_password

    # -------------------------------------------------------------------------
    # AP enable/disable
    # -------------------------------------------------------------------------

    def ap_enable(self, ssid=None, password=None):
        """
        Enable AP interface with given or saved settings.

        Args:
            ssid: AP name (uses saved/default if None)
            password: AP password (uses saved/default if None)
        """
        if ssid is not None:
            self._ap_ssid = ssid
        if password is not None:
            self._ap_password = password

        ap = self._get_ap()
        # UIFlow2: must be active, and set all config in one call
        ap.active(True)
        self._configure_ap(ap)
        self._ap_enabled = True
        print("[wifi] AP enabled")

    def ap_disable(self):
        """Disable AP interface."""
        ap = self._get_ap()
        ap.active(False)
        self._ap_enabled = False
        print("[wifi] AP disabled")

    def ap_is_enabled(self):
        """Check if AP interface is enabled."""
        ap = self._get_ap()
        return ap.active()

    # -------------------------------------------------------------------------
    # AP operations
    # -------------------------------------------------------------------------

    def _configure_ap(self, ap):
        """Configure AP (must be active, all params in one call for UIFlow2)."""
        try:
            # WPA2 requires minimum 8 character password
            if self._ap_password and len(self._ap_password) >= 8:
                print(f"[wifi] Configuring AP: {self._ap_ssid} (WPA2)")
                ap.config(
                    essid=self._ap_ssid,
                    authmode=network.AUTH_WPA_WPA2_PSK,
                    password=self._ap_password,
                )
            elif not self._ap_password:
                print(f"[wifi] Configuring AP: {self._ap_ssid} (open)")
                ap.config(essid=self._ap_ssid, authmode=network.AUTH_OPEN)
            else:
                # Invalid password (1-7 chars) - reject
                print("[wifi] AP config rejected: password must be 8+ chars or empty")
                return
            ap.config(max_clients=4)
        except Exception as e:
            print(f"[wifi] AP config failed: {e}")

    def ap_get_ip(self):
        """Get AP IP address (usually 192.168.4.1)."""
        ap = self._get_ap()
        if ap.active():
            return ap.ifconfig()[0]
        return DEFAULT_AP_IP

    def ap_get_ssid(self):
        """Get current AP SSID."""
        return self._ap_ssid

    def ap_get_password(self):
        """Get current AP password."""
        return self._ap_password

    def ap_get_clients(self):
        """
        Get list of connected clients.

        Returns:
            List of MAC address strings, or empty list
        """
        ap = self._get_ap()
        if not ap.active():
            return []

        # Try multiple methods as API varies by MicroPython variant
        # Note: contextlib.suppress not available in MicroPython
        stations = None

        # Method 1: status('stations') - works on some ESP32 builds
        try:  # noqa: SIM105
            stations = ap.status("stations")
        except Exception:
            pass

        # Method 2: config('stations') - standard MicroPython
        if stations is None:
            try:  # noqa: SIM105
                stations = ap.config("stations")
            except Exception:
                pass

        if not stations:
            return []

        result = []
        for station in stations:
            try:
                # Station format varies - may be bytes (MAC) or tuple
                if isinstance(station, bytes):
                    mac_str = ":".join(f"{b:02x}" for b in station)
                elif isinstance(station, tuple) and len(station) >= 1:
                    mac = station[0]
                    mac_str = ":".join(f"{b:02x}" for b in mac)
                else:
                    continue
                result.append(mac_str)
            except Exception:
                continue
        return result

    def ap_set_config(self, ssid, password):
        """Update AP configuration and restart if active."""
        self._ap_ssid = ssid
        self._ap_password = password
        if self.ap_is_enabled():
            # Reconfigure while active
            ap = self._get_ap()
            self._configure_ap(ap)

    # -------------------------------------------------------------------------
    # NVS persistence
    # -------------------------------------------------------------------------

    def save_config(self):
        """Save current configuration to NVS."""
        try:
            import esp32

            nvs = esp32.NVS(NVS_NAMESPACE)

            # Save STA/AP enabled states as integers (0/1)
            nvs.set_i32(NVS_KEY_STA_ENABLED, 1 if self._sta_enabled else 0)
            nvs.set_i32(NVS_KEY_AP_ENABLED, 1 if self._ap_enabled else 0)

            if self._sta_ssid:
                nvs.set_blob(NVS_KEY_STA_SSID, self._sta_ssid.encode("utf-8"))
                nvs.set_blob(NVS_KEY_STA_PASSWORD, (self._sta_password or "").encode("utf-8"))

            nvs.set_blob(NVS_KEY_AP_SSID, self._ap_ssid.encode("utf-8"))
            nvs.set_blob(NVS_KEY_AP_PASSWORD, (self._ap_password or "").encode("utf-8"))

            nvs.commit()
            print("[wifi] Config saved to NVS")
        except Exception as e:
            print(f"[wifi] Save config failed: {e}")

    def load_config(self):
        """Load configuration from NVS."""
        try:
            import esp32

            nvs = esp32.NVS(NVS_NAMESPACE)

            # Load STA/AP enabled states
            try:
                self._sta_enabled = nvs.get_i32(NVS_KEY_STA_ENABLED) != 0
            except OSError:
                self._sta_enabled = False

            try:
                self._ap_enabled = nvs.get_i32(NVS_KEY_AP_ENABLED) != 0
            except OSError:
                self._ap_enabled = False

            # Load STA credentials
            try:
                buf = bytearray(64)
                length = nvs.get_blob(NVS_KEY_STA_SSID, buf)
                self._sta_ssid = buf[:length].decode("utf-8") if length else None

                buf = bytearray(64)
                length = nvs.get_blob(NVS_KEY_STA_PASSWORD, buf)
                self._sta_password = buf[:length].decode("utf-8") if length else ""
            except OSError:
                self._sta_ssid = None
                self._sta_password = None

            # Load AP settings
            try:
                buf = bytearray(64)
                length = nvs.get_blob(NVS_KEY_AP_SSID, buf)
                self._ap_ssid = buf[:length].decode("utf-8") if length else DEFAULT_AP_SSID

                buf = bytearray(64)
                length = nvs.get_blob(NVS_KEY_AP_PASSWORD, buf)
                self._ap_password = buf[:length].decode("utf-8") if length else DEFAULT_AP_PASSWORD
            except OSError:
                self._ap_ssid = DEFAULT_AP_SSID
                self._ap_password = DEFAULT_AP_PASSWORD

            print(f"[wifi] Config loaded: sta={self._sta_enabled}, ap={self._ap_enabled}")
        except Exception as e:
            print(f"[wifi] Load config failed: {e}")
            self._sta_enabled = False
            self._ap_enabled = False

    def restore_state(self):
        """
        Load config and restore saved STA/AP states. Called at boot.

        For STA, attempts to connect to saved network if enabled.
        """
        self.load_config()

        # Restore STA state
        if self._sta_enabled:
            self.sta_enable()
            if self._sta_ssid:
                self.sta_connect(self._sta_ssid, self._sta_password or "")
        else:
            self.sta_disable()

        # Restore AP state
        if self._ap_enabled:
            self.ap_enable()
        else:
            self.ap_disable()


# Module-level singleton for shared access
_wifi_manager = None


def get_wifi_manager():
    """Get the shared WiFiManager instance."""
    global _wifi_manager
    if _wifi_manager is None:
        _wifi_manager = WiFiManager()
    return _wifi_manager


def reset_wifi_manager():
    """Reset singleton for hot-reload. Creates fresh instance on next get."""
    global _wifi_manager
    _wifi_manager = None
