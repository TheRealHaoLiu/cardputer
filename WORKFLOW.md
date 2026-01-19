# Claude Code + Cardputer Development Workflow

A guide to setting up a fast iteration loop for developing MicroPython apps on M5Stack Cardputer ADV with Claude Code as your AI pair programmer.

## The Problem

When developing on embedded devices, the typical workflow is slow:
1. Write code
2. Upload to device
3. Run manually
4. Copy/paste errors back to your AI assistant
5. Repeat

This friction makes iteration painful.

## The Solution

Create a feedback loop where Claude Code can:
1. Write files directly to a mounted directory
2. See device output via a log file
3. Iterate without manual copy/paste

## Setup

### 1. Create a Python environment

```bash
pyenv virtualenv cardputer
pyenv activate cardputer
pip install mpremote
```

### 2. Start mpremote with logging

In one terminal, connect and mount your project directory with output logging:

```bash
mpremote connect /dev/tty.usbmodem2101 mount ~/projects/cardputer + repl 2>&1 | tee /tmp/mpremote.log
```

This does three things:
- Connects to the device
- Mounts your local directory to `/remote/` on the device
- Logs all output to `/tmp/mpremote.log` (which Claude Code can read)

### 3. Set up the reload function

In the MicroPython REPL, define a quick reload function:

```python
def r(): exec(open('/remote/main.py').read(), globals())
```

Now you just type `r()` to reload and run your code.

### 4. Tell Claude Code about the log file

Claude Code can now:
- Write/edit files in your project directory
- Read `/tmp/mpremote.log` to see output and errors
- Iterate without you copy/pasting anything

## The Workflow

1. Describe what you want to build
2. Claude Code writes the code
3. You type `r()` in the REPL
4. Claude Code reads the log to see results/errors
5. Claude Code fixes issues and iterates
6. Repeat until it works

## Key Insights

### Why not let Claude Code run mpremote directly?

You might think: "Why not just have Claude run `mpremote run main.py` directly?"

The problem: mpremote's REPL mode is blocking and interactive. When Claude Code tries to run it:
- The terminal locks up waiting for input
- Claude can't Ctrl+C out of it reliably
- The process hangs indefinitely

The split-terminal approach solves this:
- **Your terminal**: Runs mpremote interactively (you control it)
- **Claude's access**: Read-only via log file + write access to source files

This separation of concerns works better than trying to have Claude drive the serial connection directly.

### Why mpremote mount?

The `mount` command makes your local files appear at `/remote/` on the device. No uploading needed - edit locally, run remotely.

### Why tee to a log file?

Claude Code can't see your terminal, but it CAN read files. By teeing output to a log file, Claude gets visibility into what's happening on the device.

### Why the r() function?

Typing `exec(open('/remote/main.py').read(), globals())` every time is tedious. The `r()` shortcut makes iteration instant.

### Why globals()?

Using `globals()` in exec means top-level variables persist between reloads, useful for debugging and maintaining state during development.

## Hardware Notes

### M5Stack Cardputer ADV

- Uses I2C keyboard (TCA8418 controller at address 0x34)
- I2C pins: SCL=9, SDA=8, INT=11
- Screen: 240x135 landscape
- Make sure you flash the correct ADV firmware (not regular Cardputer)

### Board Detection

```python
import M5
board_id = M5.getBoard()
# M5Cardputer = 14 (GPIO matrix keyboard)
# M5CardputerADV = 24 (I2C keyboard)
```

## Example Session

```
You: "Let's build a notepad app for the Cardputer"

Claude: *writes main.py*

You: r()
     # see "Notepad Ready" on screen, type some keys

Claude: *reads /tmp/mpremote.log*
        "I see key events working. Let me add backspace support..."
        *edits main.py*

You: r()
     # test backspace

Claude: *reads log*
        "Working. Now let me add multi-line support..."
```

## Troubleshooting

### "command not found: mpremote"
Install it: `pip install mpremote`

### No output in log file
The serial port can only be used by one process. Kill any `cat` or `screen` sessions first.

### Keyboard not working
Check board ID - if you have CardputerADV (24) but it reports as Cardputer (14), you have wrong firmware.

### Import errors for local modules
Add `/remote` to sys.path:
```python
import sys
if '/remote' not in sys.path:
    sys.path.insert(0, '/remote')
```
