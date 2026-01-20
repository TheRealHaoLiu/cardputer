# Implementation Tasks

## Phase 1: Project Structure

### 1.1 Create App Entry Point
- [x] 1.1.1 Create `apps/webserver_demo_app.py` with AppBase structure
- [x] 1.1.2 Create `apps/webserver_demo/` package directory
- [x] 1.1.3 Create `apps/webserver_demo/__init__.py` with `create_app()` factory

### 1.2 WiFi Connection (in webserver_demo_app.py)
- [x] 1.2.1 Load WiFi credentials from NVS (saved by Settings App)
- [x] 1.2.2 Connect to WiFi in `on_view()`
- [x] 1.2.3 Display connection status and IP address on LCD
- [x] 1.2.4 Handle connection failures gracefully

### 1.3 Server Lifecycle
- [x] 1.3.1 Import and call `create_app()` in `on_run()`
- [x] 1.3.2 Start server as async task with `app.start_server()`
- [x] 1.3.3 Stop server cleanly in `on_hide()`/`on_exit()`

## Phase 2: API Sub-Application

### 2.1 Create API Module
- [x] 2.1.1 Create `apps/webserver_demo/api.py` with `create_api()` factory
- [x] 2.1.2 Implement `GET /info` returning device name/version
- [x] 2.1.3 Implement `GET /system` returning memory, uptime

### 2.2 Speaker Control
- [x] 2.2.1 Implement `POST /beep` accepting `{frequency, duration}` JSON
- [x] 2.2.2 Implement `GET /tone/<frequency>` with URL parameter
- [x] 2.2.3 Implement `GET /beep?freq=440&duration=500` with query params

### 2.3 Display Control
- [x] 2.3.1 Implement `POST /message` to show text on LCD
- [x] 2.3.2 Implement `GET /brightness` to get current level
- [x] 2.3.3 Implement `POST /brightness` to set level

### 2.4 Mount API Sub-App
- [x] 2.4.1 Import `create_api` in `__init__.py`
- [x] 2.4.2 Mount with `app.mount(api, url_prefix='/api')`
- [x] 2.4.3 Test `/api/info` from browser/curl

## Phase 3: Pages Sub-Application

### 3.1 Create Templates Module
- [x] 3.1.1 Create `apps/webserver_demo/templates.py`
- [x] 3.1.2 Define `INDEX_HTML` constant with control panel
- [x] 3.1.3 Add buttons for beep, message input, brightness slider
- [x] 3.1.4 Add JavaScript to call API endpoints

### 3.2 Create Pages Module
- [x] 3.2.1 Create `apps/webserver_demo/pages.py` with `create_pages()` factory
- [x] 3.2.2 Implement `GET /` returning `INDEX_HTML`
- [x] 3.2.3 Implement `POST /message` form handler with redirect

### 3.3 Mount Pages Sub-App
- [x] 3.3.1 Import `create_pages` in `__init__.py`
- [x] 3.3.2 Mount with `app.mount(pages, url_prefix='')`
- [x] 3.3.3 Test control panel in browser

## Phase 4: Middleware & Error Handling

### 4.1 Request Logging
- [x] 4.1.1 Add `@app.before_request` in `__init__.py`
- [x] 4.1.2 Log method, path, client IP to console

### 4.2 Error Handlers
- [x] 4.2.1 Add `@app.errorhandler(404)` for custom 404 page
- [x] 4.2.2 Add `@app.errorhandler(500)` for error handling
- [x] 4.2.3 Return JSON errors for `/api/*`, HTML for others

### 4.3 Local Middleware (optional)
- [x] 4.3.1 Demonstrate `app.mount(api, url_prefix)` pattern
- [x] 4.3.2 Add API-specific error handling

## Phase 5: Documentation

### 5.1 Code Comments
- [x] 5.1.1 Document `create_app()` factory pattern
- [x] 5.1.2 Explain `app.mount()` and sub-applications
- [x] 5.1.3 Document each API endpoint in docstrings
- [x] 5.1.4 Add usage examples in module headers

### 5.2 API Reference
- [x] 5.2.1 List all endpoints in `webserver_demo_app.py` header comment
- [x] 5.2.2 Include curl examples for testing

## Additional Work

### Vendored Dependencies
- [x] Add `libs/microdot.mpy` (compiled from microdot source)
- [x] Add ECONNABORTED (113) to muted socket errors
