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
| `MOD_DIRNAME` | _(unset)_ | Comma-delimited mod list (e.g. `fotg` or `fotg,fotg-test`). First mod is primary and determines the engine data folder. Passed directly to the engine's `-mod` flag. |
| `MOD_VCS` | _(unset)_ | VCS per mod, positionally matched to `MOD_DIRNAME` (`git`, `svn`, or empty for unmanaged). E.g. `git,svn` or `git,` |
| `REFERENCE` | `origin/master` | Git reference to build from — branch (`origin/master`), tag (`release_25_0_0`), commit hash, or pull request (`pr/NUMBER` or `pull/NUMBER`) |
| `EXTRA_FLAGS` | _(unset)_ | Additional command line flags passed to the game binary (e.g. `-prefer_ipv4`) |

### Example `.env`

```bash
BUILD_TYPE=FastDebug
GAME_ROOT=/usr/share/games/fotg
MOD_DIRNAME=fotg,fotg-test
MOD_VCS=git,svn
REFERENCE=release_25_0_0
EXTRA_FLAGS=-prefer_ipv4
```

To build from a GitHub pull request instead:

```bash
REFERENCE=pr/7306
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

A web app is available in the [`web/`](web/) directory for managing configuration, triggering builds/restarts, and viewing logs from a browser. See [web/README.md](web/README.md) for setup instructions.

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
│           └── web/               # Web UI (see web/README.md)
└── freespace2/                    # Game root (retail data + deployed binary)
    ├── fs2_open_20250226090000_a1b2c3d  # Currently deployed build
    ├── root_fs2.vp
    └── ...
```
