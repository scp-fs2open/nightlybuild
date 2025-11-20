#!/bin/bash

DATE=$(date +%Y%m%d)

### Configuration ###
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Load defaults
if [ -f "${SCRIPT_DIR}/.env.default" ]; then
    echo "Loading defaults from .env.defaults..."
    . "${SCRIPT_DIR}/.env.default"
fi

# Load user overrides
if [ -f "${SCRIPT_DIR}/.env" ]; then
    echo "Loading user configuration from .env..."
    . "${SCRIPT_DIR}/.env"
fi

# Parse command line arguments (overrides config file)
while getopts "t:d:c:r:m:v:h" opt; do
    case "${opt}" in
        t) BUILD_TYPE="${OPTARG}" ;;
        d) USE_DEBUGGER="${OPTARG}" ;;
        c) COMPILER="${OPTARG}" ;;
        r) REFERENCE="${OPTARG}" ;;
        m) MOD_DIRNAME="${OPTARG}" ;;
        v) MOD_VCS="${OPTARG}" ;;
        h)
            echo "Usage: $0 [-t BUILD_TYPE] [-d USE_DEBUGGER] [-c COMPILER] [-r REFERENCE] [-m MOD_DIRNAME] [-v MOD_VCS]"
            exit 0
            ;;
        *)
            echo "Invalid option. Use -h for help."
            exit 1
            ;;
    esac
done
shift $((OPTIND - 1))

# Auto-derive MOD_ROOT
if [ -n "${MOD_DIRNAME}" ]; then
    MOD_ROOT="${GAME_ROOT}/${MOD_DIRNAME}"
fi

# Compiler configuration
case "${COMPILER}" in
  clang)
    DEBUGGER=lldb
    DEBUGGER_FLAG="-o"
    export CC=${CC:-clang}
    export CXX=${CXX:-clang++}
    ;;
  gcc|*)
    DEBUGGER=gdb
    DEBUGGER_FLAG="-ex"
    export CC=${CC:-gcc}
    export CXX=${CXX:-g++}
    ;;
esac

# Set MAIN_PROCESS based on debugger usage
if [ -n "${USE_DEBUGGER}" ]; then
    MAIN_PROCESS="${DEBUGGER}"
else
    MAIN_PROCESS="fs2_open"
fi

# Function to handle errors
error_exit() {
    echo "ERROR: $1" >&2
    exit 1
}

echo "Starting fs2_open export process..."

# Verify parent repo exists
if [ ! -d "$FSO_REPO" ]; then
    error_exit "FSO source directory not found at: $FSO_REPO"
fi

if [ ! -d "$FSO_REPO/.git" ]; then
    error_exit "FSO source directory exists but is not a git repository: $FSO_REPO"
fi

if [ ! -d "${GAME_ROOT}" ]; then
    error_exit "Game folder does not exist at: ${GAME_ROOT}"
fi

if [ -n "${MOD_ROOT}" ]; then
    if [ ! -d "${MOD_ROOT}" ]; then
        error_exit "Mod directory does not exist at: ${MOD_ROOT}"
    fi

    if [ -n "${MOD_VCS}" ]; then
        if [ ! -d "${MOD_ROOT}/.${MOD_VCS}" ]; then
            error_exit "Mod directory is not a ${MOD_VCS} repository: ${MOD_ROOT}"
        fi
    fi
fi

# Create build_exports directory if it doesn't exist
echo "Ensuring build_exports directory exists..."
mkdir -p "$BUILD_EXPORTS_DIR" || error_exit "Failed to create build_exports directory: $BUILD_EXPORTS_DIR"

# Fetch updates for parent and all submodules
echo "Fetching updates for parent repo and submodules..."
git -C "$FSO_REPO" fetch --recurse-submodules || error_exit "Failed to fetch updates from remote repositories"

# Get short hash for the reference
echo "Resolving reference '$REFERENCE' to commit hash..."
HASH=$(git -C "$FSO_REPO" rev-parse --short "$REFERENCE" 2>/dev/null) || error_exit "Reference '$REFERENCE' not found in repository"

# Build export path
EXPORT_PATH="$BUILD_EXPORTS_DIR/fs2_open_${DATE}_${HASH}"
BUILD_PATH="${EXPORT_PATH}/build"

# Check if export already exists
if [ -d "$EXPORT_PATH" ]; then
    error_exit "Export directory already exists: $EXPORT_PATH"
fi

