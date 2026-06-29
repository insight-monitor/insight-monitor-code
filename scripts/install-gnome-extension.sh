#!/usr/bin/env bash
set -euo pipefail

EXT_DIR="$HOME/.local/share/gnome-shell/extensions/insight-monitor@insight-monitor"
SRC_DIR="$(cd "$(dirname "$0")/../capture/gnome-extension/insight-monitor@insight-monitor" && pwd)"

echo "==> Installing Insight Monitor GNOME Shell extension..."

mkdir -p "$EXT_DIR"

cp "$SRC_DIR/extension.js" "$EXT_DIR/"
cp "$SRC_DIR/metadata.json" "$EXT_DIR/"
cp "$SRC_DIR/stylesheet.css" "$EXT_DIR/"

echo "==> Extension files copied to $EXT_DIR"

if command -v gnome-extensions &>/dev/null; then
    echo "==> Enabling extension..."
    gnome-extensions enable insight-monitor@insight-monitor 2>/dev/null || {
        echo "==> Could not enable via gnome-extensions CLI."
        echo "    Enable manually: gnome-extensions enable insight-monitor@insight-monitor"
        echo "    Or via GNOME Extensions app."
    }
else
    echo "==> gnome-extensions CLI not found. Enable the extension manually via GNOME Extensions app."
fi

echo ""
echo "==> Installation complete!"
echo ""
echo "    Restart GNOME Shell to activate:"
echo "      Xorg:  Alt+F2, type 'r', press Enter"
echo "      Wayland: Log out and log back in"
echo ""
echo "    Verify with: cat /tmp/insight-window.json"
