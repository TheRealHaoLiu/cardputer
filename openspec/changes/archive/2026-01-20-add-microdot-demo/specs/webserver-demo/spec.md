# Web Server Demo App

Demonstrates the Microdot web framework capabilities on Cardputer ADV.

## ADDED Requirements

### Requirement: Modular Sub-Application Structure

The app SHALL use Microdot's sub-application pattern for modular code organization.

**File structure:**
```
apps/
├── webserver_demo.py              # AppBase entry point
└── webserver_demo/
    ├── __init__.py                # create_app() factory
    ├── api.py                     # API sub-application
    ├── pages.py                   # HTML pages sub-application
    └── templates.py               # HTML constants
```

- Uses `app.mount(subapp, url_prefix)` to compose routes
- Each sub-application is a standalone `Microdot()` instance
- Factory pattern with `create_app()` for testability

#### Scenario: Mount API sub-application
Given an `api.py` module with a `Microdot()` instance
When `create_app()` calls `app.mount(api, url_prefix='/api')`
Then routes defined in `api.py` are accessible at `/api/*`

#### Scenario: Mount pages sub-application
Given a `pages.py` module with HTML routes
When `create_app()` calls `app.mount(pages, url_prefix='')`
Then the root URL `/` serves the control panel HTML

---

### Requirement: Web Server Initialization

The app SHALL start a Microdot web server when WiFi is connected.

- Connects to WiFi using saved credentials from Settings App
- Displays IP address and port on LCD
- Server runs asynchronously alongside the app loop

#### Scenario: Start web server on WiFi connect
Given the user launches Web Server Demo
When WiFi credentials are saved in NVS
Then the app connects to WiFi
And starts Microdot server on port 5000
And displays the IP address on screen

#### Scenario: Handle missing WiFi credentials
Given no WiFi credentials are saved
When the user launches Web Server Demo
Then the app displays "No WiFi configured"
And prompts user to configure WiFi in Settings

---

### Requirement: REST API Endpoints

The app SHALL expose JSON API endpoints for device information and control.

**Endpoints:**
- `GET /api/info` - Returns device name and version
- `GET /api/system` - Returns memory, uptime, battery info
- `GET /api/wifi` - Returns WiFi connection info
- `POST /api/beep` - Plays a tone (accepts `{frequency, duration}`)
- `POST /api/message` - Displays text on LCD
- `GET /api/brightness` - Returns current brightness
- `POST /api/brightness` - Sets brightness level

#### Scenario: Get device info via API
Given the web server is running
When a client sends `GET /api/info`
Then the server returns JSON with device name and version

#### Scenario: Control speaker via API
Given the web server is running
When a client sends `POST /api/beep` with `{"frequency": 440, "duration": 200}`
Then the Cardputer plays a 440Hz tone for 200ms
And returns `{"status": "ok"}`

---

### Requirement: Web Control Panel

The app SHALL serve an HTML control panel at the root URL.

- Accessible from any browser on the same network
- Contains buttons and forms to control the device
- Shows live device status

#### Scenario: Access control panel from browser
Given the web server is running at 192.168.1.100:5000
When a user opens `http://192.168.1.100:5000/` in a browser
Then they see an HTML page with device controls

#### Scenario: Submit message via web form
Given the user is on the control panel
When they enter "Hello" in the message field and submit
Then the Cardputer LCD displays "Hello"
And the browser shows a success message

---

### Requirement: Request Middleware

The app SHALL demonstrate middleware patterns with before/after hooks.

#### Scenario: Log incoming requests
Given `@app.before_request` middleware is configured
When any HTTP request arrives
Then the request method and path are printed to console

---

### Requirement: Error Handling

The app SHALL provide custom error handlers for common HTTP errors.

#### Scenario: Handle 404 Not Found
Given a client requests a non-existent path
When the server processes the request
Then it returns a 404 response with a friendly message

#### Scenario: Handle internal errors
Given a route handler raises an exception
When the server catches the error
Then it returns a 500 response with error details (in debug mode)
