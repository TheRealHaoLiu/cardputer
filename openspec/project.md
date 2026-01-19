# Project Context

## Purpose

Cardputer ADV MicroPython Demos is a learning-focused project for the M5Stack Cardputer ADV embedded device. The project's core philosophy is that "the code IS the documentation" - every file contains extensive comments explaining not just what code does, but WHY, teaching MicroPython and embedded development concepts.

**Key Goals:**
- Teach MicroPython and embedded development through well-documented examples
- Build a reusable app framework for the M5Stack Cardputer ADV
- Demonstrate patterns like double buffering, keyboard handling, and lifecycle management
- Support both development (remote mounted files) and standalone deployment (on-device flash)

## Tech Stack

- **MicroPython** - Python implementation for embedded systems (ESP32-S3)
- **uiflow-micropython (UIFlow2)** - M5Stack's custom MicroPython firmware with pre-built hardware libraries (Lcd, Widgets, Speaker, etc.)
- **uv** - Fast Python package manager for development tooling
- **poethepoet (poe)** - Task runner for development workflows
- **ruff** - Python linter and formatter (0.8.0+)
- **mpremote** (1.24.0+) - MicroPython remote device access tool

**Hardware Target:**
- M5Stack Cardputer ADV (ESP32-S3 microcontroller)
- 240×135 LCD display (landscape orientation)
- 69-key keyboard with modifier keys (TCA8418 I2C controller at 0x34)
- Built-in speaker for audio

## Project Conventions

### Code Style

- **Line length:** 100 characters maximum
- **Formatter/Linter:** ruff with pycodestyle (E/W), pyflakes (F), isort (I), pyupgrade (UP), flake8-bugbear (B), flake8-simplify (SIM)
- **Documentation:** Extensive inline comments explaining "why" not just "what"
- **Fonts:** Use ASCII7 fonts for compact LCD text display

**Color Constants:**
```python
Lcd.COLOR.BLACK, WHITE, RED, GREEN, BLUE
Lcd.COLOR.YELLOW, MAGENTA, CYAN, ORANGE, PINK, PURPLE
```

### Architecture Patterns

**App-based Framework with Lifecycle Management:**

Apps inherit from `AppBase` and implement lifecycle methods:
1. `on_install()` - App registered with framework
2. `on_launch()` - App about to become active
3. `on_view()` - Draw UI (called on refresh)
4. `on_ready()` - Start async background tasks
5. `on_run()` - Async loop for animation, timers, etc.
6. `on_hide()` - App loses focus (cleanup)
7. `on_exit()` - Final cleanup
8. `on_uninstall()` - App removed from framework

**Main Loop Pattern:**
```python
while not exit_flag:
    M5.update()              # Required - process hardware events
    # Your logic here
    time.sleep(0.02)         # Prevent busy-waiting (50 FPS max)
```

**Double Buffering for Smooth Animation:**
```python
canvas = Lcd.newCanvas(240, 135)
canvas.fillScreen(Lcd.COLOR.BLACK)
canvas.fillRect(x, y, w, h, color)
canvas.push(0, 0)  # Atomic copy to screen
canvas.delete()    # Free memory - important on embedded!
```

**Keyboard Event Handling:**
```python
async def _kb_event_handler(self, event, fw):
    if event.key == ord('q'):
        event.status = True  # Mark as handled
    # ESC is handled by framework, don't consume it
```

### Testing Strategy

Manual testing on hardware device. Use development workflow with mounted files for rapid iteration:
- `uv run poe run` - Mount and run main.py
- `uv run poe run apps/hello_world.py` - Run specific app
- ESC key returns to launcher for hot-reload testing

### Git Workflow

- **Main branch:** `main`
- **Feature branches:** Descriptive names (e.g., `adopting-app-framework`)
- **Commit style:** Imperative mood, concise descriptions (e.g., "Add keyboard demo app and extract keycode utilities")

## Domain Context

**Project Structure:**
```
cardputer/
├── main.py           # Entry point - initializes hardware, creates framework
├── lib/              # Core framework code (reusable)
│   ├── framework.py  # Main event loop, app lifecycle management
│   ├── app_base.py   # Base classes (AppBase, AppSelector)
│   └── keycode.py    # Key code constants and utilities
├── apps/             # Runnable applications (auto-discovered)
│   ├── launcher.py   # Home screen menu
│   ├── hello_world.py# Minimal template/demo
│   ├── anim_demo.py  # Double buffering animation demo
│   └── keyboard_demo.py # Keyboard input handling demo
├── legacy_apps/      # Old app versions (pre-framework, reference only)
├── deploy.sh         # Flash deployment script
└── pyproject.toml    # Project config and dev dependencies
```

**Key Framework Concepts:**
- **10ms tick rate** = 100 updates/second for responsive input
- **Non-blocking keyboard polling** - Events queued, not blocking
- **Async/await support** for background tasks in apps
- **ESC key** always returns to launcher (except in standalone mode)
- **Hot-reload** via framework's `discover_apps()` in remote mount mode

**Development Modes:**
- **Remote mount:** Files served from computer, no upload needed, edit-run cycle
- **Standalone deploy:** Files copied to device flash, runs without computer

## Important Constraints

- **Memory limited:** ESP32-S3 has limited RAM; always `canvas.delete()` after use
- **MicroPython compatibility:** Some Python features unavailable; follow ruff ignore rules
- **Hardware-specific:** Code depends on M5Stack UIFlow2 firmware and Cardputer ADV hardware
- **Display size:** 240×135 pixels, landscape orientation
- **No pip:** Dependencies come from UIFlow2 firmware, not installable at runtime

## External Dependencies

**Firmware Requirements:**
- M5Stack UIFlow2 firmware (provides M5, Lcd, Widgets, Speaker modules)
- Pre-flashed on Cardputer ADV device

**Development Tools (installed via uv):**
- ruff ≥0.8.0
- poethepoet ≥0.25.0
- mpremote ≥1.24.0

**Hardware APIs (from UIFlow2):**
- `M5` - Core hardware initialization and update loop
- `Lcd` - Display drawing, canvas, colors
- `Widgets` - UI components (labels, etc.)
- `Speaker` - Audio output
- `MatrixKeyboard` - Cardputer ADV keyboard handling
