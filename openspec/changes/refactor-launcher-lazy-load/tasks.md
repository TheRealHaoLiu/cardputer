# Implementation Tasks

## Phase 1: Framework Changes

### 1.1 Add new data structures
- [ ] 1.1.1 Add `_app_registry` dict for hierarchical menu structure
- [ ] 1.1.2 Add `_app_instances` dict for cached app instances
- [ ] 1.1.3 Add `_registry_scanned` boolean flag

### 1.2 Add lightweight scanning
- [ ] 1.2.1 Implement `scan_apps(force=False)` - scans directories and loads manifests without importing
- [ ] 1.2.2 Implement `_load_manifest(dir_path)` - loads `manifest.json` from a directory
- [ ] 1.2.3 Implement `_scan_directory(dir_path)` - recursively scans subdirs for manifests
- [ ] 1.2.4 Add `get_app_registry()` accessor method returning hierarchical structure

### 1.3 Add lazy loading
- [ ] 1.3.1 Implement `get_or_load_app(module_path)` - returns cached or loads new (supports subdir paths)
- [ ] 1.3.2 Implement `_load_app(module_path)` - imports, instantiates, caches
- [ ] 1.3.3 Implement `_reload_app(module_path)` - forces reimport in dev mode

## Phase 2: Launcher Changes

### 2.1 Update data model
- [ ] 2.1.1 Add `_menu_stack` list for tracking submenu navigation
- [ ] 2.1.2 Add `_current_entries` for current menu level items
- [ ] 2.1.3 Replace `_get_apps()` with `_get_menu_entries()` returning current level items

### 2.2 Update on_view()
- [ ] 2.2.1 Replace `fw.discover_apps()` with `fw.scan_apps(force=is_remote)`
- [ ] 2.2.2 Initialize menu at root level

### 2.3 Update menu drawing
- [ ] 2.3.1 Modify `_draw_menu()` to handle both apps and submenus
- [ ] 2.3.2 Display folder icon or indicator for submenus
- [ ] 2.3.3 Show breadcrumb or back indicator when in submenu

### 2.4 Update keyboard handler
- [ ] 2.4.1 On Enter with app: call `fw.get_or_load_app(module_path)` then launch
- [ ] 2.4.2 On Enter with submenu: push to `_menu_stack`, update `_current_entries`, redraw
- [ ] 2.4.3 On ESC in submenu: pop from `_menu_stack`, return to parent menu
- [ ] 2.4.4 On ESC at root: normal ESC behavior (no-op for launcher)
- [ ] 2.4.5 Add error display if app load fails

## Phase 3: Manual Hot-Reload (Dev Mode)

### 3.1 Add reload key
- [ ] 3.1.1 Add 'r' key handler in `_kb_event_handler()`
- [ ] 3.1.2 Clear `_app_instances` cache on 'r' press
- [ ] 3.1.3 Clear `_registry_scanned` flag
- [ ] 3.1.4 Rescan and redraw menu (stay at current level if possible)
- [ ] 3.1.5 Show "Reloading..." indicator briefly

### 3.2 Update UI hints
- [ ] 3.2.1 Update help text to show "r=Reload" in dev mode

## Phase 4: Reorganize Apps Directory

### 4.1 Create directory structure
- [ ] 4.1.1 Create `apps/demo/` subdirectory
- [ ] 4.1.2 Move demo apps (`anim_demo.py`, `sound_demo.py`, etc.) to `apps/demo/` (keep `hello_world.py` at top level)
- [ ] 4.1.3 Keep `launcher.py` in `apps/` root (omit from manifest so it never appears in menu)

### 4.2 Create manifest files
- [ ] 4.2.1 Create `apps/manifest.json` for top-level apps
- [ ] 4.2.2 Create `apps/demo/manifest.json` with demo app names

## Phase 5: Update Documentation

### 5.1 Update hello_world.py template
- [ ] 5.1.1 Update module docstring to mention manifest.json requirement for app registration
- [ ] 5.1.2 Remove mention of `self.name` being used for launcher display (now from manifest)
- [ ] 5.1.3 Update "RUNNING THIS APP" section to explain hierarchical app organization

### 5.2 Update README.md
- [ ] 5.2.1 Update "Creating New Apps" section to include manifest.json registration step
- [ ] 5.2.2 Update to reflect hierarchical directory structure (`apps/demo/`, etc.)
- [ ] 5.2.3 Reinforce learning-focused philosophy in the section

### 5.3 Update openspec/project.md
- [ ] 5.3.1 Update project structure diagram to show new hierarchy with manifest.json files
- [ ] 5.3.2 Update "Hot-reload" documentation to reflect new 'r' key behavior

## Phase 6: Testing

### 6.1 Functional tests
- [ ] 6.1.1 Verify menu displays all apps/submenus without importing
- [ ] 6.1.2 Verify ESC return is instant (no import delay)
- [ ] 6.1.3 Verify submenu navigation works (Enter to descend, ESC to ascend)
- [ ] 6.1.4 Verify first app launch imports and runs correctly
- [ ] 6.1.5 Verify subsequent launches use cached instance
- [ ] 6.1.6 Verify 'r' reload picks up file changes in dev mode
- [ ] 6.1.7 Verify graceful error when app fails to load
