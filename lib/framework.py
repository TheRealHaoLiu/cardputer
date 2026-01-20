"""
Cardputer App Framework
=======================

The framework is the core of the app system. It:
- Manages a list of installed apps
- Runs the main async event loop
- Polls the keyboard and routes input to the current app
- Handles ESC key to return to launcher

HOW IT WORKS:
-------------
1. main.py creates a Framework instance
2. Apps are installed via fw.install(app)
3. fw.start() begins the main event loop
4. The event loop polls keyboard every 10ms
5. Key events are routed to the current app's _kb_event_handler()
6. ESC always returns to the launcher

KEYBOARD HANDLING:
------------------
The framework uses MatrixKeyboard from the hardware module.
MatrixKeyboard auto-detects Cardputer vs Cardputer ADV hardware.

Each tick of the event loop:
1. kb.tick() - Poll keyboard hardware for new events
2. kb.is_pressed() - Check if a key was pressed
3. kb.get_key() - Get the key code
4. Route to current app's _kb_event_handler(event, fw)
5. If event not handled and key is ESC, return to launcher

USAGE:
------
    from framework import Framework
    from apps.launcher import LauncherApp
    from apps.my_app import MyApp

    fw = Framework()
    launcher = LauncherApp()
    fw.install_launcher(launcher)
    fw.install(launcher)
    fw.install(MyApp())
    fw.start()  # Blocks forever
"""

# =============================================================================
# IMPORTS
# =============================================================================

import asyncio
import json
import os
import sys

import app_base
import M5
from hardware import MatrixKeyboard

# Key code constants
from keycode import KeyCode

# =============================================================================
# KEY EVENT CLASS
# =============================================================================


class KeyEvent:
    """
    Represents a keyboard event passed to apps.

    Attributes:
    -----------
    key : int
        The key code. Either an ASCII value (0x20-0x7E for printable chars)
        or a KeyCode constant (KEYCODE_ESC, KEYCODE_ENTER, etc.)

    status : bool
        Set to True by the handler if the event was consumed.
        If False after handler returns, framework may take default action.
        (For example, ESC with status=False triggers return to launcher)

    Usage in _kb_event_handler:
    ---------------------------
        async def _kb_event_handler(self, event, fw):
            if event.key == ord('q'):
                # Handle 'q' key
                event.status = True  # We handled it
            # Don't set status for keys you don't handle
            # ESC should NOT be marked as handled (let framework handle it)
    """

    key = 0
    status = False


# =============================================================================
# FRAMEWORK CLASS
# =============================================================================


