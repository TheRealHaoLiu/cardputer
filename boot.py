# boot.py - Boot sequence with WiFi state restoration
import sys

# Add lib path before any imports
for path in ["/flash/lib", "/remote/lib"]:
    if path not in sys.path:
        sys.path.insert(0, path)

import M5


def _wifi_boot_restore():
    """Restore WiFi STA/AP states and connections on boot."""
    try:
        from wifi_manager import get_wifi_manager

        wifi = get_wifi_manager()
        wifi.restore_state()
    except Exception as e:
        print(f"[boot] WiFi restore failed: {e}")


if __name__ == "__main__":
    M5.begin()
    _wifi_boot_restore()
