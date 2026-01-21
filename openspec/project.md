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
- **Custom MicroPython firmware** - Based on M5Stack's UIFlow2, built from https://github.com/TheRealHaoLiu/cardputer-adv-micropython (branch: `custom-firmware`)
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

### Development Principles

**Incremental Implementation:**
- For complex features, break tasks into small, testable steps
- Implement and test one piece at a time before moving to the next
- Each step should be independently verifiable on hardware
- Prefer working code that can be extended over comprehensive plans that haven't been tested

**Learning-Focused Code:**
- This is a learning project - code IS documentation
- Add comments explaining "why" not just "what"
- Comment non-obvious logic, hardware quirks, and design decisions
- Include console logging with `print()` for debugging and understanding flow
- Use descriptive variable names that teach concepts

**UI/UX Design:**
- Prefer button/menu-based navigation over complex keyboard shortcuts
- Use consistent navigation patterns across apps (Tab, ;/., Enter, ESC)
- Show available actions in footer hints
- Keep UI simple - the 240x135 screen has limited space

## Domain Context

**Project Structure:**
```
cardputer/
├── main.py           # Entry point - initializes hardware, creates framework
├── boot.py           # Hardware init and WiFi connection at boot
├── lib/              # Core framework code (MicroPython standard path)
│   ├── framework.py  # Main event loop, app lifecycle, lazy loading
│   ├── app_base.py   # Base classes (AppBase, AppSelector)
│   └── keycode.py    # Key code constants and utilities
├── apps/             # Runnable applications (hierarchical menu)
│   ├── manifest.json # Top-level app registry {"module": "Display Name"}
│   ├── launcher.py   # Home screen menu (not in manifest)
│   ├── hello_world.py# Minimal template/demo
│   ├── settings_app.py # Settings application
│   └── demo/         # Demo apps submenu
│       ├── manifest.json # Demo app registry
│       ├── sound_demo.py
│       ├── anim_demo.py
│       └── ...
├── legacy/           # Pre-framework code (reference only)
│   ├── main.py       # Original monolithic entry point
│   └── apps/         # Original app implementations
├── deploy.sh         # Flash deployment script
└── pyproject.toml    # Project config and dev dependencies
```

**Legacy Code:**
The `legacy/` directory contains the original implementation before the app framework refactor. It's preserved for reference but not actively maintained. The legacy approach had a monolithic main.py with manual app registry, no lifecycle management, and tight coupling. Run with `poe run legacy/main.py` if needed.

**Key Framework Concepts:**
- **10ms tick rate** = 100 updates/second for responsive input
- **Non-blocking keyboard polling** - Events queued, not blocking
- **Async/await support** for background tasks in apps
- **ESC key** always returns to launcher (except in standalone mode)
- **Lazy loading** - Apps imported only when selected, not on every ESC
- **Hot-reload** via 'r' key in launcher (dev mode only) - rescans manifests and clears cache

**Development Modes:**
- **Remote mount:** Files served from computer, no upload needed, edit-run cycle
- **Standalone deploy:** Files copied to device flash, runs without computer

## Important Constraints

- **Memory limited:** ESP32-S3 has limited RAM; always `canvas.delete()` after use
- **MicroPython compatibility:** Some Python features unavailable; follow ruff ignore rules
- **Hardware-specific:** Code depends on custom firmware (based on UIFlow2) and Cardputer ADV hardware
- **Display size:** 240×135 pixels, landscape orientation
- **No pip:** Dependencies come from UIFlow2 firmware, not installable at runtime

## External Dependencies

**Firmware Requirements:**
- Custom firmware from https://github.com/TheRealHaoLiu/cardputer-adv-micropython (branch: `custom-firmware`)
- Local convention: clone at `../cardputer-adv-micropython` relative to this repo
- Based on UIFlow2, provides M5, Lcd, Widgets, Speaker, and many more modules
- See `MODULES.md` in the firmware repo for full module reference

**Development Tools (installed via uv):**
- ruff ≥0.8.0
- poethepoet ≥0.25.0
- mpremote ≥1.24.0

**Hardware APIs:**
See `MODULES.md` from the firmware release (`uv run poe firmware-download`) for the full list of available modules including M5, Lcd, Widgets, Speaker, hardware drivers, sensors, networking, and unit classes.
