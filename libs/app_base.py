"""
App Base Classes for Cardputer Framework
=========================================

This module provides the base classes for building apps:
- AppSelector: Circular navigation through a list of apps
- AppBase: Base class with lifecycle methods for all apps

APP LIFECYCLE:
--------------
Apps go through these lifecycle stages, each with a corresponding method:

    install()           on_install()    When app is registered with framework
        │
        ▼
    start()  ─────────► on_launch()     When app is about to become active
        │               on_view()       Draw your UI here
        │               on_ready()      Starts the on_run() async task
        │                   │
        │                   ▼
        │               on_run()        Async loop running in background
        │                   │
        ▼                   │
    stop()  ◄───────────────┘
        │               on_hide()       Cancels the on_run() task
        │               on_exit()       Clean up resources
        ▼
    uninstall()         on_uninstall()  When app is removed from framework

KEYBOARD INPUT:
---------------
To handle keyboard input, implement _kb_event_handler() in your app:

    async def _kb_event_handler(self, event, fw):
        if event.key == ord('a'):
            # Do something when 'a' is pressed
            event.status = True  # Mark as handled
        # Don't handle ESC - let framework return to launcher

CREATING AN APP:
----------------
    class MyApp(AppBase):
        def __init__(self):
            super().__init__()
            self.name = "My App"  # Shown in launcher

        def on_view(self):
            # Draw your UI
            Lcd.fillScreen(Lcd.COLOR.BLACK)
            Lcd.print("Hello!")

        async def on_run(self):
            # Background task (optional)
            while True:
                await asyncio.sleep_ms(100)
"""

import asyncio

# =============================================================================
# APP SELECTOR CLASS
# =============================================================================


class AppSelector:
    """
    Circular navigation through a list of apps.

    Used by the framework to track which app is currently active
    and to navigate between apps.

    "Circular" means going past the end wraps to the beginning,
    and going before the beginning wraps to the end.
    """

    def __init__(self, apps: list) -> None:
        """
        Initialize with a reference to the apps list.

        Parameters:
        -----------
        apps : list
            The list of apps (will be modified as apps are installed)
        """
        self._apps = apps
        self._id = 0  # Index of currently selected app

    def prev(self):
        """
        Move to previous app (wraps around).

        Returns the newly selected app.
        """
        self._id = (self._id - 1) % len(self._apps)
        return self._apps[self._id]

    def next(self):
        """
        Move to next app (wraps around).

        Returns the newly selected app.
        """
        self._id = (self._id + 1) % len(self._apps)
        return self._apps[self._id]

    def current(self):
        """Get the currently selected app."""
        return self._apps[self._id]

    def select(self, app):
        """
        Select a specific app by reference.

        Parameters:
        -----------
        app : AppBase
            The app to select (must be in the list)
        """
        self._id = self._apps.index(app)

    def index(self, id):
        """
        Select app by index (wraps around).

        Returns the selected app.
        """
        self._id = id % len(self._apps)
        return self._apps[self._id]

    def current_index(self):
        """Get the index of the currently selected app."""
        return self._id


# =============================================================================
# APP BASE CLASS
# =============================================================================


class AppBase:
    """
    Base class for all framework apps.

    Subclass this and override lifecycle methods to create your app.
    The framework calls these methods at the appropriate times.

    IMPORTANT: Don't call lifecycle methods directly!
    Use the control methods: start(), pause(), resume(), stop()

    Attributes:
    -----------
    name : str
        Display name shown in the launcher. Set this in __init__.

    _task : asyncio.Task
        The background task running on_run(). Managed automatically.

    _fw : Framework
        Reference to the framework. Set automatically when started.
    """

    def __init__(self) -> None:
        """
        Initialize the app.

        Always call super().__init__() in your subclass!
        Then set self.name to your app's display name.
        """
        self._task = None  # Background task (created in on_ready)
        self._fw = None  # Framework reference (set by framework)
        self.name = "Unnamed App"  # Override this!

    # =========================================================================
    # LIFECYCLE METHODS - Override these in your app
    # =========================================================================

    def on_install(self):
        """
        Called when app is registered with framework.

        Override to perform one-time setup that should happen
        when the app is installed (before it's ever launched).

        Default: Does nothing.
        """
        pass

    def on_launch(self):
        """
        Called when app is about to become active.

        Override to perform setup that should happen each time
        the app is launched (before on_view and on_run).

        Example: Reset state, initialize variables.

        Default: Does nothing.
        """
        pass

    def on_view(self):
        """
        Called to set up the visual display.

        Override to draw your app's UI. This is called after
        on_launch() and before on_ready().

        Example:
            def on_view(self):
                Lcd.fillScreen(Lcd.COLOR.BLACK)
                Lcd.print("My App")

        Default: Does nothing.
        """
        pass

    def on_ready(self):
        """
        Called to start the async background task.

        This creates an asyncio task that runs on_run().
        Usually you don't need to override this - just override on_run().

        Default: Creates task running on_run().
        """
        self._task = asyncio.create_task(self.on_run())

    async def on_run(self):
        """
        Async background task that runs while app is active.

        Override this for:
        - Periodic updates (animations, sensor readings, timers)
        - Background processing
        - Waiting for events

        IMPORTANT:
        - This is an async function - use 'await'!
        - Use 'await asyncio.sleep_ms(n)' for delays
        - The task is cancelled when the app exits
        - If you don't need background work, just idle:

            async def on_run(self):
                while True:
                    await asyncio.sleep_ms(100)

        Default: Sleeps forever (does nothing).
        """
        while True:
            await asyncio.sleep_ms(500)

    def on_hide(self):
        """
        Called when app loses focus.

        Cancels the background task (on_run).
        Usually you don't need to override this.

        Default: Cancels the on_run task.
        """
        if self._task:
            self._task.cancel()
            self._task = None

    def on_exit(self):
        """
        Called when app is fully stopped.

        Override to clean up resources (close files, release hardware, etc.)

        Default: Does nothing.
        """
        pass

    def on_uninstall(self):
        """
        Called when app is removed from framework.

        Override for cleanup when app is uninstalled.
        Rarely needed.

        Default: Does nothing.
        """
        pass

    # =========================================================================
    # CONTROL METHODS - Framework calls these
    # =========================================================================
    # These methods orchestrate the lifecycle. They call the on_* methods
    # in the correct order. Don't override these unless you know what
    # you're doing!

    def install(self):
        """Register app with framework. Calls on_install()."""
        self.on_install()

    def start(self, fw=None):
        """
        Launch the app.

        Called by framework when app becomes active.
        Calls on_launch(), on_view(), on_ready() in sequence.

        Parameters:
        -----------
        fw : Framework
            The framework instance (stored for later use)
        """
        if fw is not None:
            self._fw = fw
        self.on_launch()
        self.on_view()
        self.on_ready()

    def pause(self):
        """Pause the app (hides but doesn't exit). Calls on_hide()."""
        self.on_hide()

    def resume(self):
        """Resume a paused app. Calls on_ready() to restart background task."""
        self.on_ready()

    def stop(self):
        """
        Fully stop the app.

        Called by framework when switching away from this app.
        Calls on_hide() then on_exit().
        """
        self.on_hide()
        self.on_exit()

    def uninstall(self):
        """Remove app from framework. Calls on_uninstall()."""
        self.on_uninstall()
