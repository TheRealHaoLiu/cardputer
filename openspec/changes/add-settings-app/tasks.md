# Implementation Tasks

## Revised Approach

Implementing incrementally, one small step at a time. Each step should be tested before moving to the next.

---

## Step 1: Tab Framework ✅ COMPLETE

Create basic tab structure with blank content.

- [x] 1.1 Create minimal `SettingsApp` class with AppBase
- [x] 1.2 Draw tab bar with 5 tabs (WiFi, Display, Sound, System, About)
- [x] 1.3 Highlight active tab (white bg, black text)
- [x] 1.4 Tab switching with Tab key, ; and . keys
- [x] 1.5 Placeholder content showing tab name
- [x] 1.6 Footer with navigation hints
- [ ] 1.7 Test on device and verify tab switching works

---

## Step 2: Display Tab ✅ COMPLETE

Implement brightness control.

- [x] 2.1 Create display tab content layout
- [x] 2.2 Show current brightness value
- [x] 2.3 Draw brightness slider bar
- [x] 2.4 Adjust brightness with , and / keys
- [x] 2.5 Quick presets (1=25%, 2=50%, 3=75%, 4=100%)
- [x] 2.6 Screen off with 0 key
- [x] 2.7 Save to NVS with S key
- [ ] 2.8 Test on device

---

## Step 3: Sound Tab ✅ COMPLETE

Implement volume control.

- [x] 3.1 Create sound tab content layout
- [x] 3.2 Show current volume value
- [x] 3.3 Draw volume slider bar
- [x] 3.4 Adjust volume with , and / keys
- [x] 3.5 Play feedback tone when adjusting
- [x] 3.6 Mute toggle with M key
- [x] 3.7 Test tone with T key
- [x] 3.8 Save to NVS with S key
- [ ] 3.9 Test on device

---

## Step 4: System Tab ✅ COMPLETE

Implement boot options and system info.

- [x] 4.1 Create system tab content layout
- [x] 4.2 Show boot mode option (cycle with Enter)
- [x] 4.3 Display free/total memory
- [x] 4.4 Display flash storage usage
- [x] 4.5 Reboot option with R key
- [x] 4.6 Save boot option to NVS
- [ ] 4.7 Test on device

---

## Step 5: About Tab ✅ COMPLETE

Display device information.

- [x] 5.1 Create about tab content layout
- [x] 5.2 Show device model
- [x] 5.3 Show chip info (ESP32-S3)
- [x] 5.4 Show MicroPython version
- [x] 5.5 Show MAC address
- [x] 5.6 Show uptime since boot
- [ ] 5.7 Test on device

---

## Step 6: WiFi Tab ✅ COMPLETE

Implement network scanning and connection.

- [x] 6.1 Create WiFi tab content layout
- [x] 6.2 WiFi enable/disable toggle
- [x] 6.3 Scan for networks with S key
- [x] 6.4 Display network list with signal bars
- [x] 6.5 Navigate list with ; and . keys
- [x] 6.6 Select network with Enter
- [x] 6.7 Password input for secured networks
- [x] 6.8 Show connection info when connected
- [x] 6.9 Disconnect option
- [ ] 6.10 Test on device

---

## Future Enhancements (Post-MVP)

- [ ] Hidden network entry
- [ ] Hostname configuration
- [ ] WiFi QR code sharing
- [ ] Clock/Timezone tab
