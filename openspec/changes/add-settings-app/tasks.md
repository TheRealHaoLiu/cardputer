# Implementation Tasks

## Revised Approach

Implementing incrementally, one small step at a time. Each step should be tested before moving to the next.

---

## Step 1: Tab Framework ✅ IN PROGRESS

Create basic tab structure with blank content.

- [x] 1.1 Create minimal `SettingsApp` class with AppBase
- [x] 1.2 Draw tab bar with 5 tabs (WiFi, Display, Sound, System, About)
- [x] 1.3 Highlight active tab (white bg, black text)
- [x] 1.4 Tab switching with Tab key, ; and . keys
- [x] 1.5 Placeholder content showing tab name
- [x] 1.6 Footer with navigation hints
- [ ] 1.7 Test on device and verify tab switching works

---

## Step 2: Display Tab

Implement brightness control.

- [ ] 2.1 Create display tab content layout
- [ ] 2.2 Show current brightness value
- [ ] 2.3 Draw brightness slider bar
- [ ] 2.4 Adjust brightness with , and / keys
- [ ] 2.5 Quick presets (1=25%, 2=50%, 3=75%, 4=100%)
- [ ] 2.6 Screen off with 0 key
- [ ] 2.7 Save to NVS with S key
- [ ] 2.8 Test on device

---

## Step 3: Sound Tab

Implement volume control.

- [ ] 3.1 Create sound tab content layout
- [ ] 3.2 Show current volume value
- [ ] 3.3 Draw volume slider bar
- [ ] 3.4 Adjust volume with , and / keys
- [ ] 3.5 Play feedback tone when adjusting
- [ ] 3.6 Mute toggle with M key
- [ ] 3.7 Test tone with T key
- [ ] 3.8 Save to NVS with S key
- [ ] 3.9 Test on device

---

## Step 4: System Tab

Implement boot options and system info.

- [ ] 4.1 Create system tab content layout
- [ ] 4.2 Show boot mode option (cycle with Enter)
- [ ] 4.3 Display free/total memory
- [ ] 4.4 Display flash storage usage
- [ ] 4.5 Reboot option with R key
- [ ] 4.6 Save boot option to NVS
- [ ] 4.7 Test on device

---

## Step 5: About Tab

Display device information.

- [ ] 5.1 Create about tab content layout
- [ ] 5.2 Show device model
- [ ] 5.3 Show chip info (ESP32-S3)
- [ ] 5.4 Show MicroPython version
- [ ] 5.5 Show MAC address
- [ ] 5.6 Show uptime since boot
- [ ] 5.7 Test on device

---

## Step 6: WiFi Tab

Implement network scanning and connection.

- [ ] 6.1 Create WiFi tab content layout
- [ ] 6.2 WiFi enable/disable toggle
- [ ] 6.3 Scan for networks with S key
- [ ] 6.4 Display network list with signal bars
- [ ] 6.5 Navigate list with ; and . keys
- [ ] 6.6 Select network with Enter
- [ ] 6.7 Password input for secured networks
- [ ] 6.8 Show connection info when connected
- [ ] 6.9 Disconnect option
- [ ] 6.10 Test on device

---

## Future Enhancements (Post-MVP)

- [ ] Hidden network entry
- [ ] Hostname configuration
- [ ] WiFi QR code sharing
- [ ] Clock/Timezone tab
