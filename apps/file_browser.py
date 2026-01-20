"""
File Browser - Multi-Storage File Explorer
===========================================

A read-only file browser for exploring device storage locations:
- /flash  - Internal flash storage (apps, configs, user files)
- /sd     - MicroSD card (optional, requires card inserted)
- /system - System/firmware files

This utility app allows you to navigate directories, view text files,
and check storage capacity across all available storage locations.

STORAGE LOCATIONS:
------------------
    /flash  - Always available, contains your deployed apps and lib/
    /sd     - Available when FAT32 microSD card is inserted
    /system - System partition with firmware files

CONTROLS:
---------
    Up/Down   = Navigate (;/. keys or Fn+arrows)
    Right     = Open file/directory (/ key or Enter)
    Left      = Go up one directory (, key or Backspace)
    I         = Show storage info
    R         = Refresh directory listing
    ESC       = Exit to launcher (or return to selector from list)
"""

import asyncio
import sys

for path in ["/flash/lib", "/remote/lib"]:
    if path not in sys.path:
        sys.path.insert(0, path)

import os

import machine
from app_base import AppBase
from keycode import KEY_NAV_DOWN, KEY_NAV_LEFT, KEY_NAV_RIGHT, KEY_NAV_UP, KeyCode
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

# Storage locations: (display_name, path, requires_mount)
STORAGE_LOCATIONS = [
    ("Flash", "/flash", False),
    ("SD Card", "/sd", True),
    ("System", "/system", False),
]

# UI constants
MAX_VISIBLE_ITEMS = 6  # Number of file entries visible at once
ITEM_HEIGHT = 14  # Height of each file entry row


