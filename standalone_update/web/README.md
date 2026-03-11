# Standalone Update Web UI

A Flask web app for managing the FSO standalone update system — edit `.env` configuration, trigger server rebuilds and restarts, edit `multi.cfg`, and view logs, all from a browser with real-time WebSocket streaming.

The web app controls the `update` script and `.env` configuration in the parent `standalone_update/` directory. See the [parent README](../README.md) for update script documentation.

All commands below assume you are in the `standalone_update/web/` directory.

## Requirements

- Python 3.11+
- pip (for installing dependencies into a venv)

## Setup

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

## Running locally (development)

```bash
FLASK_DEBUG=1 venv/bin/python server.py
```

`FLASK_DEBUG=1` enables the auto-reloader and interactive error page. Omit it for a plain local run.

## Running via gunicorn (production / testing the production stack)

The service uses gunicorn as the WSGI server. The `run` script is the easiest way to run it locally — it loads configuration from `standalone-update-web.env` (copy from `standalone-update-web.env.example` and fill in your values):

```bash
./run
```

Set `GUNICORN_RELOAD=1` in your env file to enable auto-restart on file changes.

## Systemd setup

Create local copies of the example files and edit them in place:

```bash
# Create your env file from the example and fill in your values
cp standalone-update-web.env.example standalone-update-web.env
chmod 600 standalone-update-web.env
# Edit it to set your paths and generate a SECRET_KEY:
#   python3 -c "import secrets; print(secrets.token_hex(32))"
nano standalone-update-web.env

# Create your service file from the example and edit paths/user as needed
cp standalone-update-web.service.example standalone-update-web.service
nano standalone-update-web.service

# Symlink the service file into systemd and start it
sudo ln -s "$(pwd)/standalone-update-web.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now standalone-update-web
```

## Pages

| Page | Description |
|---|---|
| **Build Config** | View and override `.env` variables with live default display |
| **Build Controls** | Trigger a full rebuild, restart, or stop, with real-time log streaming |
| **Game Config** | Edit the `multi.cfg` file used by the game server |
| **Game Logs** | View the FSO standalone and multiplayer engine logs (real-time streaming) |

## Access

**SSH tunnel (simple, no nginx required):**

```bash
ssh -L 5000:127.0.0.1:5000 user@yourserver
# Then open http://localhost:5000 in your browser
```

**Public HTTPS via nginx (for direct internet access):**

Requires nginx, certbot, and a domain pointing at your server.

```bash
# Install nginx and certbot
sudo apt install nginx python3-certbot-nginx
sudo systemctl enable --now nginx

# Create your nginx config from the example and set your domain
cp standalone-update-web.nginx.conf.example standalone-update-web.nginx.conf
nano standalone-update-web.nginx.conf  # replace your.domain.example

# Symlink into nginx config directory
# Debian/Ubuntu:
sudo ln -s "$(pwd)/standalone-update-web.nginx.conf" /etc/nginx/sites-enabled/
# RHEL/CentOS/Fedora/Arch/openSUSE:
#   sudo ln -s "$(pwd)/standalone-update-web.nginx.conf" /etc/nginx/conf.d/

# Obtain TLS certificate (certbot will also patch the nginx config)
sudo certbot --nginx -d your.domain.example

# Verify and reload
sudo nginx -t && sudo systemctl reload nginx
```

## Configuration

The web app is configured via environment variables (set in `standalone-update-web.env` or your shell):

| Variable | Default | Description |
|---|---|---|
| `WEB_HOST` | `127.0.0.1` | Bind address |
| `WEB_PORT` | `5000` | Listen port |
| `UPDATE_LOG_PATH` | _(none)_ | Path to the update log file — read for display and used as the output destination when rebuild/restart is triggered from the UI |
| `LOG_LINES` | `100` | Maximum number of log lines to display |
| `SECRET_KEY` | _(random)_ | Flask session secret — set a stable value in production to preserve sessions across restarts |
| `PASSWORD_HASH` | _(none)_ | Werkzeug-compatible password hash for the login form — generate with `python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('yourpassword'))"` (uses scrypt by default; any algorithm supported by `check_password_hash` will work) |
| `SECURE_COOKIES` | `0` | Set to `1` to mark session and remember-me cookies as `Secure` (requires HTTPS) |
