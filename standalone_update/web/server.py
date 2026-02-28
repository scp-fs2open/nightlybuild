#!/usr/bin/env python3
import os

from flask import Flask, render_template, request, redirect, url_for, flash

from env_parser import parse_env_default, parse_env, write_env, merge_variables

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Paths — .env.default and .env live one directory up from this script
SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ENV_DEFAULT_PATH = os.path.join(SCRIPT_DIR, '.env.default')
ENV_PATH = os.path.join(SCRIPT_DIR, '.env')

# Web app configuration via environment variables
HOST = os.environ.get('WEB_HOST', '127.0.0.1')
PORT = int(os.environ.get('WEB_PORT', '5000'))
LOG_PATH = os.environ.get('UPDATE_LOG_PATH', '')
LOG_LINES = int(os.environ.get('LOG_LINES', '100'))


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


@app.route('/log')
def log_viewer():
    if not LOG_PATH:
        return render_template('log.html', lines=None, log_path=None,
                               error='UPDATE_LOG_PATH is not configured.')

    if not os.path.exists(LOG_PATH):
        return render_template('log.html', lines=None, log_path=LOG_PATH,
                               error=f'Log file not found: {LOG_PATH}')

    with open(LOG_PATH) as f:
        all_lines = f.readlines()
        lines = all_lines[-LOG_LINES:]

    return render_template('log.html', lines=lines, log_path=LOG_PATH, error=None)


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=False)
