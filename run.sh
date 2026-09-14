#!/usr/bin/env sh
set -e
cd "$(dirname "$0")"

export PATH="$HOME/.local/bin:$PATH"

if ! command -v uv >/dev/null 2>&1; then
    echo "==> Installing uv (Python manager)..."
    if command -v curl >/dev/null 2>&1; then
        curl -LsSf https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh
    elif command -v wget >/dev/null 2>&1; then
        wget -qO- https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh
    else
        echo "Error: curl or wget is required to install uv." >&2
        exit 1
    fi
fi

if [ "$(uname -s)" = "Linux" ]; then
    LDCONFIG=$(command -v ldconfig || echo /sbin/ldconfig)
    if ! "$LDCONFIG" -p 2>/dev/null | grep -q "libxcb-cursor.so.0"; then
        echo "==> Installing libxcb-cursor (required by Qt, sudo password may be asked)..."
        if command -v apt-get >/dev/null 2>&1; then
            sudo apt-get install -y libxcb-cursor0
        elif command -v pacman >/dev/null 2>&1; then
            sudo pacman -S --needed --noconfirm xcb-util-cursor
        elif command -v dnf >/dev/null 2>&1; then
            sudo dnf install -y xcb-util-cursor
        elif command -v zypper >/dev/null 2>&1; then
            sudo zypper install -y libxcb-cursor0
        else
            false
        fi || echo "Warning: could not install libxcb-cursor, the window may fail to open on X11." >&2
    fi
fi

exec uv run --script gpss-studio.py "$@"
