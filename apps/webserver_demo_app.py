"""
Web Server Demo - Microdot HTTP Server
=======================================

Demonstrates Microdot async web framework on the Cardputer.
Provides a REST API and web UI for device control.

FEATURES:
    - REST API at /api/* for JSON endpoints
    - Web UI at / for browser-based control
    - Device info, speaker control, display control

PREREQUISITES:
    - WiFi credentials saved via Settings App
    - Microdot library installed on device

API ENDPOINTS:
    GET  /api/info       - Device name and version
    GET  /api/system     - Memory and uptime stats
    POST /api/beep       - Play tone: {"frequency": 440, "duration": 200}
    GET  /api/tone/<freq> - Play tone at frequency
    GET  /api/beep?freq=440&duration=500 - Play tone with query params
    POST /api/message    - Show text: {"text": "Hello"}
    GET  /api/brightness - Get current brightness
    POST /api/brightness - Set brightness: {"level": 80}

CONTROLS:
    ESC = Exit to launcher

CURL EXAMPLES:
    curl http://<ip>/api/info
    curl http://<ip>/api/system
    curl -X POST http://<ip>/api/beep -H "Content-Type: application/json" -d '{"frequency":440,"duration":200}'
    curl -X POST http://<ip>/api/message -H "Content-Type: application/json" -d '{"text":"Hello"}'
"""

import asyncio
import sys

from M5 import Lcd, Widgets

# Path setup for imports (need parent of libs/ for "from libs.x" imports)
for lib_path in ["/flash", "/remote"]:
    if lib_path not in sys.path:
        sys.path.insert(0, lib_path)

from libs.app_base import AppBase


class WebServerDemo(AppBase):
    """
    Web server demo using Microdot.

    Connects to WiFi using saved credentials, then starts
    a Microdot web server for remote device control.
    """

    def __init__(self):
        super().__init__()
        self.name = "Web Server"
        self._wlan = None
        self._app = None
        self._server_task = None
        self._ip_address = None

    def _load_wifi_credentials(self):
        """Load saved WiFi credentials from NVS."""
        try:
            import esp32
            nvs = esp32.NVS("wifi")
            ssid_buf = bytearray(64)
            ssid_len = nvs.get_blob("ssid", ssid_buf)
            ssid = ssid_buf[:ssid_len].decode("utf-8") if ssid_len else None
            pwd_buf = bytearray(64)
            pwd_len = nvs.get_blob("password", pwd_buf)
            password = pwd_buf[:pwd_len].decode("utf-8") if pwd_len else ""
            return ssid, password
        except Exception as e:
            print(f"[webserver] No saved credentials: {e}")
            return None, None

    def _connect_wifi(self):
        """Connect to WiFi using saved credentials."""
        import network
        import time

        ssid, password = self._load_wifi_credentials()
        if not ssid:
            return False, "No WiFi credentials saved"

        self._wlan = network.WLAN(network.STA_IF)
        self._wlan.active(True)

        if self._wlan.isconnected():
            self._ip_address = self._wlan.ifconfig()[0]
            return True, f"Already connected: {self._ip_address}"

        print(f"[webserver] Connecting to {ssid}...")
        self._wlan.connect(ssid, password)

        # Wait for connection (up to 10 seconds)
        for _ in range(100):
            if self._wlan.isconnected():
                self._ip_address = self._wlan.ifconfig()[0]
                return True, f"Connected: {self._ip_address}"
            time.sleep_ms(100)

        return False, "Connection timeout"

    def on_launch(self):
        """Connect to WiFi when app launches."""
        print("[webserver] Launching...")

    def on_view(self):
        """Draw the UI and attempt WiFi connection."""
        Lcd.fillScreen(Lcd.COLOR.BLACK)
        Lcd.setFont(Widgets.FONTS.ASCII7)
        Lcd.setTextSize(1)

        # Title
        Lcd.setTextColor(Lcd.COLOR.CYAN, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 5)
        Lcd.print("Web Server Demo")

        # Status
        Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 25)
        Lcd.print("Connecting to WiFi...")

        # Connect to WiFi
        success, message = self._connect_wifi()

        # Clear status area
        Lcd.fillRect(10, 25, 220, 100, Lcd.COLOR.BLACK)

        if success:
            Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
            Lcd.setCursor(10, 25)
            Lcd.print("WiFi Connected!")

            Lcd.setTextColor(Lcd.COLOR.WHITE, Lcd.COLOR.BLACK)
            Lcd.setCursor(10, 40)
            Lcd.print(f"IP: {self._ip_address}")

            Lcd.setCursor(10, 55)
            Lcd.print("Starting server...")
        else:
            Lcd.setTextColor(Lcd.COLOR.RED, Lcd.COLOR.BLACK)
            Lcd.setCursor(10, 25)
            Lcd.print("WiFi Failed!")
            Lcd.setCursor(10, 40)
            Lcd.print(message)
            Lcd.setCursor(10, 60)
            Lcd.print("Configure WiFi in Settings")

        # Footer
        Lcd.setTextColor(Lcd.COLOR.DARKGREY, Lcd.COLOR.BLACK)
        Lcd.setCursor(10, 125)
        Lcd.print("ESC = Exit")

    async def on_run(self):
        """Start the web server and run main loop."""
        if not self._ip_address:
            # No WiFi, just idle
            while True:
                await asyncio.sleep_ms(100)
            return

        # Import and create the Microdot app
        try:
            from apps.webserver_demo import create_app
            self._app = create_app()

            # Update display
            Lcd.fillRect(10, 55, 220, 15, Lcd.COLOR.BLACK)
            Lcd.setTextColor(Lcd.COLOR.GREEN, Lcd.COLOR.BLACK)
            Lcd.setCursor(10, 55)
            Lcd.print("Server running on port 80")

            Lcd.setCursor(10, 75)
            Lcd.print(f"http://{self._ip_address}/")

            print(f"[webserver] Starting server at http://{self._ip_address}/")

            # Start server (this blocks until server stops)
            await self._app.start_server(port=80, debug=True)

        except ImportError as e:
            print(f"[webserver] Import error: {e}")
            Lcd.fillRect(10, 55, 220, 30, Lcd.COLOR.BLACK)
            Lcd.setTextColor(Lcd.COLOR.RED, Lcd.COLOR.BLACK)
            Lcd.setCursor(10, 55)
            Lcd.print("Microdot not installed!")
        except Exception as e:
            print(f"[webserver] Server error: {e}")
            Lcd.fillRect(10, 55, 220, 30, Lcd.COLOR.BLACK)
            Lcd.setTextColor(Lcd.COLOR.RED, Lcd.COLOR.BLACK)
            Lcd.setCursor(10, 55)
            Lcd.print(f"Error: {e}")

    def on_hide(self):
        """Stop the server when hiding."""
        self._stop_server()

    def on_exit(self):
        """Clean up when exiting."""
        self._stop_server()

    def _stop_server(self):
        """Stop the Microdot server."""
        if self._app:
            try:
                self._app.shutdown()
                print("[webserver] Server stopped")
            except Exception as e:
                print(f"[webserver] Error stopping server: {e}")
            self._app = None


# Export for framework discovery
App = WebServerDemo

# Allow direct execution
if __name__ == "__main__":
    import M5

    M5.begin()
    Lcd.setRotation(1)
    Lcd.setBrightness(80)

    from libs.framework import Framework

    fw = Framework()
    fw.install(WebServerDemo())
    fw.start()
