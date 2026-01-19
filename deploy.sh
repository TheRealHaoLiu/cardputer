#!/bin/bash
# Deploy to Cardputer ADV flash storage
# Replaces /flash/apps and /flash/main.py

set -e

# Find the device
DEVICE=$(ls /dev/tty.usbmodem* 2>/dev/null | head -1)
if [ -z "$DEVICE" ]; then
    echo "Error: No device found at /dev/tty.usbmodem*"
    exit 1
fi

echo "Deploying to $DEVICE"
echo ""

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
rmtree(\"/flash/apps\")
os.mkdir(\"/flash/apps\")
print(\"Cleared /flash/apps\")
'\" \
    $APP_FILES \
    + cp main.py :/flash/main.py \
    + exec \"'print(\"Done!\"); print(\"Apps:\", __import__(\"os\").listdir(\"/flash/apps\"))'\"

echo ""
echo "Reset device to run standalone, or use 'uv run poe dev' for development."
