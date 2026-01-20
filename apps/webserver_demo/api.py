"""
API Sub-Application
===================

REST API endpoints for device information and control.
All endpoints return JSON responses.

ENDPOINTS:
    GET  /info           - Device name and version
    GET  /system         - Memory and uptime stats
    POST /beep           - Play tone with JSON body
    GET  /tone/<freq>    - Play tone at frequency
    GET  /beep           - Play tone with query params
    POST /message        - Show text on LCD
    GET  /brightness     - Get current brightness
    POST /brightness     - Set brightness level
"""


def create_api():
    """Create and configure the API sub-application."""
    import gc
    import time

    from libs.microdot import Microdot

    api = Microdot()

    @api.get("/info")
    async def get_info(request):
        """Get device information."""
        return {
            "device": "M5Stack Cardputer",
            "firmware": "Cardputer ADV",
            "version": "1.0.0",
        }

    @api.get("/system")
    async def get_system(request):
        """Get system statistics."""
        gc.collect()
        free_mem = gc.mem_free()
        alloc_mem = gc.mem_alloc()

        return {
            "memory": {
                "free": free_mem,
                "allocated": alloc_mem,
                "total": free_mem + alloc_mem,
            },
            "uptime_ms": time.ticks_ms(),
        }

    @api.post("/beep")
    async def post_beep(request):
        """
        Play a tone.

        JSON body: {"frequency": 440, "duration": 200}
        """
        try:
            from M5 import Speaker

            data = request.json
            freq = data.get("frequency", 440)
            duration = data.get("duration", 200)

            Speaker.tone(freq, duration)

            return {"status": "ok", "frequency": freq, "duration": duration}
        except Exception as e:
            return {"error": str(e)}, 500

    @api.get("/tone/<freq>")
    async def get_tone(request, freq):
        """Play a tone at the specified frequency (URL parameter)."""
        try:
            from M5 import Speaker

            frequency = int(freq)
            duration = 200

            Speaker.tone(frequency, duration)

            return {"status": "ok", "frequency": frequency, "duration": duration}
        except ValueError:
            return {"error": "Invalid frequency"}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    @api.get("/beep")
    async def get_beep(request):
        """
        Play a tone using query parameters.

        Query params: ?freq=440&duration=500
        """
        try:
            from M5 import Speaker

            freq = int(request.args.get("freq", 440))
            duration = int(request.args.get("duration", 200))

            Speaker.tone(freq, duration)

            return {"status": "ok", "frequency": freq, "duration": duration}
        except ValueError:
            return {"error": "Invalid parameters"}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    @api.post("/message")
    async def post_message(request):
        """
        Display a message on the LCD.

        JSON body: {"text": "Hello World"}
        """
        try:
            from M5 import Lcd, Widgets

            data = request.json
            text = data.get("text", "")

            if not text:
                return {"error": "No text provided"}, 400

            # Draw message in center-ish area (avoid overwriting status)
            Lcd.setFont(Widgets.FONTS.ASCII7)
            Lcd.setTextSize(2)
            Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)

            # Clear message area
            Lcd.fillRect(10, 90, 220, 25, Lcd.COLOR.BLACK)
            Lcd.setCursor(10, 95)
            Lcd.print(text[:20])  # Limit length

            return {"status": "ok", "text": text[:20]}
        except Exception as e:
            return {"error": str(e)}, 500

    @api.get("/brightness")
    async def get_brightness(request):
        """Get current LCD brightness."""
        try:
            from M5 import Lcd

            # Note: Lcd.getBrightness() may not be available on all firmware
            # Return a placeholder if not available
            try:
                level = Lcd.getBrightness()
            except AttributeError:
                level = -1  # Unknown

            return {"brightness": level}
        except Exception as e:
            return {"error": str(e)}, 500

    @api.post("/brightness")
    async def post_brightness(request):
        """
        Set LCD brightness.

        JSON body: {"level": 80}  (0-255)
        """
        try:
            from M5 import Lcd

            data = request.json
            level = data.get("level", 80)

            # Clamp to valid range
            level = max(0, min(255, int(level)))

            Lcd.setBrightness(level)

            return {"status": "ok", "brightness": level}
        except Exception as e:
            return {"error": str(e)}, 500

    return api
