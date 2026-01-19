# Change: Add Demo Apps Roadmap

## Why

The Cardputer project aims to teach MicroPython and embedded development through well-documented examples. Currently we have 4 demo apps (launcher, hello_world, anim_demo, keyboard_demo) but the M5Stack hardware offers many more capabilities that should be demonstrated. A structured roadmap ensures systematic coverage of hardware features with increasing complexity.

## What Changes

- Add Phase 1: Core Hardware demos (audio, display shapes, storage)
- Add Phase 2: System & Network demos (WiFi, system info, file browser)
- Add Phase 3: Interactive demos (games, synthesizer)
- Add Phase 4: Advanced demos (sensors, data visualization)

## Impact

- Affected specs: demo-apps (new capability)
- Affected code: `apps/` directory - will add 10-15 new demo applications

## Roadmap Overview

### Phase 1: Core Hardware Features
Foundation demos that showcase built-in Cardputer hardware.

| Demo | Description | Hardware | Priority |
|------|-------------|----------|----------|
| `sound_demo.py` | Tone generator, WAV playback, volume control | Speaker | High |
| `shapes_demo.py` | Draw lines, circles, triangles, arcs, filled shapes | LCD | High |
| `qrcode_demo.py` | Generate and display QR codes | LCD | Medium |
| `storage_demo.py` | NVS key-value persistence, save/load settings | Flash NVS | Medium |
| `brightness_demo.py` | Adjust display brightness with keyboard | LCD | Low |

### Phase 2: System & Network
Demos that show system capabilities and connectivity.

| Demo | Description | Hardware | Priority |
|------|-------------|----------|----------|
| `sysinfo_demo.py` | Memory usage, chip info, flash stats | ESP32-S3 | High |
| `wifi_scanner.py` | Scan and display nearby WiFi networks | WiFi | High |
| `file_browser.py` | Navigate flash filesystem, view files | Flash FS | Medium |
| `http_demo.py` | Simple HTTP GET request demo | WiFi | Medium |

### Phase 3: Interactive Applications
Engaging demos that combine multiple features.

| Demo | Description | Hardware | Priority |
|------|-------------|----------|----------|
| `snake_game.py` | Classic Snake game with keyboard controls | LCD + KB | High |
| `piano_demo.py` | Musical keyboard - play notes with keys | Speaker + KB | Medium |
| `breakout_game.py` | Breakout/brick breaker game | LCD + KB | Medium |
| `stopwatch.py` | Timer with lap functionality | LCD + KB | Low |

### Phase 4: Advanced Features
Demos for advanced capabilities (may require additional hardware).

| Demo | Description | Hardware | Priority |
|------|-------------|----------|----------|
| `mic_demo.py` | Audio recording and playback | Microphone | Medium |
| `chart_demo.py` | Real-time data visualization (graphs) | LCD | Medium |
| `settings_app.py` | Persistent settings manager (brightness, volume) | NVS + LCD | Low |

## Implementation Guidelines

1. **Each demo should be self-contained** - Single file in `apps/` directory
2. **Follow AppBase lifecycle** - Inherit from AppBase, implement required methods
3. **Extensive comments** - "Code IS documentation" philosophy
4. **Handle ESC properly** - Return to launcher on ESC
5. **Memory management** - Always delete canvases, clean up resources
6. **Keyboard-first design** - All demos controllable via keyboard

## Success Criteria

- [ ] All Phase 1 demos completed and tested
- [ ] All Phase 2 demos completed and tested
- [ ] At least 2 Phase 3 demos completed
- [ ] Demo code quality matches existing apps (comments, patterns)