class Framework:
    """
    The main application framework.

    Manages installed apps and runs the main event loop.
    """

    def __init__(self) -> None:
        """
        Initialize the framework.

        Creates empty app list and sets up the app selector.
        Apps are added later via install().
        """
        self._apps = []  # List of installed apps (legacy, for compatibility)
        self._app_selector = app_base.AppSelector(self._apps)
        self._launcher = None  # Special app that ESC returns to
        self._running = False  # Controls main event loop
        self._kb = None  # Keyboard instance (created in run())

        # Lazy loading data structures
        # Hierarchical registry: {"apps": [...], "submenus": {"demo": {...}, ...}}
        # Each app entry: {"module": "hello_world", "name": "Hello World", "path": ""}
        # Each submenu entry: {"name": "Demo", "path": "demo", "apps": [...], "submenus": {...}}
        self._app_registry = None  # Populated by scan_apps()
        self._app_instances = {}  # Cache: module_path -> app instance
        self._registry_scanned = False  # True after first scan_apps() call

        # Detect run mode once at init (doesn't change without reset)
        try:
            os.stat("/remote/apps")
            self._apps_dir = "/remote/apps"
            self._is_remote = True
        except OSError:
            self._apps_dir = "/flash/apps"
            self._is_remote = False

    # =========================================================================
    # APP INSTALLATION
    # =========================================================================

    def install_launcher(self, launcher: app_base.AppBase):
        """
        Set the launcher (home screen) app.

        The launcher is special:
        - It's the first app shown on startup
        - Pressing ESC from any app returns here
        - It should also be install()'d to appear in app lists

        Parameters:
        -----------
        launcher : AppBase
            The launcher app instance
        """
        self._launcher = launcher

    def install(self, app: app_base.AppBase):
        """
        Install an app into the framework.

        This calls app.install() (which calls on_install) and adds
        the app to the internal list.

        Parameters:
        -----------
        app : AppBase
            The app instance to install
        """
        app.install()
        self._apps.append(app)

    def get_apps(self):
        """
        Get the list of installed apps.

        Used by the launcher to display available apps.

        Returns:
        --------
        list : List of AppBase instances
        """
        return self._apps

    def _find_app_class(self, module):
        """Find AppBase subclass in module."""
        for attr_name in dir(module):
            if attr_name.startswith("_"):
                continue
            attr = getattr(module, attr_name)
            if hasattr(attr, "__bases__"):
                for base in attr.__bases__:
                    if base.__name__ == "AppBase":
                        return attr
        return None

    # =========================================================================
    # LAZY LOADING - SCANNING
    # =========================================================================

    def scan_apps(self, force=False):
        """
        Scan apps directory and build registry without importing modules.

        This reads manifest.json files to get app names and builds a
        hierarchical menu structure. No app modules are imported.

        Parameters:
        -----------
        force : bool
            If True, rescan even if already scanned. Use for hot-reload.
        """
        if self._registry_scanned and not force:
            return

        print(f"[scan] Scanning {self._apps_dir} (force={force})")

        # Clear caches on force reload
        if force:
            self._app_instances.clear()

        # Build hierarchical registry
        self._app_registry = self._scan_directory(self._apps_dir, "")
        self._registry_scanned = True

    def _scan_directory(self, dir_path, relative_path):
        """
        Recursively scan a directory for apps and submenus.

        Returns:
        --------
        dict with keys:
            - "apps": list of app entries [{module, name, path}, ...]
            - "submenus": dict of subdir_name -> submenu registry
        """
        result = {"apps": [], "submenus": {}}

        # Load manifest for this directory
        manifest = self._load_manifest(dir_path)

        # Scan directory entries
        try:
            entries = list(os.ilistdir(dir_path))
        except OSError:
            print(f"[scan] Cannot read directory: {dir_path}")
            return result

        for entry in entries:
            name = entry[0]
            entry_type = entry[1]  # 0x4000 = directory, 0x8000 = file

            # Skip hidden files and special files
            if name.startswith("_") or name.startswith("."):
                continue

            # Directory -> potential submenu
            if entry_type == 0x4000:
                subdir_path = f"{dir_path}/{name}"
                sub_relative = f"{relative_path}/{name}" if relative_path else name

                # Only add as submenu if it has a manifest
                sub_manifest_path = f"{subdir_path}/manifest.json"
                try:
                    os.stat(sub_manifest_path)
                    # Recursively scan subdirectory
                    submenu = self._scan_directory(subdir_path, sub_relative)
                    # Derive display name from directory name (capitalize each word)
                    # MicroPython lacks .title() and .capitalize(), do it manually
                    words = name.split("_")
                    display_name = " ".join(w[0].upper() + w[1:] if w else w for w in words)
                    submenu["name"] = display_name
                    submenu["path"] = sub_relative
                    result["submenus"][name] = submenu
                    print(f"[scan] Found submenu: {display_name} ({sub_relative})")
                except OSError:
                    # No manifest, skip this directory
                    pass

            # Python file -> potential app
            elif name.endswith(".py") and entry_type == 0x8000:
                module_name = name[:-3]  # Remove .py

                # Skip launcher (never shown in menu)
                if module_name == "launcher":
                    continue

                # Check if module is in manifest
                if module_name in manifest:
                    display_name = manifest[module_name]
                    module_path = f"{relative_path}/{module_name}" if relative_path else module_name
                    result["apps"].append({
                        "module": module_name,
                        "name": display_name,
                        "path": module_path,
                    })
                    print(f"[scan] Found app: {display_name} ({module_path})")

        return result

    def _load_manifest(self, dir_path):
        """
        Load manifest.json from a directory.

        Returns:
        --------
        dict mapping module names to display names, or empty dict if not found.
        """
        manifest_path = f"{dir_path}/manifest.json"
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
                print(f"[scan] Loaded manifest: {manifest_path}")
                return manifest
        except OSError:
            return {}
        except ValueError as e:
            print(f"[scan] Invalid JSON in {manifest_path}: {e}")
            return {}

    def get_app_registry(self):
        """
        Get the hierarchical app registry.

        Call scan_apps() first to populate the registry.

        Returns:
        --------
        dict with "apps" and "submenus" keys, or None if not scanned.
        """
        return self._app_registry

    # =========================================================================
    # LAZY LOADING - APP INSTANTIATION
    # =========================================================================

    def get_or_load_app(self, module_path):
        """
        Get an app instance, loading it if necessary.

        Parameters:
        -----------
        module_path : str
            The module path (e.g., "hello_world" or "demo/sound_demo")

        Returns:
        --------
        AppBase instance, or None if loading failed.
        """
        # Check cache first
        if module_path in self._app_instances:
            print(f"[load] Using cached: {module_path}")
            return self._app_instances[module_path]

        # Load the app
        return self._load_app(module_path)

    def _load_app(self, module_path):
        """
        Import and instantiate an app module.

        Parameters:
        -----------
        module_path : str
            The module path (e.g., "hello_world" or "demo/sound_demo")

        Returns:
        --------
        AppBase instance, or None if loading failed.
        """
        print(f"[load] Loading app: {module_path}")

        # Convert path to module name for import
        # "demo/sound_demo" -> need to handle subdirectory imports
        subdir_full = None
        if "/" in module_path:
            # Subdirectory app - need to adjust sys.path temporarily
            parts = module_path.rsplit("/", 1)
            subdir = parts[0]
            module_name = parts[1]
            subdir_full = f"{self._apps_dir}/{subdir}"

            # Add subdir to path for import
            if subdir_full not in sys.path:
                sys.path.insert(0, subdir_full)
            else:
                subdir_full = None  # Already in path, don't remove later
        else:
            module_name = module_path

        try:
            # Force reimport if already loaded
            if module_name in sys.modules:
                del sys.modules[module_name]

            module = __import__(module_name)
            app_class = self._find_app_class(module)

            if app_class:
                app = app_class()
                app.install()
                self._app_instances[module_path] = app
                # Add to _apps list so AppSelector can manage it
                if app not in self._apps:
                    self._apps.append(app)
                print(f"[load] Loaded: {app_class.__name__}")
                return app
            else:
                print(f"[load] No AppBase subclass in {module_path}")
                return None

        except Exception as e:
            print(f"[load] Failed to load {module_path}: {e}")
            return None

        finally:
            # Clean up sys.path after import
            if subdir_full and subdir_full in sys.path:
                sys.path.remove(subdir_full)

    def clear_app_cache(self):
        """Clear all cached app instances and modules (for hot-reload)."""
        self._app_instances.clear()
        self._registry_scanned = False

        # Clear lazily-loaded apps from _apps list (keep launcher)
        # Use slice assignment to modify in-place (keeps _app_selector reference valid)
        self._apps[:] = [app for app in self._apps if app is self._launcher]

        # Clear cached Python modules so they're reimported fresh
        # This is essential for hot-reload to pick up code changes
        modules_to_clear = []
        for mod_name in sys.modules:
            mod = sys.modules[mod_name]
            # Clear modules loaded from apps directory
            if (
                hasattr(mod, "__file__")
                and mod.__file__
                and ("/apps/" in mod.__file__ or "/remote/" in mod.__file__)
            ):
                modules_to_clear.append(mod_name)
        for mod_name in modules_to_clear:
            del sys.modules[mod_name]
            print(f"[reload] Cleared module: {mod_name}")

        print("[reload] Cleared app cache")

    # =========================================================================
    # FRAMEWORK CONTROL
    # =========================================================================

    def start(self):
        """
        Start the framework.

        This runs the main event loop and NEVER RETURNS.
        Call this as the last thing in main.py.

        The event loop:
        1. Starts the launcher
        2. Polls keyboard continuously
        3. Routes events to current app
        4. Handles ESC to return to launcher
        """
        asyncio.run(self.run())

    # =========================================================================
    # APP LIFECYCLE CONTROL
    # =========================================================================

    async def unload(self, app: app_base.AppBase):
        """Stop an app (calls stop() which triggers on_hide + on_exit)."""
        app.stop()

    async def load(self, app: app_base.AppBase):
        """Start an app (calls start() which triggers lifecycle methods)."""
        app.start(self)

    async def reload(self, app: app_base.AppBase):
        """Restart an app (stop then start)."""
        app.stop()
        app.start(self)

    async def launch_app(self, app: app_base.AppBase):
        """
        Switch to a different app.

        Stops the current app and starts the new one.
        Called by launcher when user selects an app.

        Parameters:
        -----------
        app : AppBase
            The app to switch to
        """
        current = self._app_selector.current()
        current_name = getattr(current, "name", type(current).__name__)
        app_name = getattr(app, "name", type(app).__name__)
        print(f"[framework] Launching {app_name} (from {current_name})")
        current.stop()
        self._app_selector.select(app)
        app.start(self)

    async def return_to_launcher(self):
        """
        Return to the launcher app.

        Stops the current app and starts the launcher.
        Called when ESC is pressed and not handled by the app.
        If no launcher is set (standalone mode), exits the framework.
        """
        current = self._app_selector.current()
        current_name = getattr(current, "name", type(current).__name__)

        # No launcher set - exit the framework (standalone mode)
        if not self._launcher:
            print(f"[framework] Exiting {current_name} (standalone mode)")
            current.stop()
            self._running = False
            return

        if current != self._launcher:
            print(f"[framework] Returning to launcher (from {current_name})")
            current.stop()
            self._app_selector.select(self._launcher)
            self._launcher.start(self)

    # =========================================================================
    # MAIN EVENT LOOP
    # =========================================================================

    async def run(self):
        """
        The main event loop.

        This is the heart of the framework. It:
        1. Initializes the keyboard
        2. Starts the launcher
        3. Loops forever, polling keyboard and routing events

        The loop runs every 10ms (100 times per second).
        """
        # Initialize keyboard
        # MatrixKeyboard auto-detects hardware (Cardputer vs ADV)
        self._kb = MatrixKeyboard()
        kb = self._kb  # Local alias for convenience
        event = KeyEvent()

        # Start the launcher (or first app in standalone mode)
        if self._launcher:
            print("[framework] Starting launcher")
            self._app_selector.select(self._launcher)
            self._launcher.start(self)
        elif self._apps:
            # Standalone mode - start the first installed app
            app = self._apps[0]
            app_name = getattr(app, "name", type(app).__name__)
            print(f"[framework] Starting {app_name} (standalone mode)")
            self._app_selector.select(app)
            app.start(self)

        # Main event loop
        self._running = True
        while self._running:
            # Update M5Stack hardware (required for event processing)
            M5.update()

            # Poll keyboard for new key events
            kb.tick()

            # Check if a key was pressed
            if kb.is_pressed():
                # Get the key code and create event
                event.key = kb.get_key()
                event.status = False  # Reset handled status

                # Route to current app
                await self.handle_input(event)

            # Small delay to prevent busy-waiting
            # 10ms = 100 updates per second, very responsive
            await asyncio.sleep_ms(10)

    async def handle_input(self, event: KeyEvent):
        """
        Handle a keyboard event.

        Routes the event to the current app's _kb_event_handler.
        If the event is not handled and is ESC, returns to launcher.

        Parameters:
        -----------
        event : KeyEvent
            The keyboard event to handle
        """
        app = self._app_selector.current()

        # Let the app handle the event first
        if hasattr(app, "_kb_event_handler"):
            await app._kb_event_handler(event, self)

        # If not handled and ESC was pressed, return to launcher
        if event.status is False and event.key == KeyCode.KEYCODE_ESC:
            await self.return_to_launcher()
