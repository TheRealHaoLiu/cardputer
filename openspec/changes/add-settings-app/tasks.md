# Implementation Tasks

## 0. Preparation

- [ ] 0.1 Remove `apps/brightness_demo.py` (replaced by Settings > Display)
- [ ] 0.2 Study UIFlow WiFi/network APIs in firmware source
- [ ] 0.3 Create base settings app structure with tab framework

## 1. Core Framework

### 1.1 Tab System
- [ ] 1.1.1 Create `SettingsApp` class inheriting from `AppBase`
- [ ] 1.1.2 Implement tab bar rendering with active tab highlight
- [ ] 1.1.3 Add Tab key cycling between tabs
- [ ] 1.1.4 Add Shift+Tab for reverse cycling
- [ ] 1.1.5 Create base `SettingsTab` class for tab content

### 1.2 UI Components
- [ ] 1.2.1 Implement slider component (brightness/volume bars)
- [ ] 1.2.2 Implement toggle switch component (ON/OFF)
- [ ] 1.2.3 Implement scrollable list component (network list)
- [ ] 1.2.4 Implement text input component with cursor
- [ ] 1.2.5 Implement signal strength bar drawing

## 2. WiFi Tab

### 2.1 Network Scanning
- [ ] 2.1.1 Implement WiFi scan trigger
- [ ] 2.1.2 Parse scan results (SSID, RSSI, security type)
- [ ] 2.1.3 Display network list with signal bars
- [ ] 2.1.4 Add scrolling for long network lists
- [ ] 2.1.5 Add "Scan" button/action

### 2.2 Network Connection
- [ ] 2.2.1 Network selection with Enter key
- [ ] 2.2.2 Password input dialog for secured networks
- [ ] 2.2.3 Connection attempt with status display
- [ ] 2.2.4 Connected indicator (checkmark) on active network
- [ ] 2.2.5 Error handling for failed connections

### 2.3 Hidden Network
- [ ] 2.3.1 "Add hidden network" option in list
- [ ] 2.3.2 SSID text input field
- [ ] 2.3.3 Password text input field
- [ ] 2.3.4 Connect to hidden network

### 2.4 WiFi Toggle & Info
- [ ] 2.4.1 WiFi enable/disable toggle
- [ ] 2.4.2 Display IP address when connected
- [ ] 2.4.3 Display MAC address
- [ ] 2.4.4 Display gateway and subnet
- [ ] 2.4.5 Display DNS server
- [ ] 2.4.6 Display RSSI with signal bars
- [ ] 2.4.7 Display channel number

### 2.5 Hostname
- [ ] 2.5.1 Display current hostname
- [ ] 2.5.2 Edit hostname with text input
- [ ] 2.5.3 Save hostname to NVS
- [ ] 2.5.4 Default to "cardputer" if not set

### 2.6 Saved Networks
- [ ] 2.6.1 Display currently saved SSID
- [ ] 2.6.2 "Forget network" option
- [ ] 2.6.3 Save new credentials to NVS

### 2.7 QR Code Sharing
- [ ] 2.7.1 Generate WiFi QR code for current network
- [ ] 2.7.2 Display QR code on screen
- [ ] 2.7.3 Return to normal view on keypress

## 3. Display Tab

### 3.1 Brightness Control
- [ ] 3.1.1 Display current brightness as slider bar
- [ ] 3.1.2 Adjust with ←/→ or +/- keys
- [ ] 3.1.3 Real-time brightness update as slider moves
- [ ] 3.1.4 Show percentage value

### 3.2 Presets & Actions
- [ ] 3.2.1 Quick preset keys (1=25%, 2=50%, 3=75%, 4=100%)
- [ ] 3.2.2 Screen off option (0 key)
- [ ] 3.2.3 Any key restores from screen off
- [ ] 3.2.4 Save to NVS option (S key)

## 4. Sound Tab

### 4.1 Volume Control
- [ ] 4.1.1 Display current volume as slider bar
- [ ] 4.1.2 Adjust with ←/→ or +/- keys
- [ ] 4.1.3 Play feedback tone when adjusting (440Hz, 50ms)
- [ ] 4.1.4 Show percentage value

### 4.2 Sound Actions
- [ ] 4.2.1 Mute toggle (M key)
- [ ] 4.2.2 Visual mute indicator
- [ ] 4.2.3 Test tone button (T key)
- [ ] 4.2.4 Save to NVS option (S key)

## 5. System Tab

### 5.1 Boot Option
- [ ] 5.1.1 Display current boot option
- [ ] 5.1.2 Cycle through options with Enter
- [ ] 5.1.3 Save to NVS immediately on change

### 5.2 System Info
- [ ] 5.2.1 Display free/total heap memory
- [ ] 5.2.2 Display flash storage usage
- [ ] 5.2.3 Refresh info on tab focus

### 5.3 System Actions
- [ ] 5.3.1 Reboot option with confirmation
- [ ] 5.3.2 Execute soft reset

## 6. About Tab

### 6.1 Device Information
- [ ] 6.1.1 Display device model name
- [ ] 6.1.2 Display chip info (ESP32-S3)
- [ ] 6.1.3 Display MicroPython version
- [ ] 6.1.4 Display UIFlow version (if available)
- [ ] 6.1.5 Display MAC address
- [ ] 6.1.6 Display uptime since boot

## 7. Polish & Testing

- [ ] 7.1 Double-buffered rendering for smooth updates
- [ ] 7.2 Consistent color scheme across all tabs
- [ ] 7.3 Error handling for all operations
- [ ] 7.4 Memory cleanup on tab switch
- [ ] 7.5 Test all keyboard navigation paths
- [ ] 7.6 Test NVS persistence across reboots
