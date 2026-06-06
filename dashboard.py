#!/usr/bin/env python3
# 🦅 Eagle Script Dashboard
# Logs dekho + InitData update karo

import os
import sys
import json
import time
import subprocess
import threading
from collections import deque
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# ===== STATE =====
bot_process = None
log_buffer = deque(maxlen=300)  # last 300 lines
bot_lock = threading.Lock()
CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except:
        return {"litebits_init": ""}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

def read_bot_output(proc):
    for line in iter(proc.stdout.readline, b''):
        decoded = line.decode('utf-8', errors='replace').rstrip()
        ts = time.strftime('%H:%M:%S')
        log_buffer.append(f"[{ts}] {decoded}")
    proc.stdout.close()

def start_bot():
    global bot_process
    config = load_config()
    init = config.get("litebits_init", "").strip()
    if not init:
        log_buffer.append("[DASHBOARD] ❌ InitData not set! Update it first.")
        return False

    env = os.environ.copy()
    env["LITEBITS_INIT"] = init
    env["PROXY"] = os.environ.get("PROXY", "http://kcartik:kcartik@chill-ki-mutt.kcartik-vps.tech:22425")

    bot_process = subprocess.Popen(
        [sys.executable, "litebits_bot.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env
    )
    log_buffer.append("[DASHBOARD] ✅ Bot started!")
    t = threading.Thread(target=read_bot_output, args=(bot_process,), daemon=True)
    t.start()
    return True

def stop_bot():
    global bot_process
    if bot_process and bot_process.poll() is None:
        bot_process.terminate()
        bot_process = None
        log_buffer.append("[DASHBOARD] 🛑 Bot stopped.")
        return True
    return False

def bot_status():
    if bot_process and bot_process.poll() is None:
        return "running"
    return "stopped"

# ===== HTML DASHBOARD =====
DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🦅 Eagle Script Dashboard</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

  :root {
    --bg: #0a0a0f;
    --panel: #111118;
    --border: #1e1e2e;
    --gold: #d4af37;
    --gold2: #f5cc50;
    --red: #8b0000;
    --green: #00c853;
    --text: #c9c9d4;
    --dim: #555570;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'JetBrains Mono', monospace;
    min-height: 100vh;
    padding: 20px;
  }

  .header {
    text-align: center;
    padding: 24px 0 20px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 24px;
  }

  .header h1 {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: var(--gold);
    letter-spacing: 2px;
  }

  .header p {
    color: var(--dim);
    font-size: 0.75rem;
    margin-top: 4px;
  }

  .grid {
    display: grid;
    grid-template-columns: 340px 1fr;
    gap: 16px;
    max-width: 1100px;
    margin: 0 auto;
  }

  @media (max-width: 768px) {
    .grid { grid-template-columns: 1fr; }
  }

  .panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
  }

  .panel-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--gold);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
  }

  /* STATUS */
  .status-dot {
    display: inline-block;
    width: 10px; height: 10px;
    border-radius: 50%;
    margin-right: 8px;
    animation: pulse 2s infinite;
  }
  .status-dot.running { background: var(--green); }
  .status-dot.stopped { background: #555; animation: none; }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
  }

  #status-text {
    font-size: 0.85rem;
    font-weight: 700;
  }

  /* BUTTONS */
  .btn-row {
    display: flex;
    gap: 10px;
    margin-top: 16px;
  }

  .btn {
    flex: 1;
    padding: 10px;
    border: none;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    font-weight: 700;
    cursor: pointer;
    transition: opacity 0.2s;
    letter-spacing: 1px;
  }
  .btn:hover { opacity: 0.85; }
  .btn:active { opacity: 0.7; }

  .btn-start { background: var(--green); color: #000; }
  .btn-stop  { background: var(--red); color: #fff; }

  /* INIT DATA */
  textarea {
    width: 100%;
    min-height: 100px;
    background: #0d0d14;
    border: 1px solid var(--border);
    border-radius: 6px;
    color: var(--text);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    padding: 10px;
    resize: vertical;
    margin-top: 8px;
    line-height: 1.5;
  }
  textarea:focus { outline: 1px solid var(--gold); }

  .btn-save {
    width: 100%;
    margin-top: 10px;
    background: var(--gold);
    color: #000;
  }

  #save-msg {
    font-size: 0.72rem;
    color: var(--green);
    margin-top: 6px;
    min-height: 18px;
    text-align: center;
  }

  /* LOGS */
  .log-box {
    background: #080810;
    border: 1px solid var(--border);
    border-radius: 6px;
    height: 420px;
    overflow-y: auto;
    padding: 12px;
    font-size: 0.72rem;
    line-height: 1.7;
  }

  .log-line { white-space: pre-wrap; word-break: break-all; }
  .log-line.reward { color: var(--gold2); font-weight: 700; }
  .log-line.error  { color: #ff4444; }
  .log-line.info   { color: var(--text); }
  .log-line.warn   { color: #ffaa00; }
  .log-line.dash   { color: var(--dim); }

  .log-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }

  .auto-scroll-label {
    font-size: 0.7rem;
    color: var(--dim);
    cursor: pointer;
    user-select: none;
  }

  .btn-clear {
    background: transparent;
    border: 1px solid var(--border);
    color: var(--dim);
    font-size: 0.65rem;
    padding: 3px 10px;
    border-radius: 4px;
    cursor: pointer;
    font-family: 'JetBrains Mono', monospace;
  }
  .btn-clear:hover { border-color: var(--gold); color: var(--gold); }
</style>
</head>
<body>

<div class="header">
  <h1>🦅 EAGLE SCRIPT DASHBOARD</h1>
  <p>LiteBits.io Bot Monitor</p>
</div>

<div class="grid">

  <!-- LEFT PANEL -->
  <div style="display:flex;flex-direction:column;gap:16px;">

    <div class="panel">
      <div class="panel-title">Bot Status</div>
      <div>
        <span class="status-dot stopped" id="status-dot"></span>
        <span id="status-text">Checking...</span>
      </div>
      <div class="btn-row">
        <button class="btn btn-start" onclick="botAction('start')">▶ START</button>
        <button class="btn btn-stop"  onclick="botAction('stop')">■ STOP</button>
      </div>
    </div>

    <div class="panel">
      <div class="panel-title">Init Data</div>
      <textarea id="init-input" placeholder="Paste Telegram InitData here..."></textarea>
      <button class="btn btn-save" onclick="saveInit()">💾 SAVE & APPLY</button>
      <div id="save-msg"></div>
    </div>

  </div>

  <!-- RIGHT PANEL: LOGS -->
  <div class="panel">
    <div class="panel-title">Live Logs</div>
    <div class="log-controls">
      <label class="auto-scroll-label">
        <input type="checkbox" id="auto-scroll" checked> Auto-scroll
      </label>
      <button class="btn-clear" onclick="clearLogs()">Clear</button>
    </div>
    <div class="log-box" id="log-box"></div>
  </div>

</div>

<script>
  let lastCount = 0;
  let localLogs = [];

  function colorLine(line) {
    const l = line.toLowerCase();
    if (l.includes('reward') || l.includes('stoshi') || l.includes('✨') || l.includes('💰')) return 'reward';
    if (l.includes('error') || l.includes('❌') || l.includes('failed')) return 'error';
    if (l.includes('warn') || l.includes('⚠️')) return 'warn';
    if (l.includes('[dashboard]')) return 'dash';
    return 'info';
  }

  function renderLogs() {
    const box = document.getElementById('log-box');
    box.innerHTML = localLogs.map(line =>
      `<div class="log-line ${colorLine(line)}">${escHtml(line)}</div>`
    ).join('');
    if (document.getElementById('auto-scroll').checked) {
      box.scrollTop = box.scrollHeight;
    }
  }

  function escHtml(str) {
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  function clearLogs() { localLogs = []; renderLogs(); }

  async function fetchLogs() {
    try {
      const r = await fetch(`/logs?since=${lastCount}`);
      const d = await r.json();
      if (d.lines && d.lines.length > 0) {
        localLogs = [...localLogs, ...d.lines].slice(-300);
        lastCount = d.total;
        renderLogs();
      }
    } catch(e) {}
  }

  async function fetchStatus() {
    try {
      const r = await fetch('/status');
      const d = await r.json();
      const dot = document.getElementById('status-dot');
      const txt = document.getElementById('status-text');
      if (d.status === 'running') {
        dot.className = 'status-dot running';
        txt.textContent = '🟢 RUNNING';
        txt.style.color = '#00c853';
      } else {
        dot.className = 'status-dot stopped';
        txt.textContent = '⚫ STOPPED';
        txt.style.color = '#555';
      }
    } catch(e) {}
  }

  async function botAction(action) {
    await fetch(`/bot/${action}`, {method:'POST'});
    setTimeout(fetchStatus, 500);
    setTimeout(fetchLogs, 800);
  }

  async function saveInit() {
    const val = document.getElementById('init-input').value.trim();
    if (!val) { document.getElementById('save-msg').textContent = '⚠️ Empty!'; return; }
    const r = await fetch('/config', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({litebits_init: val})
    });
    const d = await r.json();
    document.getElementById('save-msg').textContent = d.ok ? '✅ Saved!' : '❌ Error';
    setTimeout(() => document.getElementById('save-msg').textContent = '', 3000);
  }

  // Load saved init on page load
  async function loadSavedInit() {
    try {
      const r = await fetch('/config');
      const d = await r.json();
      if (d.litebits_init) {
        document.getElementById('init-input').value = d.litebits_init;
      }
    } catch(e) {}
  }

  loadSavedInit();
  fetchStatus();
  fetchLogs();
  setInterval(fetchLogs, 3000);
  setInterval(fetchStatus, 5000);
</script>
</body>
</html>"""

# ===== ROUTES =====

@app.route('/')
def index():
    return render_template_string(DASHBOARD_HTML)

@app.route('/status')
def status():
    return jsonify({"status": bot_status()})

@app.route('/logs')
def logs():
    since = int(request.args.get('since', 0))
    all_logs = list(log_buffer)
    total = len(all_logs)
    new_lines = all_logs[since:]
    return jsonify({"lines": new_lines, "total": total})

@app.route('/bot/start', methods=['POST'])
def bot_start():
    with bot_lock:
        if bot_status() == 'running':
            return jsonify({"ok": False, "msg": "Already running"})
        ok = start_bot()
    return jsonify({"ok": ok})

@app.route('/bot/stop', methods=['POST'])
def bot_stop():
    with bot_lock:
        ok = stop_bot()
    return jsonify({"ok": ok})

@app.route('/config', methods=['GET'])
def config_get():
    return jsonify(load_config())

@app.route('/config', methods=['POST'])
def config_post():
    data = request.get_json()
    if not data:
        return jsonify({"ok": False})
    config = load_config()
    config.update(data)
    save_config(config)
    return jsonify({"ok": True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    log_buffer.append("[DASHBOARD] 🦅 Eagle Script Dashboard started!")
    app.run(host='0.0.0.0', port=port)
  
