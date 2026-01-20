# Change: Add WiFi Access Point Mode

## Why
The WiFi tab currently only supports station mode (connecting to networks). Users need the ability to create their own WiFi hotspot for scenarios like file sharing, serving a web UI, or device configuration when no WiFi network is available.

## What Changes
- Add three WiFi modes: STA (station), AP (access point), STA+AP (dual mode)
- Add AP configuration: SSID and password
- Display connected clients when AP is active
- Show AP IP address for other devices to connect
- In STA+AP mode, show both IPs (STA from router, AP at 192.168.4.1)
- Persist AP settings and mode selection to NVS

## Impact
- Affected specs: settings-app (WiFi tab, boot initialization)
- Affected code:
  - `lib/wifi_constants.py` - new constants module
  - `lib/wifi_manager.py` - new reusable WiFi management library
  - `apps/settings/wifi_tab.py` - mode UI, AP/STA config editors (uses WiFiManager)
  - `boot.py` - restore WiFi mode on boot (uses WiFiManager)
- NVS: all WiFi settings in `cardputer_wifi` namespace (clean break, no migration)
