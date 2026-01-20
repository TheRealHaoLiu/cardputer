# Change: Add SD Card Demo App

## Why

The Cardputer ADV has an SD card slot (GPIO pins SCK:40, MISO:39, MOSI:14, CS:12) but no demo showing how to use it. SD card storage enables:
- Storing larger files that don't fit in flash (8MB limit)
- Transferring data between devices via removable media
- Logging sensor data over time
- Loading assets (images, configs, sounds) without reflashing

This demo will teach MicroPython SD card operations on ESP32-S3 using `machine.SDCard` and standard file I/O.

## What Changes

- Add `apps/demo/sdcard_demo.py` - Interactive SD card demo app
- Demonstrates:
  - Mounting SD card with proper SPI pin configuration
  - Directory listing with file sizes
  - File content viewing (text files)
  - File writing (create test file with timestamp)
  - Directory navigation
  - Error handling for missing/unmounted card
- Follows established demo app pattern (AppBase, lifecycle, keyboard events)

## Impact

- Affected specs: `demo-apps`
- Affected code: `apps/demo/sdcard_demo.py` (new), `apps/demo/manifest.json` (add entry)

## Technical Notes

**SD Card API (MicroPython):**
```python
import machine, os

# Initialize with Cardputer ADV pins
sd = machine.SDCard(slot=2, sck=40, miso=39, mosi=14, cs=12, freq=1000000)

# Mount to /sd directory
os.mount(sd, '/sd')

# File operations via os module
os.listdir('/sd')           # List directory
os.stat('/sd/file.txt')     # Get file info (size, etc.)
os.mkdir('/sd/newdir')      # Create directory
os.remove('/sd/file.txt')   # Delete file
os.chdir('/sd')             # Change directory

# File I/O via open()
with open('/sd/data.txt', 'w') as f:
    f.write('Hello SD card!')

with open('/sd/data.txt', 'r') as f:
    content = f.read()

# Unmount before ejecting
os.umount('/sd')
```

**Requirements:**
- FAT32 formatted microSD card
- Insert with contacts facing away from screen
- May need lower freq (1MHz) if OSError occurs
