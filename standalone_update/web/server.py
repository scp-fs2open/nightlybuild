#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import threading
import shutil
from datetime import datetime, timedelta

import requests as http_requests
from flask import Flask, make_response, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, join_room
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash

from env_parser import parse_env_default, parse_env, write_env, merge_variables

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
csrf = CSRFProtect(app)
socketio = SocketIO(app, async_mode='gevent')

app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

_secure_cookies = os.environ.get('SECURE_COOKIES', '0').lower() in ('1', 'true', 'yes')
app.config['REMEMBER_COOKIE_SECURE'] = _secure_cookies
app.config['SESSION_COOKIE_SECURE'] = _secure_cookies

APP_TITLE = 'FSO Standalone Update Manager'
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1 MB

app.jinja_env.filters['basename'] = os.path.basename
app.jinja_env.globals['APP_TITLE'] = APP_TITLE


@app.context_processor
def inject_engine_webui_flag():
    """Make engine_webui_available accessible in all templates."""
    return {'engine_webui_available': parse_multi_cfg_webapi() is not None}

login_manager = LoginManager(app)
login_manager.login_view = 'login'

PASSWORD_HASH = os.environ.get('PASSWORD_HASH', '')


class User(UserMixin):
    id = '1'


_user = User()


@login_manager.user_loader
def load_user(user_id):
    return _user if user_id == '1' else None

# Paths — .env.default and .env live one directory up from this script
SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ENV_DEFAULT_PATH = os.path.join(SCRIPT_DIR, '.env.default')
ENV_PATH = os.path.join(SCRIPT_DIR, '.env')
UPDATE_SCRIPT = os.path.join(SCRIPT_DIR, 'update')

# Web app configuration via environment variables
HOST = os.environ.get('WEB_HOST', '127.0.0.1')
PORT = int(os.environ.get('WEB_PORT', '5000'))
LOG_PATH = os.environ.get('UPDATE_LOG_PATH', '')
LOG_LINES = int(os.environ.get('LOG_LINES', '100'))

# Process tracking
_running_process = None
_running_action = None       # 'rebuilding', 'updating', 'restarting', or 'stopping'
_running_action_base = None  # 'rebuild', 'update', 'restart', or 'stop'
_log_file = None


def get_status():
    """Return (status_string, is_running) for the current update process."""
    global _running_process, _running_action, _running_action_base, _log_file
    global _last_emitted_status
    if _running_process is not None:
        exit_code = _running_process.poll()
        if exit_code is None:
            return (_running_action, True)
        # Process finished — close the log handle, then append footer
        if _log_file is not None:
            _log_file.close()
            _log_file = None
        if LOG_PATH:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            footer = (f'=== Web UI: {_running_action_base} completed at {timestamp} ===\n' if exit_code == 0
                      else f'=== Web UI: {_running_action_base} failed (exit code {exit_code}) at {timestamp} ===\n')
            with open(LOG_PATH, 'a') as f:
                f.write(footer)
        _running_process = None
        _running_action = None
        _running_action_base = None
        # Immediately notify clients of completion
        _last_emitted_status = 'idle'
        socketio.emit('build_status', {'status': 'idle', 'is_running': False}, to='page:server')
        # Push updated build info (may have changed after rebuild or mod update)
        build_info = read_build_info()
        socketio.emit('build_info', {'info': build_info}, to='page:server')
    return ('idle', False)


def start_update(restart_only=False, stop_only=False, update_mods_only=False):
    """Start the update script in the background. Returns True on success."""
    global _running_process, _running_action, _running_action_base, _log_file
    if not LOG_PATH:
        return False
    status, is_running = get_status()
    if is_running:
        return False

    if stop_only:
        action, flag, running_label = 'stop', '-S', 'stopping'
    elif update_mods_only:
        action, flag, running_label = 'update', '-U', 'updating'
    elif restart_only:
        action, flag, running_label = 'restart', '-R', 'restarting'
    else:
        action, flag, running_label = 'rebuild', None, 'rebuilding'

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    header = f'=== Web UI: {action} triggered at {timestamp} ===\n'

    _log_file = open(LOG_PATH, 'w')
    _log_file.write(header)
    _log_file.flush()

    # Notify clients the log was truncated and reset the watcher to the start
    socketio.emit('update_log_truncated', to='page:server')
    _sync_watcher_to_offset(LOG_PATH, 0)

    cmd = [UPDATE_SCRIPT]
    if flag:
        cmd.append(flag)

    _running_process = subprocess.Popen(
        cmd, stdout=_log_file, stderr=subprocess.STDOUT,
        cwd=SCRIPT_DIR
    )
    _running_action = running_label
    _running_action_base = action
    # Immediately notify clients of new status
    _last_emitted_status = running_label
    socketio.emit('build_status', {'status': running_label, 'is_running': True}, to='page:server')
    return True


