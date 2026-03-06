# Standalone Server Update Script

Automated build-and-deploy script for FSO standalone game servers. Designed to run on headless Linux VPS servers, typically triggered by cron.

## What It Does

1. Fetches the latest source from a local FSO git repo at a configurable ref (branch, tag, etc.)
2. Creates a git worktree export and builds the engine via cmake/make
3. Optionally updates a mod directory (git or svn)
4. Stops any running server instance (screen session)
5. Deploys the new build and restarts the server in a detached screen
6. Cleans up old build exports, keeping only the most recent

## Prerequisites

- Linux system with bash
- git, cmake, make
- gcc or clang (and associated C++ compiler)
- screen
- A local clone of the [fs2open](https://github.com/scp-fs2open/fs2open.github.com) repository with submodules
- A game root directory with the base game data files (e.g. retail VPs)
- Optional: gdb or lldb for debugger-attached runs

## Installation

1. Clone or copy this directory onto your server.

2. Ensure the FSO source repo is cloned locally with submodules:
   ```bash
   git clone --recurse-submodules https://github.com/scp-fs2open/fs2open.github.com.git /usr/share/games/fs2source/fs2_open
   ```

3. Create your game root directory with the base game data:
   ```bash
   mkdir -p /usr/share/games/freespace2
   # Copy retail VP files, etc. into this directory
   ```

4. Optionally create a `.env` file with your overrides (see Configuration below).

5. Make sure the `update` script is executable:
   ```bash
   chmod +x update
   ```

## Configuration

The script uses a two-layer config system:

- `.env.default` — Checked-in defaults. Don't edit this on your server.
- `.env` — Your local overrides (gitignored). Only set values that differ from defaults.

### Available Variables

| Variable | Default | Description |
|---|---|---|
| `BUILD_TYPE` | `Release` | CMake build type (`Release`, `Debug`, `FastDebug`, etc.) |
| `COMPILER` | `gcc` | Compiler toolchain (`gcc` or `clang`) |
| `USE_DEBUGGER` | _(unset)_ | Set to any non-empty value to run the server under gdb/lldb |
| `FSO_REPO` | `/usr/share/games/fs2source/fs2_open` | Path to the local FSO git repository |
| `GAME_ROOT` | `/usr/share/games/freespace2` | Path to the game data directory where builds are deployed |
| `BUILD_EXPORTS_DIR` | `/usr/share/games/fs2source/build_exports` | Working directory for build worktrees |
| `MOD_DIRNAME` | _(unset)_ | Mod folder name (e.g. `fotg`). Enables mod-specific launch flags. |
| `MOD_VCS` | _(unset)_ | VCS for auto-updating the mod folder (`git` or `svn`). Leave unset to manage manually. |
| `REFERENCE` | `origin/master` | Git reference to build from — branch (`origin/master`), tag (`release_25_0_0`), or commit hash |
| `EXTRA_FLAGS` | _(unset)_ | Additional command line flags passed to the game binary (e.g. `-prefer_ipv4`) |

### Example `.env`

```bash
BUILD_TYPE=FastDebug
GAME_ROOT=/usr/share/games/fotg
MOD_DIRNAME=fotg
MOD_VCS=git
REFERENCE=release_25_0_0
EXTRA_FLAGS=-prefer_ipv4
```

All variables can also be passed as command line arguments (run `./update -h` for usage).

## Server Control Modes

In addition to a full rebuild, the update script supports two shortcut modes:

```bash
./update -R   # Restart using the existing deployed binary (skip fetch/build)
./update -S   # Stop the server without restarting
```

`-R` is useful for applying configuration changes or recovering a crashed server quickly. `-S` shuts down the screen session and game process without bringing them back up.

## Cron Setup

The script is intended to be run via cron. Example crontab entry that runs daily at 09:00 UTC:

```cron
# Set timezone to UTC for this crontab
CRON_TZ=UTC

# Run script daily at 0900 UTC
0 9 * * * /usr/share/games/fs2source/nightlybuild/standalone_update/update > /home/scpuser/standalone_update.log 2>&1
```

Each run produces a uniquely named build (datetime + commit hash), so the script can safely be run multiple times per day.

## Web UI

A small Flask web app for managing `.env` configuration, triggering server rebuilds and restarts, and viewing logs.

### Requirements

- Python 3.11+
- pip (for installing dependencies into a venv)

### Setup

```bash
cd standalone_update/web
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

### Running locally (development)

```bash
cd standalone_update/web
FLASK_DEBUG=1 venv/bin/python server.py
```

`FLASK_DEBUG=1` enables the auto-reloader and interactive error page. Omit it for a plain local run.

### Running via gunicorn (production / testing the production stack)

The service uses gunicorn as the WSGI server. The `web/run` script is the easiest way to run it locally — it loads configuration from `web/standalone-update-web.env` (copy from `standalone-update-web.env.example` and fill in your values):

```bash
cd standalone_update
web/run
```

Set `GUNICORN_RELOAD=1` in your env file to enable auto-restart on file changes.

### Systemd setup

The service reads all configuration from an environment file at `/etc/standalone-update-web.env` (root-owned, mode 600):

```bash
# Create the environment file from the example
sudo cp web/standalone-update-web.env.example /etc/standalone-update-web.env
sudo chmod 600 /etc/standalone-update-web.env
# Edit it to set your paths and generate a SECRET_KEY:
#   python3 -c "import secrets; print(secrets.token_hex(32))"
sudo nano /etc/standalone-update-web.env

# Install and start the service
sudo cp web/standalone-update-web.service.example /etc/systemd/system/standalone-update-web.service
sudo systemctl daemon-reload
sudo systemctl enable --now standalone-update-web
```

### Pages

| Page | Description |
|---|---|
| **Configuration** | View and override `.env` variables with live default display |
| **Server** | Trigger a full rebuild, restart, or stop, with live update log |
| **Logs** | View the FSO standalone and multiplayer engine logs (auto-refreshing) |

### Access

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

# Create the htpasswd file for HTTP Basic Auth
sudo apt install apache2-utils
sudo htpasswd -c /etc/nginx/standalone-update-web.htpasswd yourusername

# Install the nginx config and set your domain
sudo cp web/standalone-update-web.nginx.conf.example /etc/nginx/sites-available/standalone-update-web
sudo nano /etc/nginx/sites-available/standalone-update-web  # replace your.domain.example
sudo ln -s /etc/nginx/sites-available/standalone-update-web /etc/nginx/sites-enabled/

# Obtain TLS certificate (certbot will also patch the nginx config)
sudo certbot --nginx -d your.domain.example

# Verify and reload
sudo nginx -t && sudo systemctl reload nginx
```

### Configuration

The web app is configured via environment variables (set in `/etc/standalone-update-web.env` or your shell):

| Variable | Default | Description |
|---|---|---|
| `WEB_HOST` | `127.0.0.1` | Bind address |
| `WEB_PORT` | `5000` | Listen port |
| `UPDATE_LOG_PATH` | _(none)_ | Path to the update log file — read for display and used as the output destination when rebuild/restart is triggered from the UI |
| `LOG_LINES` | `100` | Maximum number of log lines to display |
| `SECRET_KEY` | _(random)_ | Flask session secret — set a stable value in production to preserve sessions across restarts |

## Directory Structure

After setup, the typical directory layout on a server looks like:

```
/usr/share/games/
├── fs2source/
│   ├── fs2_open/                  # FSO source repo (git clone)
│   ├── build_exports/             # Worktree build artifacts (managed by script)
│   └── nightlybuild/
│       └── standalone_update/     # This directory
│           ├── update             # The script
│           ├── .env.default       # Default configuration
│           ├── .env               # Your overrides (gitignored)
│           └── web/               # Web UI for config management
│               ├── server.py
│               ├── env_parser.py
│               └── venv/          # Python venv (gitignored)
└── freespace2/                    # Game root (retail data + deployed binary)
    ├── fs2_open_20250226090000_a1b2c3d  # Currently deployed build
    ├── root_fs2.vp
    └── ...
```