class FileBrowser(AppBase):
    """Multi-storage file browser for exploring device filesystems."""

    def __init__(self):
        super().__init__()
        self.name = "File Browser"
        self._sd = None  # SDCard object
        self._sd_mounted = False  # Whether SD is mounted
        self._sd_available = None  # None = not checked, True/False = checked
        self._error_msg = ""  # Last error message
        self._current_path = ""  # Current directory path
        self._current_storage = None  # Index into STORAGE_LOCATIONS
        self._storage_selected = 0  # Selected item in storage selector
        self._entries = []  # List of (name, is_dir, size) tuples
        self._selected = 0  # Currently selected entry index
        self._scroll_offset = 0  # Scroll offset for long lists
        self._view_mode = "selector"  # "selector", "list", "info", or "viewer"
        self._file_content = []  # Lines of file being viewed
        self._content_offset = 0  # Vertical scroll offset for file viewer
        self._content_h_offset = 0  # Horizontal scroll offset for long lines

    def on_launch(self):
        """Start in storage selector mode."""
        self._view_mode = "selector"
        self._storage_selected = 0
        self._current_storage = None
        self._sd_available = None  # Will check when selector is drawn
        self._check_sd_available()

    def _check_sd_available(self):
        """Check if SD card is available (try mount/unmount)."""
        if self._sd_available is not None:
            return self._sd_available

        try:
            # Try to initialize and mount SD card
            sd = machine.SDCard(
                slot=3,
                sck=machine.Pin(SD_SCK),
                miso=machine.Pin(SD_MISO),
                mosi=machine.Pin(SD_MOSI),
                cs=machine.Pin(SD_CS),
                freq=SD_FREQ,
            )
            # Try to mount temporarily
            try:
                os.mount(sd, "/sd")
                os.umount("/sd")
            except OSError:
                # May already be mounted or other issue
                try:  # noqa: SIM105 - contextlib not available in MicroPython
                    os.umount("/sd")
                except OSError:
                    pass
            sd.deinit()
            self._sd_available = True
        except OSError:
            self._sd_available = False

        return self._sd_available

    def _mount_sd(self):
        """Mount the SD card."""
        if self._sd_mounted:
            return True

        self._error_msg = ""

        try:
            self._sd = machine.SDCard(
                slot=3,
                sck=machine.Pin(SD_SCK),
                miso=machine.Pin(SD_MISO),
                mosi=machine.Pin(SD_MOSI),
                cs=machine.Pin(SD_CS),
                freq=SD_FREQ,
            )

            try:
                os.mount(self._sd, "/sd")
            except OSError:
                # Already mounted, unmount first
                try:  # noqa: SIM105 - contextlib not available in MicroPython
                    os.umount("/sd")
                except OSError:
                    pass
                os.mount(self._sd, "/sd")

            self._sd_mounted = True
            return True

        except OSError as e:
            self._error_msg = f"Mount failed: {e}"
            self._cleanup_sd()
            return False

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
        if self._sd_mounted:
            try:  # noqa: SIM105 - contextlib not available in MicroPython
                os.umount("/sd")
            except OSError:
                pass
            self._sd_mounted = False

        self._cleanup_sd()

    def _select_storage(self, index):
        """Select a storage location and enter it."""
        name, path, requires_mount = STORAGE_LOCATIONS[index]

        if requires_mount and not self._mount_sd():
            return False

        self._current_storage = index
        self._current_path = path
        self._load_directory()
        self._view_mode = "list"
        return True

    def _return_to_selector(self):
        """Return to storage selector, unmounting SD if needed."""
        if self._sd_mounted:
            self._unmount_sd()

        self._current_storage = None
        self._view_mode = "selector"
        self._sd_available = None  # Re-check on next draw
        self._check_sd_available()

    def _load_directory(self):
        """Load entries from current directory."""
        self._entries = []
        self._selected = 0
        self._scroll_offset = 0
        self._error_msg = ""

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

    def _get_storage_info(self, path):
        """Get storage info for any mount point using statvfs."""
        try:
            stat = os.statvfs(path)
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
        if self._view_mode == "selector":
            self._draw_selector_view()
        elif self._view_mode == "list":
            self._draw_list_view()
        elif self._view_mode == "info":
            self._draw_info_view()
        elif self._view_mode == "viewer":
            self._draw_file_viewer()

    def _draw_selector_view(self):
        """Draw storage location selector."""
        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.ASCII7)

        # Title
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("File Browser")

        Lcd.setTextSize(1)
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 28)
        Lcd.print("Select storage location:")

        # Storage options
        y = 45
        for i, (name, path, requires_mount) in enumerate(STORAGE_LOCATIONS):
            is_selected = i == self._storage_selected

            # Check availability for SD card
            available = True
            status = ""
            if requires_mount:
                available = self._sd_available if self._sd_available is not None else True
                if not available:
                    status = " (no card)"

            # Background for selected
            if is_selected:
                Lcd.fillRect(0, y, SCREEN_W, ITEM_HEIGHT + 4, Lcd.COLOR.DARKGREY)

            bg = Lcd.COLOR.DARKGREY if is_selected else Lcd.COLOR.BLACK

            # Storage name
            if available:
                color = Lcd.COLOR.WHITE if is_selected else Lcd.COLOR.LIGHTGREY
            else:
                color = Lcd.COLOR.RED

            Lcd.setTextColor(color, bg)
            Lcd.setCursor(10, y + 2)
            Lcd.print(f"{name}{status}")

            # Path hint
            Lcd.setTextColor(Lcd.COLOR.YELLOW if is_selected else Lcd.COLOR.DARKGREY, bg)
            Lcd.setCursor(120, y + 2)
            Lcd.print(path)

            y += ITEM_HEIGHT + 6

        # Footer
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(0, SCREEN_H - 12)
        Lcd.print("Up/Dn=Nav  Rt=Open  ESC=Exit")

    def _draw_list_view(self):
        """Draw file browser list view."""
        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.ASCII7)

        # Title bar with storage name and path
        Lcd.setTextSize(1)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLUE)
        Lcd.fillRect(0, 0, SCREEN_W, 12, Lcd.COLOR.BLUE)
        Lcd.setCursor(2, 2)

        # Show storage name and relative path
        if self._current_storage is not None:
            storage_name = STORAGE_LOCATIONS[self._current_storage][0]
            storage_root = STORAGE_LOCATIONS[self._current_storage][1]
            rel_path = self._current_path[len(storage_root) :] or "/"
            display = f"{storage_name}:{rel_path}"
            if len(display) > 38:
                display = display[:35] + "..."
            Lcd.print(display)

        # Error state
        if self._error_msg:
            Lcd.setTextSize(1)
            Lcd.setTextColor(Lcd.COLOR.RED, Lcd.COLOR.BLACK)
            Lcd.setCursor(10, 40)
            if len(self._error_msg) > 35:
                Lcd.print(self._error_msg[:35])
                Lcd.setCursor(10, 52)
                Lcd.print(self._error_msg[35:70])
            else:
                Lcd.print(self._error_msg)

            Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
            Lcd.setCursor(10, 80)
            Lcd.print("BS=Back  R=Retry  ESC=Exit")
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
        Lcd.print("Up/Dn=Nav Rt=Open Lt=Back")
        Lcd.setCursor(0, SCREEN_H - 10)
        Lcd.print("I=Info R=Refresh ESC=Exit")

    def _draw_info_view(self):
        """Draw storage info view."""
        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.ASCII7)

        # Title
        Lcd.setTextSize(2)
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)

        if self._current_storage is not None:
            storage_name = STORAGE_LOCATIONS[self._current_storage][0]
            Lcd.print(f"{storage_name} Info")
        else:
            Lcd.print("Storage Info")

        Lcd.setTextSize(1)

        # Get storage info for current storage root
        storage_root = STORAGE_LOCATIONS[self._current_storage][1] if self._current_storage else "/"
        info = self._get_storage_info(storage_root)

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
            if len(path_display) > 30:
                path_display = "..." + path_display[-27:]
            Lcd.print(f"Path: {path_display}")
        else:
            Lcd.setTextColor(Lcd.COLOR.RED, Lcd.COLOR.BLACK)
            Lcd.setCursor(10, 50)
            Lcd.print("Info not available")

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
        max_chars = 38  # Characters that fit on screen
        y = 14

        if not self._file_content:
            Lcd.setCursor(10, 40)
            Lcd.print("(empty file)")
        else:
            visible_end = min(self._content_offset + max_lines, len(self._file_content))
            max_line_len = 0  # Track longest line for scroll indicator
            for i in range(self._content_offset, visible_end):
                line = self._file_content[i]
                max_line_len = max(max_line_len, len(line))
                # Apply horizontal offset and limit to screen width
                line = line[self._content_h_offset : self._content_h_offset + max_chars]
                Lcd.setCursor(2, y)
                Lcd.print(line)
                y += 12

            # Vertical scroll indicators
            if self._content_offset > 0:
                Lcd.setTextColor(Lcd.COLOR.MAGENTA, Lcd.COLOR.BLACK)
                Lcd.setCursor(SCREEN_W - 12, 14)
                Lcd.print("^")
            if visible_end < len(self._file_content):
                Lcd.setTextColor(Lcd.COLOR.MAGENTA, Lcd.COLOR.BLACK)
                Lcd.setCursor(SCREEN_W - 12, y - 12)
                Lcd.print("v")

            # Horizontal scroll indicators
            if self._content_h_offset > 0:
                Lcd.setTextColor(Lcd.COLOR.MAGENTA, Lcd.COLOR.BLACK)
                Lcd.setCursor(0, 60)
                Lcd.print("<")
            if self._content_h_offset + max_chars < max_line_len:
                Lcd.setTextColor(Lcd.COLOR.MAGENTA, Lcd.COLOR.BLACK)
                Lcd.setCursor(SCREEN_W - 8, 60)
                Lcd.print(">")

        # Line count
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(SCREEN_W - 60, SCREEN_H - 22)
        Lcd.print(f"L{self._content_offset + 1}/{len(self._file_content)}")

        # Footer
        Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
        Lcd.setCursor(0, SCREEN_H - 10)
        Lcd.print("Arrows=Scroll  BS/ESC=Back")

    def _open_file(self, path):
        """Open and read a text file."""
        self._file_content = []
        self._content_offset = 0
        self._content_h_offset = 0

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

    def _navigate_up(self):
        """Go up one directory level or return to selector."""
        if self._current_storage is None:
            return

        storage_root = STORAGE_LOCATIONS[self._current_storage][1]

        # At storage root? Return to selector
        if self._current_path == storage_root:
            self._return_to_selector()
            self.on_view()
            return

        # Remove last path component
        last_slash = self._current_path.rfind("/")
        if last_slash > 0:
            self._current_path = self._current_path[:last_slash]
        else:
            self._current_path = storage_root

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
            if self._view_mode == "info":
                self._view_mode = "list"
                self.on_view()
                event.status = True
                return
            # In list mode, return to selector first
            if self._view_mode == "list":
                self._return_to_selector()
                self.on_view()
                event.status = True
                return
            # In selector mode, let framework handle ESC to exit app
            return

        # Storage selector controls
        if self._view_mode == "selector":
            if key in (KeyCode.KEYCODE_UP, KEY_NAV_UP):
                if self._storage_selected > 0:
                    self._storage_selected -= 1
                    self.on_view()
                event.status = True
                return

            if key in (KeyCode.KEYCODE_DOWN, KEY_NAV_DOWN):
                if self._storage_selected < len(STORAGE_LOCATIONS) - 1:
                    self._storage_selected += 1
                    self.on_view()
                event.status = True
                return

            if key in (KeyCode.KEYCODE_ENTER, KEY_NAV_RIGHT):
                # Check if SD card is available
                name, path, requires_mount = STORAGE_LOCATIONS[self._storage_selected]
                if requires_mount and not self._sd_available:
                    # Can't select unavailable storage
                    event.status = True
                    return

                if self._select_storage(self._storage_selected):
                    self.on_view()
                event.status = True
                return

            event.status = True
            return

        # Backspace - go up or exit viewer (comma handled separately for horizontal scroll)
        if key == KeyCode.KEYCODE_BACKSPACE:
            if self._view_mode in ("viewer", "info"):
                self._view_mode = "list"
                self.on_view()
            elif self._view_mode == "list":
                self._navigate_up()
            event.status = True
            return

        # Comma (left) in list mode - go up directory
        if key == KEY_NAV_LEFT and self._view_mode == "list":
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
            if key in (KeyCode.KEYCODE_UP, KEY_NAV_UP) and self._content_offset > 0:
                self._content_offset -= 1
                self.on_view()
            elif (
                key in (KeyCode.KEYCODE_DOWN, KEY_NAV_DOWN)
                and self._content_offset < len(self._file_content) - 1
            ):
                self._content_offset += 1
                self.on_view()
            elif key in (KeyCode.KEYCODE_RIGHT, KEY_NAV_RIGHT):
                # Scroll right (show more of long lines)
                self._content_h_offset += 10
                self.on_view()
            elif key in (KeyCode.KEYCODE_LEFT, KEY_NAV_LEFT) and self._content_h_offset > 0:
                # Scroll left
                self._content_h_offset = max(0, self._content_h_offset - 10)
                self.on_view()
            event.status = True
            return

        # List view controls
        if self._view_mode == "list":
            if key in (KeyCode.KEYCODE_UP, KEY_NAV_UP):
                if self._selected > 0:
                    self._selected -= 1
                    # Adjust scroll if needed
                    if self._selected < self._scroll_offset:
                        self._scroll_offset = self._selected
                    self.on_view()
                event.status = True
                return

            if key in (KeyCode.KEYCODE_DOWN, KEY_NAV_DOWN):
                if self._selected < len(self._entries) - 1:
                    self._selected += 1
                    # Adjust scroll if needed
                    if self._selected >= self._scroll_offset + MAX_VISIBLE_ITEMS:
                        self._scroll_offset = self._selected - MAX_VISIBLE_ITEMS + 1
                    self.on_view()
                event.status = True
                return

            if key in (KeyCode.KEYCODE_ENTER, KEY_NAV_RIGHT):
                self._enter_selected()
                event.status = True
                return

            # I = Show info
            if key == ord("i") or key == ord("I"):
                self._view_mode = "info"
                self.on_view()
                event.status = True
                return

            # R = Refresh directory
            if key == ord("r") or key == ord("R"):
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
        """Clean up resources."""
        if self._sd_mounted:
            self._unmount_sd()


# Export for framework discovery
App = FileBrowser

if __name__ == "__main__":
    import M5

    M5.begin()
    Lcd.setRotation(1)
    Lcd.setBrightness(40)

    from framework import Framework

    fw = Framework()
    fw.install(FileBrowser())
    fw.start()
