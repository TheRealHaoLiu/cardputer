## Context

Adding WiFi AP mode to settings requires new infrastructure that could benefit other apps (webserver demo, future captive portal, etc.). This design captures implementation decisions for reusability and maintainability.

## Goals / Non-Goals

**Goals:**
- Clean, reusable WiFi management code in lib/
- Constants for mode values and NVS keys
- Leverage existing MicroPython libraries where appropriate
- Intuitive sub-tab UI for independent STA/AP control

**Non-Goals:**
- Full-featured captive portal (future work)
- mDNS/DNS-SD (future work)

## Decisions

### 1. UI Architecture: Sub-tabs over Mode Cycling

**Problem with mode cycling:**
The original design used a single mode that cycles through OFF→STA→AP→STA+AP. This created UX issues:
- Users couldn't independently control STA and AP
- Confusing when you want to disconnect STA but keep AP running
- No way to turn off just one interface

**Solution: Independent sub-tabs**
The WiFi tab contains two sub-tabs: `[S]TA` and `[A]P`. Each can be toggled on/off independently.

```
┌──────────────────────────────────────┐
│  ▓[S]TA▓   [A]P                      │  <- Sub-tab bar (S/A to switch)
├──────────────────────────────────────┤
│ Status: Connected   IP: 192.168.1.50 │  <- Context-specific content
│ > HomeWifi          ████ WPA     *   │
│   OfficeNet         ███  WPA         │
├──────────────────────────────────────┤
│ [O]ff [S]can [D]isconnect            │  <- Context-specific controls
└──────────────────────────────────────┘
```

**Key bindings:**
| Key | Action |
|-----|--------|
| `S` | Switch to STA sub-tab |
| `A` | Switch to AP sub-tab |
| `O` | Toggle current interface on/off |
| `↑/↓` | Navigate network list (STA) or fields (AP editor) |
| `Enter` | Connect to network (STA) or apply changes (AP editor) |
| `ESC` | Cancel current operation (password input, AP editor) |

**STA-specific keys (when STA sub-tab active):**
| Key | Action |
|-----|--------|
| `S` | Scan for networks (context: already in STA tab) |
| `D` | Disconnect from current network |
| `C` | Connect to saved network |

**AP-specific keys (when AP sub-tab active):**
| Key | Action |
|-----|--------|
| `E` | Edit AP configuration (SSID/password) |

### 2. Sub-tab Visual States

**STA Sub-tab States:**

Off:
```
│  ▓[S]TA▓   [A]P                      │
├──────────────────────────────────────┤
│ Status: Off                          │
│                                      │
│       WiFi radio disabled            │
│       Press [O] to enable            │
├──────────────────────────────────────┤
│ [O]n                                 │
```

On, not connected:
```
│  ▓[S]TA▓   [A]P                      │
├──────────────────────────────────────┤
│ Status: Not connected                │
│                                      │
│ > HomeWifi          ████ WPA         │
│   OfficeNet         ███  WPA         │
├──────────────────────────────────────┤
│ [O]ff [S]can [C]onnect saved         │
```

On, connected:
```
│  ▓[S]TA▓   [A]P                      │
├──────────────────────────────────────┤
│ Status: Connected   IP: 192.168.1.50 │
│                                      │
│ > HomeWifi          ████ WPA     *   │
│   OfficeNet         ███  WPA         │
├──────────────────────────────────────┤
│ [O]ff [S]can [D]isconnect            │
```

**AP Sub-tab States:**

Off:
```
│  [S]TA   ▓[A]P▓                      │
├──────────────────────────────────────┤
│ Status: Off                          │
│ SSID: Cardputer-AP                   │
│ Pass: ********                       │
│                                      │
│       Press [O] to start             │
├──────────────────────────────────────┤
│ [O]n [E]dit                          │
```

On, no clients:
```
│  [S]TA   ▓[A]P▓                      │
├──────────────────────────────────────┤
│ SSID: Cardputer-AP   IP: 192.168.4.1 │
│ Clients: 0                           │
│                                      │
│       Waiting for connections...     │
├──────────────────────────────────────┤
│ [O]ff [E]dit                         │
```