echo "Creating worktree at '$EXPORT_PATH'..."
git -C "$FSO_REPO" worktree add "$EXPORT_PATH" "$REFERENCE" || error_exit "Failed to create worktree at: $EXPORT_PATH"

# Initialize submodules in the worktree
echo "Initializing submodules in worktree..."
cd "$EXPORT_PATH" || error_exit "Failed to change to export directory: $EXPORT_PATH"
git submodule update --init --recursive || error_exit "Failed to initialize submodules"

# Clean up git metadata
echo "Removing git metadata..."
rm -rf .git || error_exit "Failed to remove .git directory"
find . -name ".git" -exec rm -rf {} + 2>/dev/null || true  # Don't fail if some .git files are already gone

# Return to original location and clean up worktree tracking
echo "Cleaning up worktree tracking..."
cd - > /dev/null || error_exit "Failed to return to previous directory"
git -C "$FSO_REPO" worktree prune || error_exit "Failed to clean up worktree tracking"

echo "Export completed successfully at: $EXPORT_PATH"

# Make build folder
echo "Making build folder inside export folder..."
mkdir -p "${BUILD_PATH}" || error_exit "Could not create build folder: ${BUILD_PATH}"

# Run cmake
echo "Running cmake inside build export build folder..."
cmake -DCMAKE_BUILD_TYPE="${BUILD_TYPE}" -S "${EXPORT_PATH}" -B "${BUILD_PATH}" || error_exit "Failed to run cmake for type ${BUILD_TYPE} in ${BUILD_PATH}"

# Run make
echo "Running make inside build export build folder..."
make -C "${BUILD_PATH}" || error_exit "make failed to run in: ${BUILD_PATH}"

if [ -n "${MOD_ROOT}" ] && [ -n "${MOD_VCS}" ]; then
    if [ "${MOD_VCS}" = "git" ]; then
        # Update mod git
        echo "Updating mod git folder..."
        git -C "${MOD_ROOT}" pull || error_exit "Failed to update mod git folder at ${MOD_ROOT}"
    elif [ "${MOD_VCS}" = "svn" ]; then
        # Update mod svn
        echo "Updating mod svn folder..."
        (cd "${MOD_ROOT}" && svn up) || error_exit "Failed to update mod svn folder at ${MOD_ROOT}"
    fi
fi

# Kill server
echo "Restarting server..."
if pgrep "${MAIN_PROCESS}" > /dev/null 2>&1; then
    echo "Killing ${MAIN_PROCESS}..."
    pkill "${MAIN_PROCESS}" || error_exit "Could not kill ${MAIN_PROCESS}"
fi

if screen -ls | grep server > /dev/null; then
    echo "Killing screen..."
    screen -S server -X quit || error_exit "Could not kill screen"
fi

# Remove existing builds
echo "Checking for old game builds..."
if ls ${GAME_ROOT}/fs2_open_* > /dev/null 2>&1; then
    echo "Removing old game builds"
    rm -rf ${GAME_ROOT}/fs2_open_* || error_exit "Could not remove old builds in ${GAME_ROOT}"
else
    echo "No old builds found"
fi

# Copy build
echo "Copying build to game folder..."
cp ${BUILD_PATH}/bin/fs2_open_* "${GAME_ROOT}/fs2_open_${DATE}" || error_exit "Failed to copy build to game root ${GAME_ROOT}"

# Restart the server
echo "Starting screen and ${MAIN_PROCESS}/${MOD_DIRNAME:-freespace2}"
(
    cd ${GAME_ROOT}
    if [ -n "${USE_DEBUGGER}" ]; then
        screen -dmS server ${DEBUGGER} ${DEBUGGER_FLAG} "r -standalone -noninteractive${MOD_DIRNAME:+ -mod ${MOD_DIRNAME}}" "fs2_open_${DATE}"
    else
        screen -dmS server ./fs2_open_${DATE} -standalone -noninteractive${MOD_DIRNAME:+ -mod ${MOD_DIRNAME}}
    fi
)

# Clean up old build_exports
(
    cd "$BUILD_EXPORTS_DIR" || error_exit "Failed to change to export directory: $BUILD_EXPORTS_DIR"

    EXPORT_COUNT=$(ls -1 | wc -l)
    if [ "$EXPORT_COUNT" -gt 1 ]; then
        echo "Cleaning up old build_export folders..."
        ls -t | tail -n +2 | xargs rm -rf || error_exit "Failed to remove old exports under ${BUILD_EXPORTS_DIR}"
    else
        echo "Only one build export found, nothing to clean up"
    fi
)
