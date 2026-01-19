#!/bin/bash
# Deploy to Cardputer ADV flash storage
#
# WARNING: This replaces ALL of the following on the device:
#   - /flash/main.py
#   - /flash/lib/* (framework, app_base, etc.)
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
echo "WARNING: This will replace /flash/main.py, /flash/lib/*, and /flash/apps/*"
echo ""

# Build the list of lib files dynamically
LIB_FILES=$(ls lib/*.py 2>/dev/null | while read f; do
    filename=$(basename "$f")
    echo "+ cp $f :/flash/lib/$filename"
done | tr '\n' ' ')

# Build the list of app files dynamically
APP_FILES=$(ls apps/*.py 2>/dev/null | while read f; do
    filename=$(basename "$f")
    echo "+ cp $f :/flash/apps/$filename"
done | tr '\n' ' ')

# Use a single mpremote session with chained commands
eval uv run mpremote connect "$DEVICE" \
    exec \"'
import os
def rmtree(path):
    try:
        for f in os.listdir(path):
            fp = path + \"/\" + f
            try:
                os.remove(fp)
            except:
                rmtree(fp)
        os.rmdir(path)
    except:
        pass

# Clear and recreate lib directory
rmtree(\"/flash/lib\")
os.mkdir(\"/flash/lib\")
print(\"Cleared /flash/lib\")

# Clear and recreate apps directory
rmtree(\"/flash/apps\")
os.mkdir(\"/flash/apps\")
print(\"Cleared /flash/apps\")
'\" \
    $LIB_FILES \
    $APP_FILES \
    + cp main.py :/flash/main.py \
    + exec \"'
import os
print(\"Done!\")
print(\"Lib:\", os.listdir(\"/flash/lib\"))
print(\"Apps:\", os.listdir(\"/flash/apps\"))
'\"

echo ""
echo "Reset device to run standalone, or use 'uv run poe run' for development."