On, with clients:
```
│  [S]TA   ▓[A]P▓                      │
├──────────────────────────────────────┤
│ SSID: Cardputer-AP   IP: 192.168.4.1 │
│ Clients: 2                           │
│   aa:bb:cc:dd:ee:ff                  │
│   11:22:33:44:55:66                  │
├──────────────────────────────────────┤
│ [O]ff [E]dit                         │
```

### 3. Password Input Screen (STA)

When connecting to a secured network:
```
├──────────────────────────────────────┤
│ Connect to: HomeWifi                 │
│                                      │
│ Password:                            │
│ ┌────────────────────────────────┐   │
│ │ **********_                    │   │
│ └────────────────────────────────┘   │
├──────────────────────────────────────┤
│ [Enter] Connect  [ESC] Cancel        │
```

**ESC behavior:** Returns to STA network list (not exit WiFi tab).

### 4. AP Config Editor

When editing AP settings:
```
├──────────────────────────────────────┤
│ AP Configuration                     │
│                                      │
│ ▓SSID: Cardputer-AP_▓                │  <- Selected field highlighted
│  Pass: ********                      │
│                                      │
├──────────────────────────────────────┤
│ [Enter] Apply  [ESC] Cancel          │
```

**ESC behavior:** Returns to AP status view (discards changes).

### 5. Constants Module

Create `lib/wifi_constants.py` for shared constants:

```python
# NVS
NVS_NAMESPACE = "cardputer_wifi"
NVS_KEY_STA_ENABLED = "sta_on"
NVS_KEY_AP_ENABLED = "ap_on"
NVS_KEY_STA_SSID = "sta_ssid"
NVS_KEY_STA_PASSWORD = "sta_password"
NVS_KEY_AP_SSID = "ap_ssid"
NVS_KEY_AP_PASSWORD = "ap_password"

# Defaults
DEFAULT_AP_SSID = "Cardputer-AP"
DEFAULT_AP_IP = "192.168.4.1"
```

Note: Mode constants (WIFI_MODE_OFF, etc.) are no longer needed since STA and AP are independent.

### 6. WiFi Manager Library

Extract reusable WiFi logic into `lib/wifi_manager.py`:

```python
class WiFiManager:
    """Manages WiFi STA and AP interfaces independently."""

    def __init__(self):
        self._sta = None
        self._ap = None
        self._sta_enabled = False
        self._ap_enabled = False

    # STA operations
    def sta_enable(self): ...
    def sta_disable(self): ...
    def sta_is_enabled(self): ...
    def sta_connect(self, ssid, password): ...
    def sta_disconnect(self): ...
    def sta_scan(self): ...
    def sta_is_connected(self): ...
    def sta_get_ip(self): ...
    def sta_get_ssid(self): ...

    # AP operations
    def ap_enable(self, ssid=None, password=None): ...
    def ap_disable(self): ...
    def ap_is_enabled(self): ...
    def ap_get_ip(self): ...
    def ap_get_ssid(self): ...
    def ap_get_password(self): ...
    def ap_get_clients(self): ...
    def ap_set_config(self, ssid, password): ...

    # NVS persistence
    def save_config(self): ...
    def load_config(self): ...
    def restore_state(self): ...  # Called at boot
```

### 7. External Libraries

**Already available in UIFlow2:**
- `network` - built-in MicroPython WiFi module (use this)
- `esp32` - NVS access (use this)

**Not needed:**
- microdot - already used for webserver, not needed for WiFi
- No additional external deps required for AP mode

**UIFlow Reference Implementations:**
- `m5stack/uiflow-micropython/tests/wlan/test_wlan_ap.py` - AP mode test
- `m5stack/uiflow-micropython/examples/system/wlan_ap/wlan_ap_cores3_example.py` - Simple AP example

**Future consideration:**
- Captive portal for phone-based WiFi config (no keyboard needed)
- mDNS for .local hostname resolution

## UIFlow Patterns Reference

### AP Mode Configuration

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
```

### Connected Clients Info

```python
# Get list of connected stations
stations = wlan.status("stations")
# Returns list of tuples: [(mac_bytes, rssi), ...]

for mac, rssi in stations:
    mac_str = ":".join(f"{b:02x}" for b in mac)
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
