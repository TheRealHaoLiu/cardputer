"""
Pages Sub-Application
=====================

HTML page routes for the web UI.
Serves the control panel interface.

ROUTES:
    GET  /         - Main control panel
    POST /message  - Form handler for message submission (with redirect)
"""


def create_pages():
    """Create and configure the pages sub-application."""
    from libs.microdot import Microdot, redirect

    from apps.webserver_demo.templates import INDEX_HTML

    pages = Microdot()

    @pages.get("/")
    async def index(request):
        """Serve the main control panel page."""
        return INDEX_HTML, 200, {"Content-Type": "text/html"}

    @pages.post("/message")
    async def post_message_form(request):
        """
        Handle form submission for message display.

        This is for traditional form POSTs (not AJAX).
        Redirects back to the index page after processing.
        """
        try:
            from M5 import Lcd, Widgets

            # Get form data
            text = request.form.get("text", "")

            if text:
                # Draw message on LCD
                Lcd.setFont(Widgets.FONTS.ASCII7)
                Lcd.setTextSize(2)
                Lcd.setTextColor(Lcd.COLOR.YELLOW, Lcd.COLOR.BLACK)
                Lcd.fillRect(10, 90, 220, 25, Lcd.COLOR.BLACK)
                Lcd.setCursor(10, 95)
                Lcd.print(text[:20])

            # Redirect back to index
            return redirect("/")

        except Exception as e:
            print(f"[pages] Error: {e}")
            return redirect("/")

    return pages
