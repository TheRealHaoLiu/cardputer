# Cardputer ADV MicroPython Demos

Personal learning project for the M5Stack Cardputer ADV. I'm new to MicroPython and ESP32 development, so this repo contains experiments and demos as I learn.

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

### Run with local files mounted

```bash
uv run poe run
```

Mounts current directory to `/remote/` on device and runs `main.py`.

`main.py` adds both `/remote/apps` and `/flash/apps` to `sys.path`. When mounted, apps import from `/remote/apps` (your local files). Edit code locally, re-run to see changes immediately - no copying needed.

### Deploy to flash (standalone)

```bash
uv run poe deploy
```

Copies all files to device flash and resets. The device runs independently after this.

### Direct REPL access

```bash
uv run mpremote connect /dev/tty.usbmodem* repl
```

For interactive debugging. Exit with `Ctrl+]`.

### Other tasks

```bash
uv run poe --help       # List all available tasks
uv run poe ls           # List files on device
uv run poe reset        # Reset device
```

## Available Apps/Demos

| App | Description |
|-----|-------------|
| `hello_world` | App template - copy this to create new apps |
| `demo_text` | Text rendering demo |
| `demo_lcd` | LCD graphics demo |
| `demo_keyboard` | Keyboard input handling |
| `demo_widgets` | UIFlow widgets demo |
| `demo_anim` | Animation demo |
| `demo_sound` | Speaker/buzzer demo |
| `demo_nvs` | Non-volatile storage demo |
| `init_nvs` | Initialize NVS for uiflow launcher |
| `notepad` | Simple text editor |

## Creating New Apps

1. Copy `apps/hello_world.py` to `apps/my_app.py`
2. Rename the class to `MyApp`
3. Add to `APP_REGISTRY` in `main.py`:
   ```python
   ("my_app", "MyApp", "My App"),
   ```

See `apps/hello_world.py` for the required structure and keyboard handling patterns.

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues like:

- mpremote can't connect (launcher blocking)
- REPL modes (raw vs normal)
- Boot option values
- NVS initialization
