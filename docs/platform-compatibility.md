# Platform Compatibility

## Supported Platforms

| Platform | Display Server | Window Tracking | Status |
|----------|---------------|-----------------|--------|
| Ubuntu 22.04 (GNOME 42) | X11 | `xdotool` + `xprop` | Supported |
| Ubuntu 22.04 (GNOME 42) | Wayland | GNOME Shell extension | Requires GNOME 45+ — not supported |
| Ubuntu 24.04 (GNOME 46) | X11 | `xdotool` + `xprop` | Supported |
| Ubuntu 24.04 (GNOME 46) | Wayland | GNOME Shell extension | Supported |
| Other Linux (X11) | X11 | `xdotool` + `xprop` | Supported (requires xdotool) |
| Other Linux (Wayland, GNOME 45+) | Wayland | GNOME Shell extension | Supported |
| Other Wayland compositors (KDE, Sway) | Wayland | Not supported | No window tracking available |

## Wayland

### Requirements

- GNOME Shell 45+ (Ubuntu 24.04 ships GNOME 46)
- `gnome-extensions` CLI
- Python 3.11+

### Setup

1. Install the GNOME Shell extension:
   ```bash
   bash scripts/install-gnome-extension.sh
   ```

2. Restart GNOME Shell:
   - Xorg: `Alt+F2`, type `r`, Enter
   - Wayland: Log out and log back in

3. Verify:
   ```bash
   cat /tmp/insight-window.json
   ```

See `docs/capture-agent/wayland-setup.md` for detailed instructions.

### Known Limitations

- Only GNOME Shell is supported (not KDE, Sway, etc.)
- Browser tab URL detection requires the URL in the window title
- The extension tracks only the focused window
- GNOME Shell 45+ required (ESM extension format)

## X11

### Requirements

- `xdotool` and `xprop` installed:
  ```bash
  sudo apt install xdotool x11-utils
  ```

### Setup

No additional setup needed. The capture agent auto-detects X11 and uses `xdotool`/`xprop`.

## Self-Hosted Deployment (Systemd)

Three user-level systemd services for auto-start on boot:

| Service | Description | Port |
|---------|-------------|------|
| `insight-backend.service` | FastAPI backend | 8002 |
| `insight-capture.service` | Capture agent (depends on backend) | — |
| `insight-dashboard.service` | Vite dashboard dev server | 5173 |

### Install

```bash
bash scripts/install-systemd-services.sh
```

### Manage

```bash
systemctl --user status insight-backend
systemctl --user status insight-capture
systemctl --user status insight-dashboard
```

### View Logs

```bash
journalctl --user -u insight-backend -f
journalctl --user -u insight-capture -f
journalctl --user -u insight-dashboard -f
```

## Tested Configurations

| Ubuntu Version | GNOME Version | Display Server | Tested |
|---------------|---------------|----------------|--------|
| 24.04 LTS | 46 | Wayland | In progress |
| 24.04 LTS | 46 | X11 | In progress |
| 22.04 LTS | 42 | X11 | In progress |
