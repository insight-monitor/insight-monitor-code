# Wayland Setup for Capture Agent

The capture agent supports both X11 and Wayland display servers. On Wayland (default on Ubuntu 22.04+), a GNOME Shell extension is required for window tracking since `xdotool`/`xprop` do not work under Wayland.

## Requirements

- GNOME Shell 45+ (Ubuntu 22.04 ships GNOME 42, Ubuntu 24.04 ships GNOME 46)
- `gnome-extensions` CLI (included with GNOME Shell)
- Python 3.11+

## Installation

### 1. Install the GNOME Shell extension

```bash
bash scripts/install-gnome-extension.sh
```

This copies the extension to `~/.local/share/gnome-shell/extensions/insight-monitor@insight-monitor/` and enables it.

### 2. Restart GNOME Shell

- **Xorg session**: Press `Alt+F2`, type `r`, press Enter.
- **Wayland session**: Log out and log back in.

### 3. Enable autostart (optional)

To auto-enable the extension on login:

```bash
mkdir -p ~/.config/autostart
cp scripts/insight-monitor-extension.desktop ~/.config/autostart/
```

## How It Works

1. The GNOME Shell extension (`capture/gnome-extension/`) monitors the focused window
2. On focus change, it writes window metadata (title, WM class, PID) to `/tmp/insight-window.json`
3. `WaylandWindowTracker` in `capture/window_tracker.py` polls this file to get the active window

## Verification

After installation and Shell restart:

```bash
# Check that the extension is writing data
cat /tmp/insight-window.json

# Should show something like:
# {"title": "Terminal", "wm_class": "gnome-terminal-server", "pid": 1234}
```

Then run the capture agent:

```bash
npm run capture
```

The logs should show window tracking events with title and process info.

## Troubleshooting

### Extension not found

```bash
gnome-extensions list
# Should include "insight-monitor@insight-monitor"
```

If not listed, verify the extension files are in `~/.local/share/gnome-shell/extensions/insight-monitor@insight-monitor/`.

### `/tmp/insight-window.json` is empty or stale

- Make sure the extension is enabled: `gnome-extensions info insight-monitor@insight-monitor`
- Restart GNOME Shell (see above)
- Check GNOME Shell logs: `journalctl -f -o cat /usr/bin/gnome-shell`

### Permission denied

The extension runs in the GNOME Shell process context (your user). `/tmp/insight-window.json` should be writable by your user.

## Known Limitations

- Only GNOME Shell is supported (not KDE, Sway, or other Wayland compositors)
- GNOME Shell 45+ required (uses ESM import syntax for extensions)
- The extension tracks the focused window only — not all open windows
- Browser tab URL detection requires the browser to include the URL in the window title
