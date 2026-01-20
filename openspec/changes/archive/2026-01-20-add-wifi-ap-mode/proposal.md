# Change: Add WiFi Access Point Mode

## Why
The WiFi tab currently only supports station mode (connecting to networks). Users need the ability to create their own WiFi hotspot for scenarios like file sharing, serving a web UI, or device configuration when no WiFi network is available.

## What Changes
- Add sub-tab navigation within WiFi tab: `[S]TA` and `[A]P`
- STA and AP can be controlled independently with `[O]n/[O]ff` toggle
- Add AP configuration: SSID and password editor
- Display connected clients when AP is active
- Show AP IP address for other devices to connect
- Both STA and AP can be active simultaneously
- Persist STA/AP enabled states and settings to NVS

## UI Design

### Sub-tab Navigation
The WiFi tab contains two sub-tabs: `[S]TA` and `[A]P`. Press `S` or `A` to switch between them. The selected sub-tab is highlighted.

### STA Sub-tab (selected)
```
┌──────────────────────────────────────┐
│  ▓[S]TA▓   [A]P                      │
├──────────────────────────────────────┤
│ Status: Connected   IP: 192.168.1.50 │
│                                      │
│ > HomeWifi          ████ WPA     *   │
│   OfficeNet         ███  WPA         │
├──────────────────────────────────────┤
│ [O]ff [S]can [D]isconnect            │
└──────────────────────────────────────┘
```

### AP Sub-tab (selected, active)
```
┌──────────────────────────────────────┐
│  [S]TA   ▓[A]P▓                      │
├──────────────────────────────────────┤
│ SSID: Cardputer-AP   IP: 192.168.4.1 │
│ Clients: 2                           │
│   aa:bb:cc:dd:ee:ff                  │
│   11:22:33:44:55:66                  │
├──────────────────────────────────────┤
│ [O]ff [E]dit                         │
└──────────────────────────────────────┘
```

### Key Bindings
- `[S]` - Switch to STA sub-tab
- `[A]` - Switch to AP sub-tab
- `[O]` - Toggle on/off (context-aware: STA or AP depending on active sub-tab)
- In STA sub-tab: `[S]can`, `[D]isconnect`, `[C]onnect saved`, arrows + Enter
- In AP sub-tab: `[E]dit` config

## Impact
- Affected specs: settings-app (WiFi tab, boot initialization)
- Affected code:
  - `lib/wifi_constants.py` - new constants module
  - `lib/wifi_manager.py` - new reusable WiFi management library
  - `apps/settings/wifi_tab.py` - sub-tab UI, AP/STA controls (uses WiFiManager)
  - `boot.py` - restore WiFi state on boot (uses WiFiManager)
- NVS: all WiFi settings in `cardputer_wifi` namespace (clean break, no migration)
