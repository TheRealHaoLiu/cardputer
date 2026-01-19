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

### Phase 1: Core Hardware Features ✅ COMPLETE
Foundation demos that showcase built-in Cardputer hardware.

| Demo | Description | Hardware | Status |
|------|-------------|----------|--------|
| `sound_demo.py` | Tone generator, WAV playback, volume control | Speaker | ✅ Done |
| `shapes_demo.py` | Draw lines, circles, triangles, arcs, filled shapes | LCD | ✅ Done |
| `qrcode_demo.py` | Generate and display QR codes | LCD | ✅ Done |
| `storage_demo.py` | NVS key-value persistence, save/load settings | Flash NVS | ✅ Done |
| `brightness_demo.py` | Adjust display brightness with keyboard | LCD | ⚠️ **SUPERSEDED** |

> **Note:** `brightness_demo.py` will be removed by `add-settings-app` proposal.
> Brightness control is moving to the Settings App > Display tab.

### Phase 2: System & Network ⚠️ REDESIGNED
> **Note:** This phase has been redesigned. See `add-settings-app` proposal for the new plan.
>
> WiFi configuration, system info, and brightness control are now part of a comprehensive
> **Settings App** with a tabbed interface. The file browser and HTTP demo remain as
> standalone demos.

**Original plan (deprecated):**

| Demo | Description | Status |
|------|-------------|--------|
| `sysinfo_demo.py` | Memory usage, chip info, flash stats | → Moved to Settings > System/About |
| `wifi_scanner.py` | Scan and display nearby WiFi networks | → Moved to Settings > WiFi |
| `file_browser.py` | Navigate flash filesystem, view files | 📋 Still planned |
| `http_demo.py` | Simple HTTP GET request demo | 📋 Still planned |

**New plan:** See `openspec/changes/add-settings-app/proposal.md`

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