def get_fso_data_dir():
    if sys.platform == 'darwin':
        return os.path.expanduser(
            '~/Library/Application Support/HardLightProductions/FreeSpaceOpen')
    else:
        xdg = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
        return os.path.join(xdg, 'HardLightProductions', 'FreeSpaceOpen')


def get_fso_data_file(filename):
    """Return the path to a file in the FSO data dir, respecting MOD_DIRNAME."""
    fso_data = get_fso_data_dir()
    mod_dirname = parse_env(ENV_PATH).get('MOD_DIRNAME', '').split(',')[0]
    if mod_dirname:
        return os.path.join(fso_data, mod_dirname, 'data', filename)
    return os.path.join(fso_data, 'data', filename)


def parse_multi_cfg_webapi():
    """Parse multi.cfg for engine web API settings.

    Returns a dict with 'port', 'username', and 'password' if the web API
    appears to be configured (i.e. +webui_root is set), or None otherwise.
    """
    cfg_path = get_fso_data_file('multi.cfg')
    if not os.path.exists(cfg_path):
        return None

    settings = {}
    try:
        with open(cfg_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith('+webapi_server_port'):
                    parts = line.split(None, 1)
                    if len(parts) == 2:
                        try:
                            settings['port'] = int(parts[1])
                        except ValueError:
                            pass
                elif line.startswith('+webapi_username'):
                    parts = line.split(None, 1)
                    if len(parts) == 2:
                        settings['username'] = parts[1]
                elif line.startswith('+webapi_password'):
                    parts = line.split(None, 1)
                    if len(parts) == 2:
                        settings['password'] = parts[1]
                elif line.startswith('+webui_root'):
                    parts = line.split(None, 1)
                    if len(parts) == 2:
                        settings['webui_root'] = parts[1]
    except OSError:
        return None

    # Only expose the proxy when the engine web API is configured
    if 'webui_root' not in settings:
        return None

    # Apply engine defaults for any missing values
    settings.setdefault('port', 8080)
    settings.setdefault('username', 'admin')
    settings.setdefault('password', 'admin')
    return settings


def get_log_panels():
    fso_data = get_fso_data_dir()
    return [
        {'id': 'standalone', 'name': 'FSO Standalone Log',
         'path': os.path.join(fso_data, 'data', 'fs2_standalone.log')},
        {'id': 'multi', 'name': 'Multi Log',
         'path': get_fso_data_file('multi.log')},
    ]


# --- WebSocket file watcher (polling loop + rooms) ---

_watch_state = {}       # realpath -> {'offset': int, 'inode': int}
_watch_lock = threading.Lock()
_last_emitted_status = None
_last_engine_running = None  # Track engine running state for change detection
_watcher_started = False

# Registry of files to watch: realpath -> {line_event, truncate_event, room}
_watch_registry = {}

# Track room occupancy so the watcher skips emitting (and advancing offsets)
# when no clients are listening — prevents lost lines during SSR-to-WS handoff.
_room_occupancy = {}


def _check_and_emit_file(filepath, line_event, truncate_event, room):
    """Read new lines from a file since last check; detect truncation/rotation."""
    if not filepath or not os.path.exists(filepath):
        return

    # Don't read or advance offset if no one is in the room — data would be
    # lost since emit goes nowhere but offset still advances past it.
    if _room_occupancy.get(room, 0) <= 0:
        return

    with _watch_lock:
        state = _watch_state.get(filepath)
        try:
            stat = os.stat(filepath)
        except OSError:
            return

        current_size = stat.st_size
        current_inode = stat.st_ino

        if state is None:
            # First time seeing this file — set offset to end (SSR already delivered content)
            _watch_state[filepath] = {'offset': current_size, 'inode': current_inode}
            return

        # Detect truncation or rotation
        if current_size < state['offset'] or current_inode != state['inode']:
            state['offset'] = 0
            state['inode'] = current_inode
            socketio.emit(truncate_event, to=room)

        if current_size == state['offset']:
            return

        # Read new content (cap at 256 KB to avoid memory spikes)
        max_chunk = 256 * 1024
        read_from = max(state['offset'], current_size - max_chunk) if current_size - state['offset'] > max_chunk else state['offset']
        try:
            with open(filepath, 'r') as f:
                f.seek(read_from)
                new_data = f.read()
            state['offset'] = current_size
        except OSError:
            return

    # Emit outside the lock
    if new_data:
        socketio.emit(line_event, {'data': new_data}, to=room)


def _check_and_emit_status():
    """Emit build status changes to clients on the server page."""
    global _last_emitted_status
    status, is_running = get_status()
    if status != _last_emitted_status:
        _last_emitted_status = status
        socketio.emit('build_status', {'status': status, 'is_running': is_running}, to='page:server')


def _check_and_emit_engine_status():
    """Poll for game engine process and emit changes to all connected pages."""
    global _last_engine_running
    running = is_engine_running()
    if running != _last_engine_running:
        _last_engine_running = running
        payload = {'running': running}
        socketio.emit('engine_status', payload, to='page:server')
        socketio.emit('engine_status', payload, to='page:logs')


def _file_watcher():
    """Background greenlet that polls log files and build status for changes."""
    while True:
        socketio.sleep(0.25)
        _check_and_emit_status()
        _check_and_emit_engine_status()
        for filepath, reg in _watch_registry.items():
            _check_and_emit_file(filepath, reg['line_event'], reg['truncate_event'], reg['room'])


def _start_watcher():
    """Register watched files and start the polling loop."""
    global _watcher_started
    with _watch_lock:
        if _watcher_started:
            return
        _watcher_started = True

    if LOG_PATH:
        real_path = os.path.realpath(LOG_PATH)
        _watch_registry[real_path] = {
            'line_event': 'update_log_lines',
            'truncate_event': 'update_log_truncated',
            'room': 'page:server',
        }

    for panel in get_log_panels():
        real_path = os.path.realpath(panel['path'])
        _watch_registry[real_path] = {
            'line_event': f'game_log_lines_{panel["id"]}',
            'truncate_event': f'game_log_truncated_{panel["id"]}',
            'room': 'page:logs',
        }

    socketio.start_background_task(_file_watcher)


@socketio.on('connect')
def handle_connect():
    if not current_user.is_authenticated:
        return False


_client_rooms = {}  # sid -> room


@socketio.on('join_page')
def handle_join_page(page):
    if page not in ('server', 'logs'):
        return

    room = f'page:{page}'
    join_room(room)
    _room_occupancy[room] = _room_occupancy.get(room, 0) + 1
    _client_rooms[request.sid] = room

    # Send current engine status so the client is never stale
    running = is_engine_running()
    socketio.emit('engine_status', {'running': running}, to=request.sid)

    if page == 'logs':
        # One-time lsof check: tell the client which log files the engine has open
        panels_active = {}
        for panel in get_log_panels():
            panels_active[panel['id']] = is_log_open_by_engine(panel['path'])
        socketio.emit('log_file_active', {'panels': panels_active}, to=request.sid)

    if page == 'server':
        # Send current build status so the client is never stale
        status, is_running = get_status()
        socketio.emit('build_status',
                      {'status': status, 'is_running': is_running},
                      to=request.sid)


@socketio.on('server_action')
def handle_server_action(data):
    action = data.get('action', '') if isinstance(data, dict) else data
    if action not in ('rebuild', 'update', 'restart', 'stop'):
        return {'ok': False, 'error': 'Invalid action.'}
    if not LOG_PATH:
        return {'ok': False, 'error': 'UPDATE_LOG_PATH is not configured.'}
    kwargs = {}
    if action == 'update':
        kwargs['update_mods_only'] = True
    elif action == 'restart':
        kwargs['restart_only'] = True
    elif action == 'stop':
        kwargs['stop_only'] = True
    if not start_update(**kwargs):
        return {'ok': False, 'error': 'An update is already in progress.'}
    return {'ok': True}


@socketio.on('disconnect')
def handle_disconnect():
    room = _client_rooms.pop(request.sid, None)
    if room:
        _room_occupancy[room] = max(0, _room_occupancy.get(room, 0) - 1)


@app.after_request
def _no_cache(response):
    response.headers['Cache-Control'] = 'no-store'
    return response


@app.before_request
def _ensure_watcher():
    if not _watcher_started:
        _start_watcher()


def _sync_watcher_to_offset(filepath, offset):
    """Set the watcher's file position so it picks up only content added after this point."""
    filepath = os.path.realpath(filepath)
    try:
        inode = os.stat(filepath).st_ino
    except OSError:
        return
    with _watch_lock:
        _watch_state[filepath] = {'offset': offset, 'inode': inode}


def _get_game_root():
    """Resolve GAME_ROOT from .env override or .env.default."""
    overrides = parse_env(ENV_PATH)
    if 'GAME_ROOT' in overrides:
        return overrides['GAME_ROOT']
    for var in parse_env_default(ENV_DEFAULT_PATH):
        if var.name == 'GAME_ROOT' and var.default_value:
            return var.default_value
    return ''


def read_build_info():
    """Read build_info.json from GAME_ROOT. Returns dict or None."""
    game_root = _get_game_root()
    if not game_root:
        return None
    path = os.path.join(game_root, 'build_info.json')
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _get_engine_process_name():
    """Determine the process name to look for (fs2_open, or debugger if USE_DEBUGGER is set)."""
    overrides = parse_env(ENV_PATH)
    use_debugger = overrides.get('USE_DEBUGGER', '')
    if not use_debugger:
        # Check .env.default — USE_DEBUGGER is commented out by default,
        # so parse_env_default won't return a value unless it's uncommented
        for var in parse_env_default(ENV_DEFAULT_PATH):
            if var.name == 'USE_DEBUGGER' and var.default_value:
                use_debugger = var.default_value
                break
    if use_debugger:
        return 'lldb' if sys.platform == 'darwin' else 'gdb'
    return 'fs2_open'


def is_engine_running():
    """Check whether the game engine process is currently running."""
    process_name = _get_engine_process_name()
    pgrep = shutil.which('pgrep')
    if not pgrep:
        return None  # Can't determine
    try:
        result = subprocess.run(
            [pgrep, process_name],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    except OSError:
        return None


def is_log_open_by_engine(filepath):
    """Check whether the engine process currently has a specific log file open."""
    if not filepath or not os.path.exists(filepath):
        return False
    process_name = _get_engine_process_name()
    lsof = shutil.which('lsof')
    if not lsof:
        return None  # Can't determine
    try:
        result = subprocess.run(
            [lsof, '-c', process_name, '--', filepath],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    except OSError:
        return None


def read_log_lines():
    """Read the last LOG_LINES from the log file. Returns (lines, error, offset)."""
    if not LOG_PATH:
        return (None, 'UPDATE_LOG_PATH is not configured.', 0)
    if not os.path.exists(LOG_PATH):
        return (None, f'Log file not found: {LOG_PATH}', 0)
    with open(LOG_PATH) as f:
        all_lines = f.readlines()
        offset = f.tell()
        return (all_lines[-LOG_LINES:], None, offset)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if PASSWORD_HASH and check_password_hash(PASSWORD_HASH, password):
            login_user(_user, remember=True)
            next_url = request.args.get('next', '')
            if not next_url or not next_url.startswith('/'):
                next_url = url_for('build_config')
            return redirect(next_url)
        flash('Invalid password.', 'error')
    return render_template('login.html')


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
def index():
    return redirect(url_for('build_config'))


@app.route('/build-config', methods=['GET'])
@login_required
def build_config():
    variables = parse_env_default(ENV_DEFAULT_PATH)
    overrides = parse_env(ENV_PATH)
    sections = merge_variables(variables, overrides)
    return render_template('config.html', sections=sections)


@app.route('/build-config', methods=['POST'])
@login_required
def build_config_save():
    variables = parse_env_default(ENV_DEFAULT_PATH)
    overrides = {}

    for var in variables:
        is_overridden = request.form.get(f'override_{var.name}') == 'on'
        value = request.form.get(f'value_{var.name}', '').strip()
        if is_overridden and value:
            overrides[var.name] = value

    mod = overrides.get('MOD_DIRNAME', '')
    if mod:
        for segment in mod.split(','):
            if not segment or '/' in segment or '..' in segment:
                flash('Each mod in MOD_DIRNAME must be a plain directory name '
                      '(no slashes, "..", or empty segments).', 'error')
                return redirect(url_for('build_config'))

    vcs = overrides.get('MOD_VCS', '')
    if vcs:
        for segment in vcs.split(','):
            if segment not in ('', 'git', 'svn'):
                flash('Each VCS in MOD_VCS must be "git", "svn", or empty.', 'error')
                return redirect(url_for('build_config'))

    write_env(ENV_PATH, overrides)
    flash('Configuration saved.', 'success')
    return redirect(url_for('build_config'))


@app.route('/build-controls')
@login_required
def build_controls():
    status, is_running = get_status()
    lines, log_error, offset = read_log_lines()
    if LOG_PATH and offset:
        _sync_watcher_to_offset(LOG_PATH, offset)
    build_info = read_build_info()
    return render_template('server.html', status=status, is_running=is_running,
                           lines=lines, log_path=LOG_PATH, log_error=log_error,
                           build_info=build_info)


@app.route('/game-config', methods=['GET'])
@login_required
def game_config():
    cfg_path = get_fso_data_file('multi.cfg')
    content = ''
    exists = os.path.exists(cfg_path)
    if exists:
        with open(cfg_path) as f:
            content = f.read()
    return render_template('multicfg.html', content=content, cfg_path=cfg_path,
                           exists=exists)


@app.route('/game-config', methods=['POST'])
@login_required
def game_config_save():
    cfg_path = get_fso_data_file('multi.cfg')
    content = request.form.get('content', '')
    # Normalize line endings
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    cfg_dir = os.path.dirname(cfg_path)
    if not os.path.isdir(cfg_dir):
        os.makedirs(cfg_dir, exist_ok=True)
    with open(cfg_path, 'w') as f:
        f.write(content)
    flash('multi.cfg saved.', 'success')
    return redirect(url_for('game_config'))


@app.route('/game-logs')
@login_required
def game_logs():
    panels = get_log_panels()
    for panel in panels:
        if not os.path.exists(panel['path']):
            panel['lines'] = None
            panel['error'] = f'Log file not found: {os.path.basename(panel["path"])}'
        else:
            with open(panel['path']) as f:
                panel['lines'] = f.readlines()[-LOG_LINES:]
                _sync_watcher_to_offset(panel['path'], f.tell())
            panel['error'] = None
    return render_template('logs.html', panels=panels)


# --- Engine web UI proxy ---
# Forwards requests to the game engine's built-in Mongoose HTTP server,
# injecting Basic Auth from multi.cfg so the user only authenticates once
# through the Flask login.  Two route prefixes are needed because the legacy
# JS uses a mix of relative URLs (resolve under /engine/) and absolute URLs
# (resolve at /api/1/).

_ENGINE_PROXY_TIMEOUT = 10  # seconds

# Relaxed CSP for the legacy engine webui which relies on inline styles
# (jQuery UI, DataTables) and may use eval (older jQuery/DataTables).
_ENGINE_CSP = (
    "default-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
    "connect-src 'self'; "
    "img-src 'self'"
)

# External auto-login script tag injected into the legacy index.html so
# users skip the built-in login form — our proxy handles authentication.
_ENGINE_AUTOLOGIN_TAG = '<script src="/static/engine_autologin.js"></script>'


def _proxy_to_engine(target_path):
    """Forward the current request to the engine's web server."""
    webapi = parse_multi_cfg_webapi()
    if not webapi:
        return make_response('Engine web API is not configured in multi.cfg.', 502)

    url = f'http://127.0.0.1:{webapi["port"]}/{target_path}'
    if request.query_string:
        url += '?' + request.query_string.decode()

    # Strip hop-by-hop and auth headers — we supply our own auth
    fwd_headers = {k: v for k, v in request.headers
                   if k.lower() not in ('host', 'authorization', 'cookie')}

    try:
        resp = http_requests.request(
            method=request.method,
            url=url,
            data=request.get_data(),
            headers=fwd_headers,
            auth=(webapi['username'], webapi['password']),
            allow_redirects=False,
            timeout=_ENGINE_PROXY_TIMEOUT,
        )
    except http_requests.ConnectionError:
        return make_response('Engine web server is not reachable.', 502)
    except http_requests.Timeout:
        return make_response('Engine web server timed out.', 504)

    # Pass through the response, stripping hop-by-hop headers
    excluded = {'content-encoding', 'transfer-encoding', 'connection'}
    headers = {k: v for k, v in resp.headers.items()
               if k.lower() not in excluded}

    body = resp.content

    # For the legacy HTML page: inject auto-login and set a relaxed CSP
    if target_path in ('', 'index.html') and resp.status_code == 200:
        text = resp.text
        text = text.replace('</body>', _ENGINE_AUTOLOGIN_TAG + '\n</body>')
        response = make_response(text, resp.status_code, headers)
        response.headers['Content-Security-Policy'] = _ENGINE_CSP
        return response

    return make_response(body, resp.status_code, headers)


@app.route('/engine/')
@app.route('/engine/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
@csrf.exempt
def engine_proxy(subpath=''):
    return _proxy_to_engine(subpath)


@app.route('/api/1/', methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/api/1/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
@csrf.exempt
def engine_api_proxy(subpath=''):
    return _proxy_to_engine(f'api/1/{subpath}')


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes')
    socketio.run(app, host=HOST, port=PORT, debug=debug)
