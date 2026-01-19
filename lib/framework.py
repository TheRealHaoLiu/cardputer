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
    from lib.framework import Framework
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
import os
import sys

import M5
from hardware import MatrixKeyboard

from lib import app_base

# Try to import KeyCode constants from firmware
# Fall back to our own definitions if not available
try:
    from unit import KeyCode
except ImportError:

    class KeyCode:
        """Key code constants for special keys."""

        KEYCODE_ESC = 0x1B  # Escape key
        KEYCODE_ENTER = 0x0D  # Enter/Return key
        KEYCODE_LEFT = 0x25  # Left arrow (if available)
        KEYCODE_UP = 0x26  # Up arrow
        KEYCODE_RIGHT = 0x27  # Right arrow (if available)
        KEYCODE_DOWN = 0x28  # Down arrow


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
        self._apps = []  # List of installed apps
        self._app_selector = app_base.AppSelector(self._apps)
        self._launcher = None  # Special app that ESC returns to
        self._running = False  # Controls main event loop
        self._discovered_modules = set()  # Track loaded modules

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

    # =========================================================================
    # APP DISCOVERY
    # =========================================================================

    def discover_apps(self):
        """Scan apps directory and load/reload app modules."""
        print(f"[discover] Scanning {self._apps_dir} (remote={self._is_remote})")

        for entry in os.ilistdir(self._apps_dir):
            filename = entry[0]
            if (
                not filename.endswith(".py")
                or filename.startswith("_")
                or filename == "launcher.py"
            ):
                continue

            module_name = filename[:-3]

            # In remote mode, force reload for hot-reloading
            if self._is_remote and module_name in sys.modules:
                print(f"[discover] Reloading {module_name}")
                del sys.modules[module_name]

            # Skip if already discovered (flash mode only)
            if not self._is_remote and module_name in self._discovered_modules:
                print(f"[discover] Skipping {module_name} (already discovered)")
                continue

            try:
                module = __import__(module_name)
                self._discovered_modules.add(module_name)

                app_class = self._find_app_class(module)
                if app_class:
                    # Find existing app with same class name
                    existing_idx = None
                    for i, app in enumerate(self._apps):
                        if type(app).__name__ == app_class.__name__:
                            existing_idx = i
                            break

                    if existing_idx is not None:
                        # In remote mode, replace with new instance for hot-reload
                        if self._is_remote:
                            new_app = app_class()
                            new_app.install()
                            self._apps[existing_idx] = new_app
                            print(f"[discover] Replaced {app_class.__name__}")
                    else:
                        # New app, install it
                        self.install(app_class())
                        print(f"[discover] Installed {app_class.__name__}")
                else:
                    print(f"[discover] No AppBase subclass in {filename}")
            except Exception as e:
                print(f"[discover] Failed to load {filename}: {e}")

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
        kb = MatrixKeyboard()
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
