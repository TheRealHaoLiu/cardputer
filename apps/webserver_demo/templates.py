"""
HTML Templates
==============

HTML template constants for the web UI.
Keeping templates separate from routes for maintainability.
"""

INDEX_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cardputer Control</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e;
            color: #eee;
            padding: 20px;
            max-width: 600px;
            margin: 0 auto;
        }
        h1 { color: #00d4ff; margin-bottom: 20px; }
        h2 { color: #888; font-size: 14px; margin: 20px 0 10px; text-transform: uppercase; }
        .card {
            background: #16213e;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .row { display: flex; gap: 10px; margin-bottom: 10px; }
        input, button {
            padding: 10px 15px;
            border: none;
            border-radius: 5px;
            font-size: 14px;
        }
        input {
            background: #0f3460;
            color: #fff;
            flex: 1;
        }
        input::placeholder { color: #666; }
        button {
            background: #00d4ff;
            color: #1a1a2e;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover { background: #00b8e6; }
        button:active { transform: scale(0.98); }
        .btn-secondary { background: #e94560; }
        .btn-secondary:hover { background: #d63850; }
        .slider-container { display: flex; align-items: center; gap: 15px; }
        input[type="range"] {
            -webkit-appearance: none;
            background: #0f3460;
            height: 8px;
            border-radius: 4px;
        }
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 20px;
            height: 20px;
            background: #00d4ff;
            border-radius: 50%;
            cursor: pointer;
        }
        .value { min-width: 50px; text-align: center; font-weight: bold; }
        #status {
            position: fixed;
            bottom: 20px;
            left: 20px;
            right: 20px;
            background: #16213e;
            padding: 10px 15px;
            border-radius: 5px;
            text-align: center;
            display: none;
        }
        #status.show { display: block; }
        #status.success { border-left: 3px solid #00d4ff; }
        #status.error { border-left: 3px solid #e94560; }
        .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .info-item { background: #0f3460; padding: 10px; border-radius: 5px; }
        .info-label { color: #888; font-size: 12px; }
        .info-value { font-size: 18px; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Cardputer Control</h1>

    <h2>Device Info</h2>
    <div class="card">
        <div class="info-grid" id="info">
            <div class="info-item">
                <div class="info-label">Device</div>
                <div class="info-value" id="device-name">Loading...</div>
            </div>
            <div class="info-item">
                <div class="info-label">Free Memory</div>
                <div class="info-value" id="free-mem">--</div>
            </div>
        </div>
        <div class="row" style="margin-top: 10px;">
            <button onclick="refreshInfo()">Refresh Info</button>
        </div>
    </div>

    <h2>Speaker</h2>
    <div class="card">
        <div class="row">
            <input type="number" id="freq" placeholder="Frequency (Hz)" value="440">
            <input type="number" id="duration" placeholder="Duration (ms)" value="200">
        </div>
        <div class="row">
            <button onclick="playTone()">Play Tone</button>
            <button class="btn-secondary" onclick="playTone(880)">High Beep</button>
            <button class="btn-secondary" onclick="playTone(220)">Low Beep</button>
        </div>
    </div>

    <h2>Display</h2>
    <div class="card">
        <form id="message-form" onsubmit="sendMessage(event)">
            <div class="row">
                <input type="text" id="message" placeholder="Message to display" maxlength="20">
                <button type="submit">Send</button>
            </div>
        </form>
        <div class="slider-container" style="margin-top: 15px;">
            <span>Brightness</span>
            <input type="range" id="brightness" min="0" max="255" value="80" onchange="setBrightness(this.value)">
            <span class="value" id="brightness-value">80</span>
        </div>
    </div>

    <div id="status"></div>

    <script>
        function showStatus(message, isError) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'show ' + (isError ? 'error' : 'success');
            setTimeout(() => status.className = '', 2000);
        }

        async function api(method, path, data) {
            try {
                const opts = { method };
                if (data) {
                    opts.headers = {'Content-Type': 'application/json'};
                    opts.body = JSON.stringify(data);
                }
                const resp = await fetch('/api' + path, opts);
                const json = await resp.json();
                if (!resp.ok) throw new Error(json.error || 'Request failed');
                return json;
            } catch (e) {
                showStatus('Error: ' + e.message, true);
                throw e;
            }
        }

        async function refreshInfo() {
            try {
                const info = await api('GET', '/info');
                document.getElementById('device-name').textContent = info.device || 'Unknown';

                const sys = await api('GET', '/system');
                const freeMb = (sys.memory.free / 1024).toFixed(1);
                document.getElementById('free-mem').textContent = freeMb + ' KB';

                showStatus('Info refreshed');
            } catch (e) {}
        }

        async function playTone(freq) {
            freq = freq || parseInt(document.getElementById('freq').value) || 440;
            const duration = parseInt(document.getElementById('duration').value) || 200;
            try {
                await api('POST', '/beep', {frequency: freq, duration: duration});
                showStatus('Tone played: ' + freq + ' Hz');
            } catch (e) {}
        }

        async function sendMessage(e) {
            e.preventDefault();
            const text = document.getElementById('message').value;
            if (!text) return;
            try {
                await api('POST', '/message', {text: text});
                showStatus('Message sent');
                document.getElementById('message').value = '';
            } catch (e) {}
        }

        async function setBrightness(level) {
            document.getElementById('brightness-value').textContent = level;
            try {
                await api('POST', '/brightness', {level: parseInt(level)});
            } catch (e) {}
        }

        // Load info on page load
        refreshInfo();
    </script>
</body>
</html>
"""
