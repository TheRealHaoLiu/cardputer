# Cardputer ADV MicroPython Demos

A **learning-focused** project for the M5Stack Cardputer ADV. Every file is heavily commented to teach MicroPython and embedded development concepts.

## Learning Approach

**The code IS the documentation.** Each file contains extensive comments explaining:
- What each section does and WHY
- Common patterns and best practices
- API references and quick lookups
- Gotchas and important notes

Start with `apps/hello_world.py` - it's the template with the most detailed explanations.

## Hardware

[M5Stack Cardputer ADV](https://shop.m5stack.com/products/m5stack-cardputer-adv-version-esp32-s3) - ESP32-S3 with built-in 240x135 LCD and keyboard.

## Firmware

Uses [uiflow-micropython](https://github.com/m5stack/uiflow-micropython) (UIFlow2) instead of vanilla MicroPython.

**Why UIFlow2?**
- Includes M5Stack hardware libraries (Lcd, Widgets, Speaker, etc.) pre-built
- Hardware abstraction already done for Cardputer ADV's display, keyboard, speaker
- No need to find/port drivers for the specific hardware

**Source code**: https://github.com/m5stack/uiflow-micropython

## Initial Setup

### 1. Install m5launcher

Install [m5launcher](https://github.com/bmorcelli/M5Cardputer-Launcher) to make firmware management easier.

### 2. Install uiflow2 firmware

Use m5launcher to install uiflow2 for **Cardputer ADV** (NOT regular Cardputer - they have different hardware).

### 3. Set boot mode

The uiflow firmware has a built-in launcher that can interfere with mpremote. Set boot mode to run main.py directly:

```bash
uv run poe set-boot-mode      # 0 = run main.py (default)
uv run poe set-boot-mode 1    # 1 = show built-in launcher
uv run poe set-boot-mode 2    # 2 = network setup only
```

For development with mpremote, use mode 0.

### 4. USB Connection Note

If mpremote can't connect, try: turn off the device, then plug in USB to power it on. Not sure why this helps, but it does.

## Development Workflow

### Running Apps

**Run the launcher (menu to select apps):**
```bash
uv run poe run
```

**Run a specific app directly (skip the menu):**
```bash
uv run poe run apps/hello_world.py
uv run poe run apps/demo_anim.py
uv run poe run apps/notepad.py
# etc.
```

Each app has standalone support via `if __name__ == "__main__"` block, so you can test individual apps without going through the launcher menu.

### How It Works

`poe run` mounts your local directory to `/remote/` on the device and executes the file. **All files are loaded from your local machine** - including `lib/` (framework, app_base) and `apps/`. Your local edits are immediately available - no copying needed!

- `poe run` (no args) → runs `main.py` → shows launcher menu
- `poe run apps/foo.py` → runs that app directly with hardware init

**Hot-reloading**: In remote mode, returning to the launcher (ESC) reloads app modules, so your code changes take effect without restarting.

Press **ESC** to exit any app and return to the launcher (or REPL if running standalone).

### Deploy to Flash (Standalone)

```bash
uv run poe deploy
```

Copies all files to device flash. The device runs independently after this - no computer needed.

**WARNING**: Deploy replaces **all** of the following on the device:
- `/flash/main.py`
- `/flash/lib/*` (framework.py, app_base.py, etc.)
- `/flash/apps/*` (all app files)

Any changes made directly on the device will be lost!

### Direct REPL Access

```bash
uv run mpremote connect /dev/tty.usbmodem* repl
```

For interactive debugging. Exit with `Ctrl+]`.

### All Available Tasks

```bash
uv run poe --help           # List all tasks
uv run poe run [file]       # Run file (default: main.py)
uv run poe deploy           # Copy files to flash
uv run poe ls [path]        # List files on device
uv run poe cat <path>       # Show file contents from device
uv run poe reset            # Reset device
uv run poe set-boot-mode N  # Set boot mode (0/1/2)
uv run poe lint             # Check code for errors
uv run poe format           # Format code with ruff
```

## Available Apps/Demos

Each demo teaches specific concepts. Run them with `uv run poe run apps/<name>.py`.

| App | Concepts Taught |
|-----|-----------------|
| `hello_world` | **START HERE** - App structure, keyboard callbacks, main loop pattern |
| `notepad` | Text editing, cursor management, incremental screen updates |
| `demo_anim` | **Double buffering** - The key to smooth animation (canvas vs direct draw) |
| `demo_text` | Fonts, colors (Lcd.COLOR.*), text alignment, scrolling marquee |
| `demo_lcd` | Shape drawing, brightness control, QR codes, display info |
| `demo_keyboard` | Key events, modifier detection, FN combinations, matrix layout |
| `demo_sound` | Tones, musical notes, volume control, sound effects |
| `demo_widgets` | High-level UI components (Label), text alignment, UI patterns |
| `demo_nvs` | Persistent storage, saving settings, understanding boot options |

## Creating New Apps

1. Copy `apps/hello_world.py` to `apps/my_app.py`
2. Rename the class to `MyApp` (must inherit from `AppBase`)
3. Set `self.name = "My App"` in `__init__`
4. Update the `if __name__ == "__main__"` block to use `MyApp`

**That's it!** Apps are auto-discovered from the `apps/` directory. No need to register them anywhere - just create the file and it appears in the launcher.

See `apps/hello_world.py` for the required structure and keyboard handling patterns.

## Key Concepts Quick Reference

### The Main Loop Pattern
Every app needs this structure:
```python
while not exit_flag:
    M5.update()      # REQUIRED - processes hardware events
    # Your logic here
    time.sleep(0.02) # Prevent busy-waiting
```

### Keyboard Callback Pattern
Never do slow operations in callbacks! Use flags:
```python
exit_flag = False

def on_key(keyboard):
    nonlocal exit_flag
    while keyboard._keyevents:
        event = keyboard._keyevents.pop(0)
        if event.keycode == 0x1B:  # ESC
            exit_flag = True  # Just set flag, don't do heavy work

kb.set_keyevent_callback(on_key)
```

### Double Buffering (Smooth Animation)
```python
canvas = Lcd.newCanvas(240, 135)  # Create off-screen buffer
canvas.fillScreen(Lcd.COLOR.BLACK)  # Draw to canvas (invisible)
canvas.fillRect(x, y, w, h, color)
canvas.push(0, 0)                   # Copy to screen (atomic, no flicker!)
canvas.delete()                     # Free memory when done
```

### Color Constants (Lcd.COLOR.*)
Use built-in color constants for cleaner code:
```python
Lcd.COLOR.BLACK, Lcd.COLOR.WHITE
Lcd.COLOR.RED, Lcd.COLOR.GREEN, Lcd.COLOR.BLUE
Lcd.COLOR.YELLOW, Lcd.COLOR.MAGENTA, Lcd.COLOR.CYAN
Lcd.COLOR.ORANGE, Lcd.COLOR.PINK, Lcd.COLOR.PURPLE
```

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues like:

- mpremote can't connect (launcher blocking)
- REPL modes (raw vs normal)
- Boot option values
- NVS initialization
