# -*- encoding: utf-8 -*-
# boot.py - Simple boot that runs main.py
import M5


def _wifi_boot_connect():
    """Connect to WiFi on boot if enabled and credentials exist."""
    try:
        import esp32

        # Check if WiFi is enabled (wifi_on in settings namespace)
        try:
            nvs_settings = esp32.NVS("settings")
            wifi_on = nvs_settings.get_i32("wifi_on")
        except OSError:
            # Key doesn't exist - WiFi not explicitly enabled
            return

        if wifi_on != 1:
            return

        # Load credentials from wifi namespace
        try:
            nvs_wifi = esp32.NVS("wifi")
            ssid_buf = bytearray(64)
            ssid_len = nvs_wifi.get_blob("ssid", ssid_buf)
            if not ssid_len:
                return
            ssid = ssid_buf[:ssid_len].decode("utf-8")

            pwd_buf = bytearray(64)
            pwd_len = nvs_wifi.get_blob("password", pwd_buf)
            password = pwd_buf[:pwd_len].decode("utf-8") if pwd_len else ""
        except OSError:
            # No credentials saved
            return

        # Connect to WiFi
        import network
        import time

        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        time.sleep_ms(100)

        print(f"[boot] Connecting to {ssid}...")
        wlan.connect(ssid, password)

        # Wait up to 10 seconds for connection
        for _ in range(100):
            if wlan.isconnected():
                print(f"[boot] Connected to {ssid}")
                return
            time.sleep_ms(100)

        print("[boot] WiFi connection timeout")

    except Exception as e:
        print(f"[boot] WiFi connect failed: {e}")


if __name__ == "__main__":
    M5.begin()
    _wifi_boot_connect()
