# Tasks: Add SD Card Demo

## 1. Implementation

- [x] 1.1 Create `apps/demo/sdcard_demo.py` with AppBase structure and docstring
- [x] 1.2 Implement SD card mount with Cardputer ADV pins (SCK:40, MISO:39, MOSI:14, CS:12)
- [x] 1.3 Add mount status display and error handling for missing card
- [x] 1.4 Display SD card info using `os.statvfs()` (total/used/free MB, usage bar)
- [x] 1.5 Implement directory listing view with scrollable file/folder list
- [x] 1.6 Show file info (name, size in KB/MB, type indicator for dir vs file)
- [x] 1.7 Implement file content viewer for text files (scrollable)
- [x] 1.8 Implement test file creation (write timestamp to demo write capability)
- [x] 1.9 Add keyboard navigation (up/down scroll, Enter to view/enter dir, Backspace to go up)
- [x] 1.10 Handle SD card errors gracefully (show user-friendly messages)
- [x] 1.11 Implement `on_exit()` cleanup (close files, unmount, deinit SDCard)

## 2. Integration

- [x] 2.1 Add entry to `apps/demo/manifest.json`
- [x] 2.2 Test via `poe run apps/demo/sdcard_demo.py` with SD card inserted
- [x] 2.3 Test error handling with no SD card inserted
- [x] 2.4 Test from launcher menu navigation
