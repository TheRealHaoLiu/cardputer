# Add File Browser

## Summary

Promote the SD card demo into a full-fledged file browser application at the root app level, capable of navigating and viewing files across all device storage locations: `/flash`, `/sd`, and `/system`.

## Motivation

The current SD card demo only browses the microSD card and lives in the demo folder. A file browser is a fundamental utility app that users need for exploring the device's internal flash storage (`/flash`) to inspect deployed apps and configs, the system partition (`/system`) to understand firmware structure, and optionally the SD card. It deserves to be a first-class app alongside Settings.

## Scope

- **In scope:**
  - Promote from demo to root-level app (`apps/file_browser.py`)
  - Root selector menu to choose storage location
  - Browsing `/flash` (internal storage), `/sd` (microSD), and `/system` (firmware)
  - Read-only operations (navigate, view text files)
  - Graceful handling when SD card is not present
  - Storage info display for each location

- **Out of scope:**
  - File operations (create, delete, rename, copy)
  - Binary file viewing (hex dump)
  - File search functionality

## Approach

1. Create new `apps/file_browser.py` based on `apps/demo/sdcard_demo.py`
2. Add root selector view that appears on launch
3. Make SD card mounting optional (only when `/sd` is selected)
4. Generalize path handling to work with any storage root
5. Remove the old demo and update manifests

## Affected Files

- `apps/file_browser.py` - New root-level file browser app
- `apps/manifest.json` - Add "File Browser" entry
- `apps/demo/sdcard_demo.py` - Delete (replaced by file_browser.py)
- `apps/demo/manifest.json` - Remove "SD Card Demo" entry

## Supersedes

This proposal supersedes the **SD Card Demo** requirement from `demo-apps` spec (created by the archived `add-sd-card-demo` change). The file browser generalizes SD card browsing to support multiple storage locations and promotes it from demo to utility app.

## Spec Deltas

- `file-browser` - New capability with full file browsing requirements
- `demo-apps` - REMOVED: SD Card Demo requirement (superseded by file-browser)
