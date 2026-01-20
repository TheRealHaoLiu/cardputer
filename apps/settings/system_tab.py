"""
System Tab - Boot options and system info
"""

from M5 import Lcd, Widgets

from . import (
    BLACK,
    CONTENT_H,
    CONTENT_Y,
    CYAN,
    GRAY,
    GREEN,
    SCREEN_W,
    WHITE,
    YELLOW,
    TabBase,
)


class SystemTab(TabBase):
    """System settings tab."""

    def __init__(self):
        self.boot_option = 1  # 0=main.py, 1=Launcher, 2=Setup
        self.boot_option_saved = 1
        self.boot_labels = ["main.py", "Launcher", "Setup"]

    def draw(self, app):
        """Draw system tab content."""
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(1)

        # Boot mode
        Lcd.setTextColor(CYAN, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 5)
        Lcd.print("Boot Mode:")
        Lcd.setTextColor(WHITE, BLACK)
        boot_label = self.boot_labels[self.boot_option]
        Lcd.setCursor(90, CONTENT_Y + 5)
        Lcd.print(f"[{boot_label}]")

        # Memory info
        try:
            import gc
            gc.collect()
            free_mem = gc.mem_free()
            alloc_mem = gc.mem_alloc()
            total_mem = free_mem + alloc_mem
            Lcd.setTextColor(GRAY, BLACK)
            Lcd.setCursor(10, CONTENT_Y + 25)
            Lcd.print("Memory:")
            Lcd.setTextColor(WHITE, BLACK)
            Lcd.setCursor(70, CONTENT_Y + 25)
            Lcd.print(f"{free_mem:,} / {total_mem:,} free")
        except:
            Lcd.setTextColor(GRAY, BLACK)
            Lcd.setCursor(10, CONTENT_Y + 25)
            Lcd.print("Memory: (unavailable)")

        # Storage info
        try:
            import os
            stat = os.statvfs("/flash")
            block_size = stat[0]
            total_blocks = stat[2]
            free_blocks = stat[3]
            total_kb = (total_blocks * block_size) // 1024
            used_kb = ((total_blocks - free_blocks) * block_size) // 1024
            Lcd.setTextColor(GRAY, BLACK)
            Lcd.setCursor(10, CONTENT_Y + 40)
            Lcd.print("Storage:")
            Lcd.setTextColor(WHITE, BLACK)
            Lcd.setCursor(70, CONTENT_Y + 40)
            Lcd.print(f"{used_kb} KB / {total_kb} KB used")
        except:
            Lcd.setTextColor(GRAY, BLACK)
            Lcd.setCursor(10, CONTENT_Y + 40)
            Lcd.print("Storage: (unavailable)")

        # Controls
        Lcd.setTextColor(GRAY, BLACK)
        Lcd.setCursor(10, CONTENT_Y + 60)
        Lcd.print("[Enter] Change boot  [S] Save  [R] Reboot")

        # Save indicator
        if self.boot_option != self.boot_option_saved:
            Lcd.setTextColor(YELLOW, BLACK)
            Lcd.setCursor(10, CONTENT_Y + 78)
            Lcd.print("* Unsaved changes")
        else:
            Lcd.setTextColor(GREEN, BLACK)
            Lcd.setCursor(10, CONTENT_Y + 78)
            Lcd.print("  Saved")

    def _redraw(self, app):
        """Redraw tab content."""
        Lcd.fillRect(0, CONTENT_Y, SCREEN_W, CONTENT_H, BLACK)
        self.draw(app)

    def _cycle_boot(self, app):
        """Cycle boot option."""
        self.boot_option = (self.boot_option + 1) % len(self.boot_labels)
        print(f"[system] Boot option: {self.boot_labels[self.boot_option]}")
        self._redraw(app)

    def _save(self, app):
        """Save boot option to NVS."""
        try:
            import esp32
            nvs = esp32.NVS("settings")
            nvs.set_i32("boot_option", self.boot_option)
            nvs.commit()
            self.boot_option_saved = self.boot_option
            print(f"[system] Boot option saved: {self.boot_option}")
        except Exception as e:
            print(f"[system] NVS save failed: {e}")
        self._redraw(app)

    def _reboot(self):
        """Reboot device."""
        print("[system] Rebooting...")
        Lcd.fillScreen(BLACK)
        Lcd.setTextColor(WHITE, BLACK)
        Lcd.setCursor(80, 60)
        Lcd.print("Rebooting...")
        try:
            import machine
            machine.reset()
        except Exception as e:
            print(f"[system] Reboot failed: {e}")

    def handle_key(self, app, key):
        """Handle key press."""
        from lib.keycode import KeyCode

        if key == KeyCode.KEYCODE_ENTER:
            self._cycle_boot(app)
            return True

        if key == ord("s") or key == ord("S"):
            self._save(app)
            return True

        if key == ord("r") or key == ord("R"):
            self._reboot()
            return True

        return False
