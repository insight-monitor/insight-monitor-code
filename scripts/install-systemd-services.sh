#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVICES=(
    "insight-backend.service"
    "insight-capture.service"
    "insight-dashboard.service"
)

SYSTEMD_USER_DIR="$HOME/.config/systemd/user"

echo "==> Insight Monitor — Systemd Service Installer"
echo ""

mkdir -p "$SYSTEMD_USER_DIR"

for svc in "${SERVICES[@]}"; do
    echo "    Installing $svc..."
    cp "$SCRIPT_DIR/$svc" "$SYSTEMD_USER_DIR/"
done

echo ""
echo "==> Reloading systemd daemon..."
systemctl --user daemon-reload

for svc in "${SERVICES[@]}"; do
    echo "    Enabling $svc..."
    systemctl --user enable "$svc" 2>/dev/null || echo "    (could not enable — run manually: systemctl --user enable $svc)"
done

echo ""
echo "==> Starting services..."
for svc in "${SERVICES[@]}"; do
    echo "    Starting $svc..."
    systemctl --user start "$svc" 2>/dev/null || echo "    (could not start — run manually: systemctl --user start $svc)"
done

echo ""
echo "==> Installation complete!"
echo ""
echo "    Check service status:"
echo "      systemctl --user status insight-backend"
echo "      systemctl --user status insight-capture"
echo "      systemctl --user status insight-dashboard"
echo ""
echo "    View logs:"
echo "      journalctl --user -u insight-backend -f"
echo "      journalctl --user -u insight-capture -f"
echo "      journalctl --user -u insight-dashboard -f"
