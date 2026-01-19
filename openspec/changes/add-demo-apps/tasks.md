# Implementation Tasks

## Phase 1: Core Hardware Features ✅ COMPLETE

### 1.1 Sound Demo
- [x] 1.1.1 Create `apps/sound_demo.py` with AppBase structure
- [x] 1.1.2 Implement tone generation with configurable frequency
- [x] 1.1.3 Add WAV file playback (if available) - API documented, scale/effects demos added
- [x] 1.1.4 Add volume control with keyboard
- [x] 1.1.5 Add visual feedback on screen

### 1.2 Shapes Demo
- [x] 1.2.1 Create `apps/shapes_demo.py` with AppBase structure
- [x] 1.2.2 Implement drawing primitives (line, circle, rect, triangle)
- [x] 1.2.3 Add arc and filled shape variations
- [x] 1.2.4 Add keyboard navigation to cycle through shapes
- [x] 1.2.5 Add color selection

### 1.3 QR Code Demo
- [x] 1.3.1 Create `apps/qrcode_demo.py` with AppBase structure
- [x] 1.3.2 Implement QR code generation with sample URLs
- [x] 1.3.3 Add keyboard to cycle through different QR codes
- [x] 1.3.4 Display QR content as text below code

### 1.4 Storage Demo
- [x] 1.4.1 Create `apps/storage_demo.py` with AppBase structure
- [x] 1.4.2 Implement NVS read/write operations
- [x] 1.4.3 Add counter that persists across reboots
- [x] 1.4.4 Show stored values on screen

### 1.5 Brightness Demo ⚠️ SUPERSEDED
- [x] 1.5.1 Create `apps/brightness_demo.py` with AppBase structure
- [x] 1.5.2 Implement brightness adjustment with up/down keys
- [x] 1.5.3 Display current brightness level
- [ ] 1.5.4 **PENDING REMOVAL** - Will be deleted by `add-settings-app` proposal

> **Note:** Brightness control is moving to Settings App > Display tab.
> The `brightness_demo.py` file will be removed when `add-settings-app` is implemented.

## Phase 2: System & Network ⚠️ REDESIGNED

> **This phase has been superseded by `add-settings-app` proposal.**
>
> - System info → Settings App > System/About tabs
> - WiFi scanner → Settings App > WiFi tab
> - File browser → Still planned as standalone demo
> - HTTP demo → Still planned as standalone demo
>
> See `openspec/changes/add-settings-app/` for the new implementation plan.

### 2.1 System Info Demo → MOVED TO SETTINGS APP
- [~] ~~2.1.1 Create `apps/sysinfo_demo.py`~~ → Settings > System/About tabs
- [~] ~~2.1.2-2.1.5~~ → See `add-settings-app/tasks.md`

### 2.2 WiFi Scanner → MOVED TO SETTINGS APP
- [~] ~~2.2.1 Create `apps/wifi_scanner.py`~~ → Settings > WiFi tab
- [~] ~~2.2.2-2.2.5~~ → See `add-settings-app/tasks.md`

### 2.3 File Browser (Still Planned)
- [ ] 2.3.1 Create `apps/file_browser.py` with AppBase structure
- [ ] 2.3.2 List files in flash filesystem
- [ ] 2.3.3 Navigate directories with keyboard
- [ ] 2.3.4 Display file sizes
- [ ] 2.3.5 Preview text file contents

### 2.4 HTTP Demo (Still Planned)
- [ ] 2.4.1 Create `apps/http_demo.py` with AppBase structure
- [ ] 2.4.2 Connect to WiFi (use credentials from Settings App)
- [ ] 2.4.3 Make simple HTTP GET request
- [ ] 2.4.4 Display response on screen

## Phase 3: Interactive Applications

### 3.1 Snake Game
- [ ] 3.1.1 Create `apps/snake_game.py` with AppBase structure
- [ ] 3.1.2 Implement game board and snake rendering
- [ ] 3.1.3 Add keyboard controls (WASD or arrows)
- [ ] 3.1.4 Implement food spawning and collision
- [ ] 3.1.5 Add score display and game over handling

### 3.2 Piano Demo
- [ ] 3.2.1 Create `apps/piano_demo.py` with AppBase structure
- [ ] 3.2.2 Map keyboard keys to musical notes
- [ ] 3.2.3 Play tones on keypress
- [ ] 3.2.4 Visual feedback showing which note is playing
- [ ] 3.2.5 Add octave shifting with modifier keys

### 3.3 Breakout Game
- [ ] 3.3.1 Create `apps/breakout_demo.py` with AppBase structure
- [ ] 3.3.2 Implement paddle, ball, and brick rendering
- [ ] 3.3.3 Add keyboard controls for paddle
- [ ] 3.3.4 Implement ball physics and collision
- [ ] 3.3.5 Add score and lives display

### 3.4 Stopwatch
- [ ] 3.4.1 Create `apps/stopwatch.py` with AppBase structure
- [ ] 3.4.2 Implement start/stop/reset controls
- [ ] 3.4.3 Add lap time recording
- [ ] 3.4.4 Display elapsed time with milliseconds

## Phase 4: Advanced Features

### 4.1 Microphone Demo
- [ ] 4.1.1 Create `apps/mic_demo.py` with AppBase structure
- [ ] 4.1.2 Implement audio recording
- [ ] 4.1.3 Visualize audio levels in real-time
- [ ] 4.1.4 Implement playback of recorded audio

### 4.2 Chart Demo
- [ ] 4.2.1 Create `apps/chart_demo.py` with AppBase structure
- [ ] 4.2.2 Implement line chart rendering
- [ ] 4.2.3 Add real-time data updates (random or sensor)
- [ ] 4.2.4 Add bar chart option

### ~~4.3 Settings App~~ → MOVED TO SEPARATE PROPOSAL
> Settings App is now a standalone proposal: `add-settings-app`
> See `openspec/changes/add-settings-app/` for full implementation plan.
