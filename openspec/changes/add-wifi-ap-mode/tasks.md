## 1. Library Infrastructure

- [ ] 1.1 Create `lib/wifi_constants.py` with mode constants and NVS keys
- [ ] 1.2 Create `lib/wifi_manager.py` with WiFiManager class:
      - Mode management (set_mode, get_mode)
      - STA operations (connect, disconnect, scan, is_connected, get_ip)
      - AP operations (start, stop, get_ip, get_clients)
      - NVS persistence (save_config, load_config)
- [ ] 1.3 NVS structure in "cardputer_wifi" namespace:
      - `mode`: i32 (WIFI_MODE_OFF=0, WIFI_MODE_STA=1, WIFI_MODE_AP=2, WIFI_MODE_STA_AP=3)
      - `sta_ssid`, `sta_password`: blob (STA credentials)
      - `ap_ssid`, `ap_password`: blob (AP settings)
- [ ] 1.4 Update boot.py to use WiFiManager for all four modes
- [ ] 1.5 Update wifi_tab.py to use WiFiManager (remove duplicated WiFi logic)

## 2. Reusable STA Config Editor

- [ ] 2.1 Refactor existing network scan/connect UI into STA config editor component
- [ ] 2.2 Network list with signal bars, SSID, security type
- [ ] 2.3 Network selection (up/down navigation, Enter to connect)
- [ ] 2.4 Password input screen for secured networks (masked input)
- [ ] 2.5 Scan, connect, disconnect functions
- [ ] 2.6 ESC behavior: exit to dual status view (STA+AP) or cycle mode (STA)
- [ ] 2.7 Wire editor to be callable from both STA mode and STA+AP mode

## 3. Reusable AP Config Editor

- [ ] 3.1 Create AP config editor component (menu with SSID/Password fields)
- [ ] 3.2 Implement field selection (up/down navigation)
- [ ] 3.3 Implement text input for SSID (visible) and password (masked)
- [ ] 3.4 Implement Apply (save + restart AP if active) and Cancel (discard)
- [ ] 3.5 Wire editor to be callable from both AP mode and STA+AP mode

## 4. Mode-Specific Views

- [ ] 4.1 Implement Off mode view (prompt to press M)
- [ ] 4.2 STA mode: display STA config editor as main view
- [ ] 4.3 AP mode: AP status view (IP, clients) + [E]dit to open AP config editor
- [ ] 4.4 STA+AP mode: dual status view + [S]can for STA editor + [E]dit for AP editor

## 5. Testing

- [ ] 5.1 Test mode cycling and persistence across reboots
- [ ] 5.2 Test boot.py restores correct mode (Off, STA, AP, STA+AP)
- [ ] 5.3 Test AP creation and client connections
- [ ] 5.4 Test STA+AP dual mode - verify both interfaces work independently
- [ ] 5.5 Test STA config editor from both STA and STA+AP modes
- [ ] 5.6 Test AP config editor from both AP and STA+AP modes

## 6. Optional Enhancements

- [ ] 6.1 Auto-generate default AP SSID from device name (e.g., "Cardputer-XXXX")
- [ ] 6.2 Show list of connected clients with IP/MAC when AP is active
