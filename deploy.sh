#!/bin/bash
# Deploy to Cardputer ADV flash storage
#
# WARNING: This replaces ALL of the following on the device:
#   - /flash/boot.py
#   - /flash/main.py
#   - /flash/libs/* (framework, app_base, etc.)
#   - /flash/apps/* (all app files)
#
# Any changes made directly on the device will be lost!

set -e

# Find the device
DEVICE=$(ls /dev/tty.usbmodem* 2>/dev/null | head -1)
if [ -z "$DEVICE" ]; then
    echo "Error: No device found at /dev/tty.usbmodem*"
    exit 1
fi

echo "Deploying to $DEVICE"
echo ""
echo "WARNING: This will replace /flash/boot.py, /flash/main.py, /flash/libs/*, and /flash/apps/*"
echo ""

# Remove local __pycache__ directories before copying
find libs apps -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Python code for cleanup (remove old directories, cp -r will recreate them)
CLEANUP_CODE='import os
def rmtree(p):
 try:
  for f in os.listdir(p):
   fp=p+"/"+f
   try:os.remove(fp)
   except:rmtree(fp)
  os.rmdir(p)
 except:pass
rmtree("/flash/lib");rmtree("/flash/libs");print("Cleared /flash/libs")
rmtree("/flash/apps");print("Cleared /flash/apps")'

# Use a single mpremote session with chained commands
# Note: cp -r libs/ :/flash/ copies libs directory to /flash/libs/
uv run mpremote connect "$DEVICE" \
    exec "$CLEANUP_CODE" \
    + fs cp -r libs/ :/flash/ \
    + fs cp -r apps/ :/flash/ \
    + fs cp main.py :/flash/main.py \
    + fs cp boot.py :/flash/boot.py \
    + fs tree /flash

echo ""
echo "Reset device to run standalone, or use 'uv run poe run' for development."
