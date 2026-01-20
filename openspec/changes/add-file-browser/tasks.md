# Tasks for add-file-browser

## Setup Tasks

- [x] **1. Create new file_browser.py from sdcard_demo.py**
  - Copy `apps/demo/sdcard_demo.py` to `apps/file_browser.py`
  - This becomes the base for all subsequent changes

- [x] **2. Rename class and update app name**
  - Rename class from SDCardDemo to FileBrowser
  - Update self.name to "File Browser"

## Implementation Tasks

- [x] **3. Add storage location constants and configuration**
  - Define STORAGE_LOCATIONS list with (name, path, requires_mount) tuples
  - Entries: ("Flash", "/flash", False), ("SD Card", "/sd", True), ("System", "/system", False)
  - Add _current_storage to track which storage is active

- [x] **4. Add root selector view mode**
  - Add "selector" to view_mode states
  - Create _draw_selector_view() method
  - Display storage locations with availability indicators
  - Track _storage_selected index

- [x] **5. Implement SD card availability check**
  - Add _check_sd_available() method that attempts mount/unmount
  - Cache availability result to avoid repeated mount attempts
  - Show "(no card)" indicator in selector for unavailable SD

- [x] **6. Implement storage location selection**
  - Handle Enter key in selector view to choose location
  - Mount SD card only when /sd is selected
  - Set _current_path to selected storage root
  - Transition to list view

- [x] **7. Refactor _navigate_up() for multi-storage**
  - Track current storage root (e.g., "/flash", "/sd")
  - When at storage root and Backspace pressed, return to selector
  - Unmount SD card when leaving /sd storage

- [x] **8. Generalize _get_storage_info() for any mount point**
  - Rename from _get_sd_info()
  - Accept path parameter instead of hardcoded SD_MOUNT
  - Handle statvfs errors gracefully for /system

- [x] **9. Update _draw_list_view() header**
  - Show current storage name in title bar (e.g., "Flash: /apps")
  - Adjust path truncation to account for storage prefix

- [x] **10. Remove write functionality**
  - Remove _write_test_file() method
  - Remove W key handling from _kb_event_handler()
  - Update footer help text to remove W reference

- [x] **11. Replace R remount with refresh**
  - Change R key to call _load_directory() only
  - Remove SD card remount logic from R handler
  - Update help text to say "R=Refresh"

- [x] **12. Update on_launch() for selector mode**
  - Start in selector view mode instead of auto-mounting SD
  - Initialize storage availability state
  - Don't mount SD card until selected

- [x] **13. Update on_exit() cleanup**
  - Only unmount SD if it was mounted
  - Track mounted state properly

- [x] **14. Update keyboard navigation for selector**
  - Up/Down to navigate storage options
  - Enter to select storage
  - ESC to exit app from selector

- [x] **15. Update module docstring**
  - Rewrite header documentation for file browser
  - Document new controls and storage locations
  - Remove SD-card-specific API docs

## Manifest Tasks

- [x] **16. Add entry to apps/manifest.json**
  - Add "file_browser": "File Browser" entry

- [x] **17. Remove entry from apps/demo/manifest.json**
  - Remove "sdcard_demo": "SD Card Demo" entry

- [x] **18. Delete apps/demo/sdcard_demo.py**
  - Remove the old demo file after file_browser.py is complete

## Validation Tasks

- [ ] **19. Test flash storage browsing**
  - Launch app, select Flash
  - Navigate directories and view files
  - Verify storage info display works

- [ ] **20. Test SD card browsing**
  - With card inserted: select SD Card, browse files
  - Without card: verify "(no card)" indicator shows
  - Verify clean unmount on exit

- [ ] **21. Test system browsing**
  - Select System, navigate directories
  - Handle any permission errors gracefully

- [ ] **22. Test navigation edge cases**
  - Backspace at storage root returns to selector
  - Selector displays correctly after returning
  - SD card state refreshed when returning to selector

- [x] **23. Run linter and fix issues**
  - Run `uv run ruff check apps/file_browser.py`
  - Run `uv run ruff format apps/file_browser.py`
  - Fix any linting errors

## File Changes

| File | Change |
|------|--------|
| `apps/file_browser.py` | New file (based on sdcard_demo.py) |
| `apps/manifest.json` | Add "file_browser": "File Browser" |
| `apps/demo/sdcard_demo.py` | Delete |
| `apps/demo/manifest.json` | Remove "sdcard_demo" entry |
