## 1. Library Infrastructure

- [x] 1.1 Create `lib/wifi_constants.py` with NVS keys and defaults
- [x] 1.2 Update `lib/wifi_manager.py` for independent STA/AP control:
      - Remove mode-based API (set_mode, get_mode, cycle_mode)
      - Add sta_enable(), sta_disable(), sta_is_enabled()
      - Add ap_enable(), ap_disable(), ap_is_enabled()
      - Keep existing: sta_connect, sta_disconnect, sta_scan, sta_is_connected, sta_get_ip
      - Keep existing: ap_get_ip, ap_get_clients, ap_set_config
      - Update NVS: save/restore sta_enabled and ap_enabled separately
- [x] 1.3 Update `lib/wifi_constants.py`:
      - Remove WIFI_MODE_* constants (no longer needed)
      - Add NVS_KEY_STA_ENABLED = "sta_on"
      - Add NVS_KEY_AP_ENABLED = "ap_on"
- [x] 1.4 Update boot.py to restore STA/AP states independently

## 2. Sub-tab UI Framework

- [x] 2.1 Add sub-tab state: `_subtab` (0=STA, 1=AP)
- [x] 2.2 Draw sub-tab bar with `[S]TA` and `[A]P` labels
- [x] 2.3 Highlight selected sub-tab (inverted colors)
- [x] 2.4 Handle `S` key to switch to STA sub-tab
- [x] 2.5 Handle `A` key to switch to AP sub-tab

## 3. STA Sub-tab Views

- [x] 3.1 STA Off view: show "WiFi radio disabled", prompt [O]n
- [x] 3.2 STA On (not connected): show network list, [O]ff [S]can [C]onnect saved
- [x] 3.3 STA On (connected): show status + IP, network list, [O]ff [S]can [D]isconnect
- [x] 3.4 Network list with signal bars, SSID, security type
- [x] 3.5 Network selection (up/down navigation, Enter to connect)
- [x] 3.6 Password input screen for secured networks
- [x] 3.7 Fix ESC in password input: return to STA view (not exit WiFi tab)

## 4. AP Sub-tab Views

- [x] 4.1 AP Off view: show saved SSID/pass, prompt [O]n [E]dit
- [x] 4.2 AP On (no clients): show SSID + IP, "Waiting for connections...", [O]ff [E]dit
- [x] 4.3 AP On (with clients): show SSID + IP + client list, [O]ff [E]dit
- [x] 4.4 AP config editor: SSID and password fields
- [x] 4.5 Field selection (up/down navigation)
- [x] 4.6 Text input for SSID (visible) and password (masked)
- [x] 4.7 Apply (save + restart AP if active) and Cancel (discard)
- [x] 4.8 Fix ESC in AP editor: return to AP view (not exit WiFi tab)

## 5. Key Handling

- [x] 5.1 `[O]` toggles current interface on/off (context-aware)
- [x] 5.2 STA context: `[S]` scans, `[D]` disconnects, `[C]` connects saved
- [x] 5.3 AP context: `[E]` opens config editor
- [x] 5.4 Global: `[S]` switches to STA, `[A]` switches to AP (when not in editor)

## 6. Testing

- [ ] 6.1 Test STA enable/disable and persistence across reboots
- [ ] 6.2 Test AP enable/disable and persistence across reboots
- [ ] 6.3 Test both STA and AP enabled simultaneously
- [ ] 6.4 Test boot.py restores correct STA/AP states
- [ ] 6.5 Test ESC returns to correct view (not exit tab)
- [ ] 6.6 Test AP creation and client connections

## 7. Optional Enhancements

- [ ] 7.1 Auto-generate default AP SSID from device ID (e.g., "Cardputer-XXXX")
- [x] 7.2 Show list of connected clients with MAC when AP is active
