# Refactor Launcher for Lazy Loading and Hierarchical Menus

## Why

The launcher is slow in development mode. Every ESC press triggers `discover_apps()` which imports and instantiates ALL app modules. In remote/dev mode, it also deletes modules from `sys.modules` and reimports them for hot-reload. With 10+ apps, this causes a noticeable delay (1-2 seconds).

The menu only needs app names to display - we don't need to load the actual apps until the user selects one.

Additionally, as the number of apps grows, a flat menu becomes unwieldy. Apps should be organized into categories (e.g., demos, games, tools).

## What Changes

- **Separate discovery from instantiation**: New `scan_apps()` method scans directories without importing
- **Lazy loading**: Apps are imported and instantiated only when launched via `get_or_load_app()`
- **Instance caching**: Loaded apps are cached to avoid repeated imports on subsequent launches
- **Manual hot-reload**: Add 'r' key in dev mode to force reload instead of reloading on every ESC
- **Per-folder manifest.json**: Each directory has a `manifest.json` with app display names
- **Hierarchical menus**: Subdirectories become submenus, directory structure defines hierarchy

## Directory Structure

```
apps/
  manifest.json        # top-level apps: {"hello_world": "Hello World", "settings": "Settings"} (launcher omitted)
  launcher.py          # special app, not in manifest
  hello_world.py       # template app - stays at top level for discoverability
  settings.py
  demo/
    manifest.json      # {"sound_demo": "Sound Demo", "anim_demo": "Animation Demo", ...}
    sound_demo.py
    anim_demo.py
  games/
    manifest.json      # {"snake": "Snake", ...}
    snake.py
```

## Impact

- Affected specs: launcher (new), framework internals
- Affected code:
  - `lib/framework.py` - Add `scan_apps()`, `get_or_load_app()`, hierarchical registry
  - `apps/launcher.py` - Hierarchical menu display, submenu navigation, lazy load on Enter, add 'r' reload key
  - `apps/` directory - Reorganize into subdirectories with per-folder manifests
