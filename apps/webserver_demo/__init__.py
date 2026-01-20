"""
Web Server Demo Package
=======================

Microdot web application using the sub-application pattern.

STRUCTURE:
    __init__.py   - create_app() factory, mounts sub-apps
    api.py        - REST API sub-app (/api/*)
    pages.py      - HTML pages sub-app (/)
    templates.py  - HTML template constants

USAGE:
    from apps.webserver_demo import create_app
    app = create_app()
    await app.start_server(port=80)

INSTALLING MICRODOT:
    Via mpremote: mpremote mip install microdot
    Or manually copy microdot.py to /flash/lib/
"""


def create_app():
    """
    Create and configure the Microdot application.

    Returns a Microdot app with all sub-applications mounted
    and middleware configured.

    Raises ImportError if microdot is not installed.
    """
    from libs.microdot import Microdot

    app = Microdot()

    # Import sub-applications (deferred to avoid import errors at discovery)
    from apps.webserver_demo.api import create_api
    from apps.webserver_demo.pages import create_pages

    api = create_api()
    pages = create_pages()

    # Request logging middleware
    @app.before_request
    async def log_request(request):
        client_ip = request.client_addr[0] if request.client_addr else "unknown"
        print(f"[http] {request.method} {request.path} from {client_ip}")

    # Error handlers
    @app.errorhandler(404)
    async def not_found(request):
        if request.path.startswith("/api/"):
            return {"error": "Not found", "path": request.path}, 404
        return "<h1>404 Not Found</h1><p>Page not found.</p>", 404

    @app.errorhandler(500)
    async def server_error(request):
        if request.path.startswith("/api/"):
            return {"error": "Internal server error"}, 500
        return "<h1>500 Internal Server Error</h1>", 500

    # Mount sub-applications
    # API endpoints at /api/*
    app.mount(api, url_prefix="/api")

    # HTML pages at root
    app.mount(pages, url_prefix="")

    print("[webserver] App created with api and pages sub-apps")
    return app
