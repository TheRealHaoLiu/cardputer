# Implementation Tasks

## Phase 1: Project Structure

### 1.1 Create App Entry Point
- [ ] 1.1.1 Create `apps/webserver_demo.py` with AppBase structure
- [ ] 1.1.2 Create `apps/webserver_demo/` package directory
- [ ] 1.1.3 Create `apps/webserver_demo/__init__.py` with `create_app()` factory

### 1.2 WiFi Connection (in webserver_demo.py)
- [ ] 1.2.1 Load WiFi credentials from NVS (saved by Settings App)
- [ ] 1.2.2 Connect to WiFi in `on_launch()`
- [ ] 1.2.3 Display connection status and IP address on LCD
- [ ] 1.2.4 Handle connection failures gracefully

### 1.3 Server Lifecycle
- [ ] 1.3.1 Import and call `create_app()` in `on_ready()`
- [ ] 1.3.2 Start server as async task with `app.start_server()`
- [ ] 1.3.3 Stop server cleanly in `on_hide()`/`on_exit()`

## Phase 2: API Sub-Application

### 2.1 Create API Module
- [ ] 2.1.1 Create `apps/webserver_demo/api.py` with `Microdot()` instance
- [ ] 2.1.2 Implement `GET /info` returning device name/version
- [ ] 2.1.3 Implement `GET /system` returning memory, uptime

### 2.2 Speaker Control
- [ ] 2.2.1 Implement `POST /beep` accepting `{frequency, duration}` JSON
- [ ] 2.2.2 Implement `GET /tone/<frequency>` with URL parameter
- [ ] 2.2.3 Implement `GET /beep?freq=440&duration=500` with query params

### 2.3 Display Control
- [ ] 2.3.1 Implement `POST /message` to show text on LCD
- [ ] 2.3.2 Implement `GET /brightness` to get current level
- [ ] 2.3.3 Implement `POST /brightness` to set level

### 2.4 Mount API Sub-App
- [ ] 2.4.1 Import `api` in `__init__.py`
- [ ] 2.4.2 Mount with `app.mount(api, url_prefix='/api')`
- [ ] 2.4.3 Test `/api/info` from browser/curl

## Phase 3: Pages Sub-Application

### 3.1 Create Templates Module
- [ ] 3.1.1 Create `apps/webserver_demo/templates.py`
- [ ] 3.1.2 Define `INDEX_HTML` constant with control panel
- [ ] 3.1.3 Add buttons for beep, message input, brightness slider
- [ ] 3.1.4 Add JavaScript to call API endpoints

### 3.2 Create Pages Module
- [ ] 3.2.1 Create `apps/webserver_demo/pages.py` with `Microdot()` instance
- [ ] 3.2.2 Implement `GET /` returning `INDEX_HTML`
- [ ] 3.2.3 Implement `POST /message` form handler with redirect

### 3.3 Mount Pages Sub-App
- [ ] 3.3.1 Import `pages` in `__init__.py`
- [ ] 3.3.2 Mount with `app.mount(pages, url_prefix='')`
- [ ] 3.3.3 Test control panel in browser

## Phase 4: Middleware & Error Handling

### 4.1 Request Logging
- [ ] 4.1.1 Add `@app.before_request` in `__init__.py`
- [ ] 4.1.2 Log method, path, client IP to console

### 4.2 Error Handlers
- [ ] 4.2.1 Add `@app.errorhandler(404)` for custom 404 page
- [ ] 4.2.2 Add `@app.errorhandler(500)` for error handling
- [ ] 4.2.3 Return JSON errors for `/api/*`, HTML for others

### 4.3 Local Middleware (optional)
- [ ] 4.3.1 Demonstrate `app.mount(api, local=True)` for scoped handlers
- [ ] 4.3.2 Add API-specific error handling

## Phase 5: Documentation

### 5.1 Code Comments
- [ ] 5.1.1 Document `create_app()` factory pattern
- [ ] 5.1.2 Explain `app.mount()` and sub-applications
- [ ] 5.1.3 Document each API endpoint in docstrings
- [ ] 5.1.4 Add usage examples in module headers

### 5.2 API Reference
- [ ] 5.2.1 List all endpoints in `webserver_demo.py` header comment
- [ ] 5.2.2 Include curl examples for testing
