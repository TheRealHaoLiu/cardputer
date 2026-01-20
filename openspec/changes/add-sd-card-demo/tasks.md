# Tasks: Add SD Card Demo

## 1. Implementation

- [ ] 1.1 Create `apps/demo/sdcard_demo.py` with AppBase structure and docstring
- [ ] 1.2 Implement SD card mount with Cardputer ADV pins (SCK:40, MISO:39, MOSI:14, CS:12)
- [ ] 1.3 Add mount status display and error handling for missing card
- [ ] 1.4 Display SD card info using `os.statvfs()` (total/used/free MB, usage bar)
- [ ] 1.5 Implement directory listing view with scrollable file/folder list
- [ ] 1.6 Show file info (name, size in KB/MB, type indicator for dir vs file)
- [ ] 1.7 Implement file content viewer for text files (scrollable)
- [ ] 1.8 Implement test file creation (write timestamp to demo write capability)
- [ ] 1.9 Add keyboard navigation (up/down scroll, Enter to view/enter dir, Backspace to go up)
- [ ] 1.10 Handle SD card errors gracefully (show user-friendly messages)
- [ ] 1.11 Implement `on_exit()` cleanup (close files, unmount, deinit SDCard)

## 2. Integration

- [ ] 2.1 Add entry to `apps/demo/manifest.json`
- [ ] 2.2 Test via `poe run apps/demo/sdcard_demo.py` with SD card inserted
- [ ] 2.3 Test error handling with no SD card inserted
- [ ] 2.4 Test from launcher menu navigation
