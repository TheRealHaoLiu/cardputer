"""
SD Card Demo - MicroSD Storage Explorer
========================================

Demonstrates the Cardputer ADV's SD card slot using MicroPython's
machine.SDCard and standard file I/O. SD card storage enables:
- Storing larger files that don't fit in flash (8MB limit)
- Transferring data between devices via removable media
- Logging sensor data over time
- Loading assets (images, configs, sounds) without reflashing

SD CARD API SUMMARY:
--------------------
    import machine
    import os

    # Initialize SDCard with Cardputer pins (slot=3 for SPI mode)
    # slot=2 is used by the display, so we use slot=3
    sd = machine.SDCard(slot=3, sck=machine.Pin(40), miso=machine.Pin(39),
                        mosi=machine.Pin(14), cs=machine.Pin(12), freq=1000000)

    # Mount to /sd directory
    os.mount(sd, '/sd')

    # File operations via os module
    os.listdir('/sd')           # List directory
    os.stat('/sd/file.txt')     # Get file info (size, etc.)
    os.statvfs('/sd')           # Get filesystem stats (total/free space)
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
    sd.deinit()

REQUIREMENTS:
-------------
- FAT32 formatted microSD card
- Insert with contacts facing away from screen
- May need lower freq (1MHz) if OSError occurs

CONTROLS:
---------
    Up/Down = Navigate file list
    Enter   = Open file/enter directory
    Backspace = Go up one directory
    W = Write test file (creates timestamp file)
    R = Refresh/remount SD card
    ESC = Exit to launcher
"""

import asyncio
import sys
import time

for path in ["/flash/lib", "/remote/lib"]:
    if path not in sys.path:
        sys.path.insert(0, path)

import os

import machine
from app_base import AppBase
from keycode import KeyCode
from M5 import Lcd, Widgets

# Screen dimensions
SCREEN_W = 240
SCREEN_H = 135

# SD Card pins for Cardputer ADV
SD_SCK = 40
SD_MISO = 39
SD_MOSI = 14
SD_CS = 12
SD_FREQ = 1000000  # 1 MHz (conservative, increase if stable)

# Mount point
SD_MOUNT = "/sd"

# UI constants
MAX_VISIBLE_ITEMS = 6  # Number of file entries visible at once
ITEM_HEIGHT = 14  # Height of each file entry row


