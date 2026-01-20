# Add Microdot Web Server Demo

## Why

The Cardputer ADV firmware includes Microdot, a Flask-like async web framework for MicroPython. A demo app would:
- Teach web server concepts on embedded devices
- Enable remote control of the Cardputer from any browser
- Demonstrate real-world IoT patterns (REST APIs, device control)
- Replace the planned simple "HTTP Demo" (task 2.4) with something more comprehensive

## What Changes

Create a modular web server demo using Microdot's official sub-application pattern:

```
apps/
├── webserver_demo.py              # AppBase entry point (lifecycle, WiFi, LCD)
└── webserver_demo/
    ├── __init__.py                # create_app() factory with mount()
    ├── api.py                     # Microdot() sub-app for /api/* routes
    ├── pages.py                   # Microdot() sub-app for HTML pages
    └── templates.py               # HTML constants (INDEX_HTML, etc.)
```

**Capabilities demonstrated:**
1. **Sub-applications** - `app.mount()` for modular route organization
2. **Web UI** - HTML control panel accessible from any browser
3. **REST API** - JSON endpoints for device info and control
4. **Form Handling** - Process user input from web forms
5. **Device Integration** - Control speaker, get system info via HTTP
6. **Middleware** - Request logging, error handling

**Why this structure:**
- Official Microdot pattern (simpler than Flask Blueprints)
- Scalable reference for future complex apps
- Routes portable - change mount point without editing sub-app
- Templates separate from logic

## Microdot Capabilities to Demonstrate

| Feature | Method | Example |
|---------|--------|---------|
| Sub-applications | `app.mount(subapp, url_prefix)` | Modular route organization |
| GET routes | `@app.get('/path')` | Serve pages, get data |
| POST routes | `@app.post('/path')` | Submit forms, control device |
| JSON response | `return {'key': 'value'}` | Auto-serialized |
| Request body | `request.json` | Parse JSON input |
| Query params | `request.args` | URL parameters |
| Form data | `request.form` | HTML form submission |
| Redirects | `redirect('/path')` | After form submit |
| Static files | `send_file('path')` | Serve HTML/CSS |
| Error handlers | `@app.errorhandler(404)` | Custom error pages |
| Middleware | `@app.before_request` | Logging, auth |
| URL params | `/users/<id>` | Dynamic routes |

## Dependencies

- WiFi connection (uses credentials from Settings App)
- Settings App must be implemented first for WiFi config

## Supersedes

This replaces task 2.4 "HTTP Demo" in `add-demo-apps` which was just a simple HTTP client. This is a server demo instead.
