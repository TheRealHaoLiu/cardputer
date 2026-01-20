## Context

Adding WiFi AP mode to settings requires new infrastructure that could benefit other apps (webserver demo, future captive portal, etc.). This design captures implementation decisions for reusability and maintainability.

## Goals / Non-Goals

**Goals:**
- Clean, reusable WiFi management code in lib/
- Constants for mode values and NVS keys
- Leverage existing MicroPython libraries where appropriate

**Non-Goals:**
- Full-featured captive portal (future work)
- mDNS/DNS-SD (future work)

## Decisions

### 1. Constants Module

Create `lib/wifi_constants.py` for shared constants:

```python
# WiFi modes
WIFI_MODE_OFF = 0
WIFI_MODE_STA = 1
WIFI_MODE_AP = 2
WIFI_MODE_STA_AP = 3

# NVS
NVS_NAMESPACE = "cardputer_wifi"
NVS_KEY_MODE = "mode"
NVS_KEY_STA_SSID = "sta_ssid"
NVS_KEY_STA_PASSWORD = "sta_password"
NVS_KEY_AP_SSID = "ap_ssid"
NVS_KEY_AP_PASSWORD = "ap_password"

# Defaults
DEFAULT_AP_SSID = "Cardputer-AP"
DEFAULT_AP_IP = "192.168.4.1"
```

### 2. WiFi Manager Library

Extract reusable WiFi logic into `lib/wifi_manager.py`:

```python
class WiFiManager:
    """Manages WiFi STA and AP interfaces."""

    def __init__(self):
        self._sta = None
        self._ap = None
        self._mode = WIFI_MODE_OFF

    # Mode management
    def set_mode(self, mode): ...
    def get_mode(self): ...

    # STA operations
    def sta_connect(self, ssid, password): ...
    def sta_disconnect(self): ...
    def sta_scan(self): ...
    def sta_is_connected(self): ...
    def sta_get_ip(self): ...

    # AP operations
    def ap_start(self, ssid, password=""): ...
    def ap_stop(self): ...
    def ap_get_ip(self): ...
    def ap_get_clients(self): ...

    # NVS persistence
    def save_config(self): ...
    def load_config(self): ...
```

Benefits:
- Shared between wifi_tab.py, boot.py, webserver_demo.py
- Single source of truth for WiFi state
- Testable in isolation

### 3. External Libraries

**Already available in UIFlow2:**
- `network` - built-in MicroPython WiFi module (use this)
- `esp32` - NVS access (use this)

**Not needed:**
- microdot - already used for webserver, not needed for WiFi
- No additional external deps required for AP mode

**UIFlow Reference Implementations:**
- `m5stack/uiflow-micropython/tests/wlan/test_wlan_ap.py` - AP mode test
- `m5stack/uiflow-micropython/examples/system/wlan_ap/wlan_ap_cores3_example.py` - Simple AP example
- `m5stack/uiflow-micropython/m5stack/modules/startup/nesson1.py` - Full captive portal (lines 534-826)

**Future consideration:**
- Captive portal for phone-based WiFi config (no keyboard needed)
  - UIFlow reference: `nesson1.py` SetupApp class with DNS + Microdot
  - See: https://github.com/metachris/micropython-captiveportal
  - See: https://github.com/george-hawkins/micropython-wifi-setup
- mDNS for .local hostname resolution
- Webserver demo AP fallback
  - Use WiFiManager to offer "Use saved WiFi" or "Create hotspot"
  - Fallback to AP mode if no STA credentials saved
  - Makes webserver accessible without existing WiFi network

## UIFlow Patterns Reference

### AP Mode Configuration

From `test_wlan_ap.py` and `wlan_ap_cores3_example.py`:

```python
import network

# Create and configure AP
wlan = network.WLAN(network.AP_IF)
wlan.active(False)  # Deactivate first for clean config
wlan.active(True)

# Configuration options
wlan.config(essid="Cardputer-AP")
wlan.config(password="password123")  # Min 8 chars for WPA2
wlan.config(authmode=network.AUTH_WPA_WPA2_PSK)  # Or AUTH_OPEN
wlan.config(max_clients=4)
wlan.config(txpower=20)  # dBm
wlan.config(dhcp_hostname="cardputer")
wlan.config(hidden=False)  # Hide/show SSID
wlan.config(channel=6)  # WiFi channel

# Status checks
wlan.isconnected()  # True if clients connected
wlan.ifconfig()  # (ip, netmask, gateway, dns) - default AP IP: 192.168.4.1
wlan.status("stations")  # List of connected client tuples
```

### Interface Constants

```python
# Interface types
network.AP_IF           # Access Point interface
network.STA_IF          # Station interface
network.WLAN.IF_AP      # Alternative constant
network.WLAN.IF_STA     # Alternative constant

# Auth modes
network.AUTH_OPEN              # Open network (no password)
network.AUTH_WPA_WPA2_PSK      # WPA/WPA2 with password
```

### Auto-Generated AP Name Pattern

From `nesson1.py`:

```python
import binascii
import machine

# Generate unique AP name from device ID
device_id = binascii.hexlify(machine.unique_id()).upper().decode()
ap_name = "Cardputer-" + device_id[-4:]  # e.g., "Cardputer-A1B2"
```

### NVS Storage Pattern

From UIFlow startup modules:

```python
import esp32

nvs = esp32.NVS("cardputer_wifi")

# String storage (for SSID/password)
nvs.set_str("sta_ssid", ssid)
nvs.set_str("sta_password", password)
nvs.commit()

# Reading strings
ssid = nvs.get_str("sta_ssid")

# Integer storage (for mode)
nvs.set_i32("mode", WIFI_MODE_STA)
mode = nvs.get_i32("mode")
```

### Connected Clients Info

```python
# Get list of connected stations
stations = wlan.status("stations")
# Returns list of tuples: [(mac_bytes, rssi), ...]

for mac, rssi in stations:
    mac_str = ":".join("{:02x}".format(b) for b in mac)
    print(f"Client: {mac_str}, RSSI: {rssi}")
```

## Risks / Trade-offs

**Risk:** WiFiManager singleton vs instance
- Mitigation: Use module-level instance, lazy init

**Risk:** Memory overhead of new lib module
- Mitigation: Lazy import, keep module small (~100 lines)

## File Structure

```
lib/
├── wifi_constants.py    # Constants (new)
├── wifi_manager.py      # WiFi management (new)
├── framework.py         # Existing
├── app_base.py          # Existing
└── keycode.py           # Existing

apps/settings/
└── wifi_tab.py          # Uses WiFiManager

boot.py                  # Uses WiFiManager
```

## Open Questions

- Should WiFiManager be a singleton or passed as dependency?
  - Recommend: module-level instance for simplicity
