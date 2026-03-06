#!/usr/bin/env python3
import os
import subprocess
import sys
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash

from env_parser import parse_env_default, parse_env, write_env, merge_variables

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

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
_running_action = None  # 'rebuilding' or 'restarting'


def get_status():
    """Return (status_string, is_running) for the current update process."""
    global _running_process, _running_action
    if _running_process is not None:
        if _running_process.poll() is None:
            return (_running_action, True)
        # Process finished — clear state
        _running_process = None
        _running_action = None
    return ('idle', False)


def start_update(restart_only=False, stop_only=False):
    """Start the update script in the background. Returns True on success."""
    global _running_process, _running_action
    status, is_running = get_status()
    if is_running:
        return False

    if stop_only:
        action, flag, running_label = 'stop', '-S', 'stopping'
    elif restart_only:
        action, flag, running_label = 'restart', '-R', 'restarting'
    else:
        action, flag, running_label = 'rebuild', None, 'rebuilding'

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    header = f'=== Web UI: {action} triggered at {timestamp} ===\n'

    log_file = open(LOG_PATH, 'w')
    log_file.write(header)
    log_file.flush()

    cmd = [UPDATE_SCRIPT]
    if flag:
        cmd.append(flag)

    _running_process = subprocess.Popen(
        cmd, stdout=log_file, stderr=subprocess.STDOUT,
        cwd=SCRIPT_DIR
    )
    _running_action = running_label
    return True


def get_fso_data_dir():
    if sys.platform == 'darwin':
        return os.path.expanduser(
            '~/Library/Application Support/HardLightProductions/FreeSpaceOpen')
    else:
        xdg = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
        return os.path.join(xdg, 'HardLightProductions', 'FreeSpaceOpen')


def get_log_panels():
    fso_data = get_fso_data_dir()
    mod_dirname = parse_env(ENV_PATH).get('MOD_DIRNAME', '')
    multi_path = (os.path.join(fso_data, mod_dirname, 'data', 'multi.log')
                  if mod_dirname else
                  os.path.join(fso_data, 'data', 'multi.log'))
    return [
        {'id': 'standalone', 'name': 'FSO Standalone Log',
         'path': os.path.join(fso_data, 'data', 'fs2_standalone.log')},
        {'id': 'multi', 'name': 'Multi Log', 'path': multi_path},
    ]


def read_log_lines():
    """Read the last LOG_LINES from the log file. Returns (lines, error)."""
    if not LOG_PATH:
        return (None, 'UPDATE_LOG_PATH is not configured.')
    if not os.path.exists(LOG_PATH):
        return (None, f'Log file not found: {LOG_PATH}')
    with open(LOG_PATH) as f:
        all_lines = f.readlines()
        return (all_lines[-LOG_LINES:], None)


@app.route('/')
def index():
    return redirect(url_for('config'))


@app.route('/config', methods=['GET'])
def config():
    variables = parse_env_default(ENV_DEFAULT_PATH)
    overrides = parse_env(ENV_PATH)
    sections = merge_variables(variables, overrides)
    return render_template('config.html', sections=sections)


@app.route('/config', methods=['POST'])
def config_save():
    variables = parse_env_default(ENV_DEFAULT_PATH)
    overrides = {}

    for var in variables:
        is_overridden = request.form.get(f'override_{var.name}') == 'on'
        value = request.form.get(f'value_{var.name}', '').strip()
        if is_overridden and value:
            overrides[var.name] = value

    write_env(ENV_PATH, overrides)
    flash('Configuration saved.', 'success')
    return redirect(url_for('config'))


@app.route('/server')
def server():
    status, is_running = get_status()
    lines, log_error = read_log_lines()
    return render_template('server.html', status=status, is_running=is_running,
                           lines=lines, log_path=LOG_PATH, log_error=log_error)


@app.route('/server/rebuild', methods=['POST'])
def server_rebuild():
    if not LOG_PATH:
        flash('Cannot run: UPDATE_LOG_PATH is not configured.', 'error')
        return redirect(url_for('server'))
    if not start_update(restart_only=False):
        flash('An update is already in progress.', 'error')
        return redirect(url_for('server'))
    flash('Rebuild started.', 'success')
    return redirect(url_for('server'))


@app.route('/server/restart', methods=['POST'])
def server_restart():
    if not LOG_PATH:
        flash('Cannot run: UPDATE_LOG_PATH is not configured.', 'error')
        return redirect(url_for('server'))
    if not start_update(restart_only=True):
        flash('An update is already in progress.', 'error')
        return redirect(url_for('server'))
    flash('Restart started.', 'success')
    return redirect(url_for('server'))


@app.route('/server/stop', methods=['POST'])
def server_stop():
    if not LOG_PATH:
        flash('Cannot run: UPDATE_LOG_PATH is not configured.', 'error')
        return redirect(url_for('server'))
    if not start_update(stop_only=True):
        flash('An update is already in progress.', 'error')
        return redirect(url_for('server'))
    flash('Stop initiated.', 'success')
    return redirect(url_for('server'))


@app.route('/logs')
def logs():
    panels = get_log_panels()
    for panel in panels:
        if not os.path.exists(panel['path']):
            panel['lines'] = None
            panel['error'] = f'Log file not found: {panel["path"]}'
        else:
            with open(panel['path']) as f:
                panel['lines'] = f.readlines()[-LOG_LINES:]
            panel['error'] = None
    return render_template('logs.html', panels=panels)


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=False)
