"""
WiFi Constants - Shared constants for WiFi management.

This module defines NVS keys and defaults used by WiFiManager,
wifi_tab.py, and boot.py.

Note: STA and AP are controlled independently (no combined "mode").
"""

# NVS namespace and keys (clean break from old "wifi" namespace)
NVS_NAMESPACE = "cardputer_wifi"
NVS_KEY_STA_ENABLED = "sta_on"
NVS_KEY_AP_ENABLED = "ap_on"
NVS_KEY_STA_SSID = "sta_ssid"
NVS_KEY_STA_PASSWORD = "sta_password"
NVS_KEY_AP_SSID = "ap_ssid"
NVS_KEY_AP_PASSWORD = "ap_password"

# Default AP settings
DEFAULT_AP_SSID = "Cardputer-AP"
DEFAULT_AP_PASSWORD = ""  # Open by default
DEFAULT_AP_IP = "192.168.4.1"
