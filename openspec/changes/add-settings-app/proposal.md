# Change: Add Comprehensive Settings App

## Why

The Cardputer needs a unified settings interface for configuring device options. Currently, settings like brightness require standalone demo apps, and WiFi configuration requires external tools or the UIFlow launcher. A tabbed Settings App provides a polished, integrated experience for managing all device settings.

## What Changes

- Add `apps/settings_app.py` - Full-featured tabbed settings application
- Remove `apps/brightness_demo.py` - Functionality moved to Settings > Display tab
- Update Phase 2 roadmap - Settings App replaces individual wifi/brightness demos

## Impact

- Affected specs: settings-app (new capability)
- Affected code: `apps/` directory
- Removes: `apps/brightness_demo.py`

---

## Settings App Design

### Tab Structure

```
┌─────────────────────────────────────────┐
│ ⚙ Settings                              │
├────┬────────┬────────┬────────┬─────────┤
│WiFi│Display │ Sound  │ System │ About   │
└────┴────────┴────────┴────────┴─────────┘
```

### Tab 1: WiFi 📶

**Features:**
| Feature | Description | NVS Key |
|---------|-------------|---------|
| WiFi Toggle | Enable/disable radio | - |
| Network Scanner | List available networks with signal bars | - |
| Network Selection | Select and connect with password prompt | - |
| Hidden SSID Entry | Manual SSID/password for hidden networks | - |
| Connection Info | IP, MAC, Gateway, Subnet, DNS, RSSI, Channel | - |
| Hostname | Device network name (default: "cardputer") | `hostname` |
| Saved Networks | View/forget stored credentials | `ssid0`, `pswd0` |
| QR Share | Generate QR code of current network credentials | - |

**Network List UI:**
```
┌───────────────────────────────────┐
│ ████░ HomeNetwork      WPA2   ✓  │  <- Connected indicator
│ ███░░ Neighbor_5G      WPA2      │  <- Signal bars + security
│ ██░░░ CoffeeShop       Open      │
│ █░░░░ WeakSignal       WPA3      │
│ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄  │
│ + Add hidden network...          │  <- Manual entry option
└───────────────────────────────────┘
```

**Signal Strength Bars:**
- 4 bars: Excellent (RSSI > -50 dBm)
- 3 bars: Good (RSSI > -60 dBm)
- 2 bars: Fair (RSSI > -70 dBm)
- 1 bar: Weak (RSSI <= -70 dBm)

**Connection Info Display:**
```
IP: 192.168.1.42    Gateway: 192.168.1.1
MAC: AA:BB:CC:DD:EE:FF
Subnet: 255.255.255.0   DNS: 8.8.8.8
RSSI: -45 dBm (████░)   Channel: 6
Hostname: cardputer
```

### Tab 2: Display 🔆

**Features:**
| Feature | Description | NVS Key |
|---------|-------------|---------|
| Brightness Slider | Visual bar 0-255 with percentage | `brightness` |
| Quick Presets | 25%, 50%, 75%, 100% one-key access | - |
| Screen Off | Turn off display (any key restores) | - |
| Save Setting | Persist to NVS | `brightness` |

**UI Concept:**
```
Brightness
┌────────────────────────────────┐
│ ████████████████░░░░░░░░  65% │
└────────────────────────────────┘
Presets: [1]25%  [2]50%  [3]75%  [4]100%

[S] Save to device    [0] Screen off
```

### Tab 3: Sound 🔊

**Features:**
| Feature | Description | NVS Key |
|---------|-------------|---------|
| Volume Slider | Visual bar 0-255 with percentage | `volume` |
| Mute Toggle | Quick mute/unmute | - |
| Test Tone | Play 440Hz test beep | - |
| Feedback Tone | Play tone when adjusting volume | - |
| Save Setting | Persist to NVS | `volume` |

**UI Concept:**
```
Volume                          [🔊 ON]
┌────────────────────────────────┐
│ ██████████████░░░░░░░░░░  55% │
└────────────────────────────────┘
[M] Mute   [T] Test   [S] Save
```

### Tab 4: System ⚡

**Features:**
| Feature | Description | NVS Key |
|---------|-------------|---------|
| Boot Option | 0=main.py, 1=Launcher, 2=Setup | `boot_option` |
| Memory Info | Free/used heap RAM | - |
| Storage Info | Flash filesystem usage | - |
| Reboot | Soft restart device | - |

**UI Concept:**
```
Boot Mode: [Launcher ▼]  (Enter to cycle)

Memory:   45,232 / 102,400 bytes free
Storage:  1.2 MB / 4.0 MB used

[R] Reboot device
```

### Tab 5: About ℹ️

**Features:**
| Feature | Description |
|---------|-------------|
| Device Model | M5Stack Cardputer |
| Chip | ESP32-S3 |
| MicroPython | Version string |
| UIFlow | Firmware version |
| MAC Address | WiFi MAC |
| Uptime | Time since boot |

**UI Concept:**
```
Device:      M5Stack Cardputer
Chip:        ESP32-S3 @ 240MHz
MicroPython: 1.20.0
UIFlow:      2.0.0
MAC:         AA:BB:CC:DD:EE:FF
Uptime:      2h 34m 12s
```

---

## Keyboard Controls

| Key | Action |
|-----|--------|
| **Tab** | Cycle to next tab |
| **Shift+Tab** | Cycle to previous tab |
| **↑/↓** | Navigate within tab content |
| **←/→** | Adjust sliders / Select options |
| **Enter** | Confirm / Toggle / Edit field |
| **Backspace** | Delete character in text input |
| **ESC** | Exit settings / Cancel current operation |
| **0-9** | Quick actions (presets, etc.) |
| **Typing** | Direct text input in edit mode |

---

## Visual Design Principles

1. **Signal Bars** - Custom-drawn using fillRect for WiFi strength
2. **Toggle Switches** - Visual ON/OFF indicators with color
3. **Sliders** - Filled bar with percentage text
4. **Tab Highlighting** - Active tab visually distinct (inverted colors or underline)
5. **Status Colors**:
   - Green: Connected / Enabled / Success
   - Yellow: Connecting / Warning
   - Red: Error / Disabled
   - Cyan: Information / Labels
6. **Double Buffering** - Smooth updates without flicker

---

## Future Enhancements (Post-Phase 2)

- **Clock/Timezone Tab** - NTP sync, timezone selection, RTC display
- **Theme Tab** - Custom color schemes
- **Advanced WiFi** - Static IP configuration, DNS override
- **Power Tab** - Battery info, power saving modes