class SDCardDemo(AppBase):
    """Interactive SD card file browser and demo."""

    def __init__(self):
        super().__init__()
        self.name = "SD Card Demo"
        self._sd = None  # SDCard object
        self._mounted = False  # Whether SD is mounted
        self._error_msg = ""  # Last error message
        self._current_path = SD_MOUNT  # Current directory path
        self._entries = []  # List of (name, is_dir, size) tuples
        self._selected = 0  # Currently selected entry index
        self._scroll_offset = 0  # Scroll offset for long lists
        self._view_mode = "list"  # "list", "info", or "viewer"
        self._file_content = []  # Lines of file being viewed
        self._content_offset = 0  # Scroll offset for file viewer

    def on_launch(self):
        """Initialize and mount SD card."""
        self._mount_sd()
        if self._mounted:
            self._load_directory()

    def _mount_sd(self):
        """Attempt to mount the SD card."""
        self._error_msg = ""
        self._mounted = False

        try:
            # Initialize SDCard using machine.SDCard
            # slot=3 for SPI mode (slot=2 is used by display)
            self._sd = machine.SDCard(
                slot=3,
                sck=machine.Pin(SD_SCK),
                miso=machine.Pin(SD_MISO),
                mosi=machine.Pin(SD_MOSI),
                cs=machine.Pin(SD_CS),
                freq=SD_FREQ,
            )

            # Try to mount
            try:
                os.mount(self._sd, SD_MOUNT)
            except OSError:
                # Already mounted, unmount first
                try:  # noqa: SIM105 - contextlib not available in MicroPython
                    os.umount(SD_MOUNT)
                except OSError:
                    pass
                os.mount(self._sd, SD_MOUNT)

            self._mounted = True
            self._current_path = SD_MOUNT

        except OSError as e:
            self._error_msg = f"No SD card: {e}"
            self._cleanup_sd()

    def _cleanup_sd(self):
        """Clean up SD card resources."""
        if self._sd:
            try:  # noqa: SIM105 - contextlib not available in MicroPython
                self._sd.deinit()
            except Exception:
                pass
            self._sd = None

    def _unmount_sd(self):
        """Unmount and deinitialize SD card."""
        if self._mounted:
            try:  # noqa: SIM105 - contextlib not available in MicroPython
                os.umount(SD_MOUNT)
            except OSError:
                pass
            self._mounted = False

        self._cleanup_sd()

    def _load_directory(self):
        """Load entries from current directory."""
        self._entries = []
        self._selected = 0
        self._scroll_offset = 0

        if not self._mounted:
            return

        try:
            items = os.listdir(self._current_path)
            for name in sorted(items):
                full_path = f"{self._current_path}/{name}"
                try:
                    stat = os.stat(full_path)
                    # stat[0] is mode, 0x4000 = directory flag
                    is_dir = (stat[0] & 0x4000) != 0
                    size = stat[6]  # File size
                    self._entries.append((name, is_dir, size))
                except OSError:
                    # Skip files we can't stat
                    pass
        except OSError as e:
            self._error_msg = f"Read error: {e}"

    def _get_sd_info(self):
        """Get SD card storage info using statvfs."""
        if not self._mounted:
            return None

        try:
            stat = os.statvfs(SD_MOUNT)
            # statvfs returns tuple:
            # (f_bsize, f_frsize, f_blocks, f_bfree, f_bavail, ...)
            block_size = stat[0]
            total_blocks = stat[2]
            free_blocks = stat[3]

            total_mb = (block_size * total_blocks) / (1024 * 1024)
            free_mb = (block_size * free_blocks) / (1024 * 1024)
            used_mb = total_mb - free_mb

            return {
                "total": total_mb,
                "used": used_mb,
                "free": free_mb,
                "percent": (used_mb / total_mb * 100) if total_mb > 0 else 0,
            }
        except OSError:
            return None

    def _format_size(self, size):
        """Format file size for display."""
        if size < 1024:
            return f"{size}B"
        elif size < 1024 * 1024:
            return f"{size // 1024}K"
        else:
            return f"{size // (1024 * 1024)}M"

    def on_view(self):
        """Draw the appropriate view."""
        if self._view_mode == "list":
            self._draw_list_view()
        elif self._view_mode == "info":
            self._draw_info_view()
        elif self._view_mode == "viewer":
            self._draw_file_viewer()

    def _draw_list_view(self):
        """Draw file browser list view."""
        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.ASCII7)

        # Title bar with path
        Lcd.setTextSize(1)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLUE)
        Lcd.fillRect(0, 0, SCREEN_W, 12, Lcd.COLOR.BLUE)
        Lcd.setCursor(2, 2)

        # Truncate path if too long
        display_path = self._current_path
        if len(display_path) > 35:
            display_path = "..." + display_path[-32:]
        Lcd.print(display_path)

        # Error state
        if not self._mounted:
            Lcd.setTextSize(2)
            Lcd.setTextColor(Lcd.COLOR.RED, Lcd.COLOR.BLACK)
            Lcd.setCursor(20, 40)
            Lcd.print("No SD Card")

            Lcd.setTextSize(1)
            Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
            Lcd.setCursor(10, 70)
            if self._error_msg:
                # Wrap long error messages
                if len(self._error_msg) > 35:
                    Lcd.print(self._error_msg[:35])
                    Lcd.setCursor(10, 82)
                    Lcd.print(self._error_msg[35:70])
                else:
                    Lcd.print(self._error_msg)

            Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
            Lcd.setCursor(10, 100)
            Lcd.print("R=Retry  ESC=Exit")
            return

        # File list
        y = 14
        visible_end = min(self._scroll_offset + MAX_VISIBLE_ITEMS, len(self._entries))

        if len(self._entries) == 0:
            Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
            Lcd.setCursor(10, 40)
            Lcd.print("(empty directory)")
        else:
            for i in range(self._scroll_offset, visible_end):
                name, is_dir, size = self._entries[i]
                is_selected = i == self._selected

                # Background for selected item
                if is_selected:
                    Lcd.fillRect(0, y, SCREEN_W, ITEM_HEIGHT, Lcd.COLOR.DARKGREY)

                bg = Lcd.COLOR.DARKGREY if is_selected else Lcd.COLOR.BLACK

                # Display name with "/" suffix for directories
                display_name = name + "/" if is_dir else name
                max_name_len = 28

                # Truncate if needed
                if len(display_name) > max_name_len:
                    display_name = display_name[: max_name_len - 2] + ".."

                # Directories in blue/cyan, files in white/grey
                if is_dir:
                    Lcd.setTextColor(Lcd.COLOR.CYAN if is_selected else Lcd.COLOR.BLUE, bg)
                else:
                    Lcd.setTextColor(Lcd.COLOR.WHITE if is_selected else Lcd.COLOR.LIGHTGREY, bg)

                Lcd.setCursor(4, y + 2)
                Lcd.print(display_name)

                # Size (right-aligned, files only)
                if not is_dir:
                    size_str = self._format_size(size)
                    Lcd.setTextColor(Lcd.COLOR.YELLOW, bg)
                    Lcd.setCursor(SCREEN_W - len(size_str) * 6 - 4, y + 2)
                    Lcd.print(size_str)

                y += ITEM_HEIGHT

        # Scroll indicators
        if self._scroll_offset > 0:
            Lcd.setTextColor(Lcd.COLOR.MAGENTA, Lcd.COLOR.BLACK)
            Lcd.setCursor(SCREEN_W - 12, 14)
            Lcd.print("^")
        if visible_end < len(self._entries):
            Lcd.setTextColor(Lcd.COLOR.MAGENTA, Lcd.COLOR.BLACK)
            Lcd.setCursor(SCREEN_W - 12, y - ITEM_HEIGHT + 2)
            Lcd.print("v")

        # Footer with controls
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(0, SCREEN_H - 22)
        Lcd.print("Up/Dn=Nav Enter=Open BS=Up")
        Lcd.setCursor(0, SCREEN_H - 10)
        Lcd.print("W=Write I=Info R=Refresh ESC=Exit")

    def _draw_info_view(self):
        """Draw SD card info view."""
        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.ASCII7)

        # Title
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("SD Card Info")

        Lcd.setTextSize(1)

        info = self._get_sd_info()
        if info:
            # Storage stats
            Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
            Lcd.setCursor(10, 30)
            Lcd.print(f"Total: {info['total']:.1f} MB")

            Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
            Lcd.setCursor(10, 45)
            Lcd.print(f"Used:  {info['used']:.1f} MB ({info['percent']:.1f}%)")

            Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
            Lcd.setCursor(10, 60)
            Lcd.print(f"Free:  {info['free']:.1f} MB")

            # Usage bar
            bar_x = 10
            bar_y = 78
            bar_w = 180
            bar_h = 12

            # Background
            Lcd.drawRect(bar_x, bar_y, bar_w, bar_h, Lcd.COLOR.WHITE)

            # Filled portion
            filled_w = int(bar_w * info["percent"] / 100)
            if filled_w > 0:
                # Color based on usage
                if info["percent"] > 90:
                    fill_color = Lcd.COLOR.RED
                elif info["percent"] > 70:
                    fill_color = Lcd.COLOR.YELLOW
                else:
                    fill_color = Lcd.COLOR.GREEN
                Lcd.fillRect(bar_x + 1, bar_y + 1, filled_w - 2, bar_h - 2, fill_color)

            # Current path
            Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
            Lcd.setCursor(10, 98)
            path_display = self._current_path
            if len(path_display) > 35:
                path_display = "..." + path_display[-32:]
            Lcd.print(f"Path: {path_display}")
        else:
            Lcd.setTextColor(Lcd.COLOR.RED, Lcd.COLOR.BLACK)
            Lcd.setCursor(10, 50)
            Lcd.print("Could not read SD card info")

        # Footer
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(0, SCREEN_H - 12)
        Lcd.print("Any key=Back to list  ESC=Exit")

    def _draw_file_viewer(self):
        """Draw text file viewer."""
        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.ASCII7)

        # Title bar
        Lcd.setTextSize(1)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLUE)
        Lcd.fillRect(0, 0, SCREEN_W, 12, Lcd.COLOR.BLUE)
        Lcd.setCursor(2, 2)

        # Show filename from selected entry
        if 0 <= self._selected < len(self._entries):
            name = self._entries[self._selected][0]
            if len(name) > 35:
                name = name[:32] + "..."
            Lcd.print(name)

        # File content
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        max_lines = 8
        y = 14

        if not self._file_content:
            Lcd.setCursor(10, 40)
            Lcd.print("(empty file)")
        else:
            visible_end = min(self._content_offset + max_lines, len(self._file_content))
            for i in range(self._content_offset, visible_end):
                line = self._file_content[i]
                # Truncate long lines
                if len(line) > 38:
                    line = line[:35] + "..."
                Lcd.setCursor(2, y)
                Lcd.print(line)
                y += 12

            # Scroll indicators
            if self._content_offset > 0:
                Lcd.setTextColor(Lcd.COLOR.MAGENTA, Lcd.COLOR.BLACK)
                Lcd.setCursor(SCREEN_W - 12, 14)
                Lcd.print("^")
            if visible_end < len(self._file_content):
                Lcd.setTextColor(Lcd.COLOR.MAGENTA, Lcd.COLOR.BLACK)
                Lcd.setCursor(SCREEN_W - 12, y - 12)
                Lcd.print("v")

        # Line count
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(SCREEN_W - 60, SCREEN_H - 22)
        Lcd.print(f"L{self._content_offset + 1}/{len(self._file_content)}")

        # Footer
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(0, SCREEN_H - 10)
        Lcd.print("Up/Dn=Scroll BS/ESC=Back")

    def _open_file(self, path):
        """Open and read a text file."""
        self._file_content = []
        self._content_offset = 0

        try:
            with open(path) as f:
                # Read up to 100 lines (memory limit)
                for _ in range(100):
                    line = f.readline()
                    if not line:
                        break
                    # Strip trailing newline
                    self._file_content.append(line.rstrip("\n\r"))
        except OSError as e:
            self._file_content = [f"Error: {e}"]
        except Exception:  # noqa: BLE001 - catch decode errors for binary files
            self._file_content = ["(binary file - cannot display)"]

        self._view_mode = "viewer"

    def _write_test_file(self):
        """Write a test file with timestamp."""
        if not self._mounted:
            return

        try:
            # Get current time tuple
            t = time.localtime()
            timestamp = f"{t[0]}-{t[1]:02d}-{t[2]:02d}_{t[3]:02d}{t[4]:02d}{t[5]:02d}"
            filename = f"test_{timestamp}.txt"
            filepath = f"{self._current_path}/{filename}"

            with open(filepath, "w") as f:
                f.write("Cardputer SD Card Test\n")
                f.write(f"Created: {timestamp}\n")
                f.write(f"Path: {filepath}\n")
                f.write("\nThis file demonstrates SD card write.\n")

            # Reload directory to show new file
            self._load_directory()
            self.on_view()

        except OSError as e:
            self._error_msg = f"Write failed: {e}"

    def _navigate_up(self):
        """Go up one directory level."""
        if self._current_path == SD_MOUNT:
            return  # Already at root

        # Remove last path component
        last_slash = self._current_path.rfind("/")
        if last_slash > 0:
            self._current_path = self._current_path[:last_slash]
        else:
            self._current_path = SD_MOUNT

        self._load_directory()
        self.on_view()

    def _enter_selected(self):
        """Enter directory or open file."""
        if not self._entries:
            return

        name, is_dir, size = self._entries[self._selected]
        full_path = f"{self._current_path}/{name}"

        if is_dir:
            self._current_path = full_path
            self._load_directory()
            self.on_view()
        else:
            self._open_file(full_path)
            self.on_view()

    async def _kb_event_handler(self, event, fw):
        """Handle keyboard events."""
        key = event.key

        # ESC handling
        if key == KeyCode.KEYCODE_ESC:
            if self._view_mode == "viewer":
                self._view_mode = "list"
                self.on_view()
                event.status = True
                return
            # Let framework handle ESC in list mode
            return

        # Backspace - go up or exit viewer
        if key == KeyCode.KEYCODE_BACKSPACE:
            if self._view_mode == "viewer":
                self._view_mode = "list"
                self.on_view()
            elif self._view_mode == "list" and self._mounted:
                self._navigate_up()
            event.status = True
            return

        # Info view - any key returns to list
        if self._view_mode == "info":
            self._view_mode = "list"
            self.on_view()
            event.status = True
            return

        # File viewer controls
        if self._view_mode == "viewer":
            if key == KeyCode.KEYCODE_UP and self._content_offset > 0:
                self._content_offset -= 1
                self.on_view()
            elif key == KeyCode.KEYCODE_DOWN and self._content_offset < len(self._file_content) - 1:
                self._content_offset += 1
                self.on_view()
            event.status = True
            return

        # List view controls
        if self._view_mode == "list":
            if key == KeyCode.KEYCODE_UP:
                if self._selected > 0:
                    self._selected -= 1
                    # Adjust scroll if needed
                    if self._selected < self._scroll_offset:
                        self._scroll_offset = self._selected
                    self.on_view()
                event.status = True
                return

            if key == KeyCode.KEYCODE_DOWN:
                if self._selected < len(self._entries) - 1:
                    self._selected += 1
                    # Adjust scroll if needed
                    if self._selected >= self._scroll_offset + MAX_VISIBLE_ITEMS:
                        self._scroll_offset = self._selected - MAX_VISIBLE_ITEMS + 1
                    self.on_view()
                event.status = True
                return

            if key == KeyCode.KEYCODE_ENTER:
                self._enter_selected()
                event.status = True
                return

            # W = Write test file
            if key == ord("w") or key == ord("W"):
                self._write_test_file()
                event.status = True
                return

            # I = Show info
            if key == ord("i") or key == ord("I"):
                self._view_mode = "info"
                self.on_view()
                event.status = True
                return

            # R = Refresh/remount
            if key == ord("r") or key == ord("R"):
                self._unmount_sd()
                self._mount_sd()
                if self._mounted:
                    self._load_directory()
                self.on_view()
                event.status = True
                return

        event.status = True

    async def on_run(self):
        """Background task."""
        while True:
            await asyncio.sleep_ms(100)

    def on_exit(self):
        """Clean up SD card resources."""
        self._unmount_sd()


# Export for framework discovery
App = SDCardDemo

if __name__ == "__main__":
    import M5

    M5.begin()
    Lcd.setRotation(1)
    Lcd.setBrightness(40)

    from framework import Framework

    fw = Framework()
    fw.install(SDCardDemo())
    fw.start()
