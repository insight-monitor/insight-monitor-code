#!/usr/bin/env bash
set -euo pipefail

EXT_UUID="insight-monitor@insight-monitor"
EXT_DIR="$HOME/.local/share/gnome-shell/extensions/${EXT_UUID}"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../capture/gnome-extension/${EXT_UUID}" && pwd)"
WINDOW_JSON="/tmp/insight-window.json"

info()  { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
ok()    { printf '\033[1;32m==>\033[0m %s\n' "$*"; }
warn()  { printf '\033[1;33m==>\033[0m %s\n' "$*"; }
err()   { printf '\033[1;31m==>\033[0m %s\n' "$*" >&2; }

is_wayland() {
    [ "${XDG_SESSION_TYPE:-}" = "wayland" ]
}

is_gnome() {
    [ "${XDG_CURRENT_DESKTOP:-}" = "${XDG_CURRENT_DESKTOP%:*}GNOME"* ] \
        || [ "${XDG_CURRENT_DESKTOP:-}" = "GNOME" ]
}

usage() {
    cat <<EOF
Usage: $(basename "$0") [COMMAND]

Commands:
    install    Install and enable the GNOME Shell extension (default)
    verify     Verify the extension is writing window data
    remove     Disable and remove the extension files
    help       Show this help

Examples:
    $(basename "$0")            # install + enable
    $(basename "$0") verify     # check if /tmp/insight-window.json exists
    $(basename "$0") remove     # clean removal
EOF
}

# ──────────────────────────────────────────────────────────────────────────────
# install command
# ──────────────────────────────────────────────────────────────────────────────

cmd_install() {
    info "Installing Insight Monitor GNOME Shell extension..."

    if [ ! -d "$SRC_DIR" ]; then
        err "Extension source not found at: $SRC_DIR"
        exit 1
    fi

    mkdir -p "$EXT_DIR"
    cp "$SRC_DIR/extension.js" "$EXT_DIR/"
    cp "$SRC_DIR/metadata.json" "$EXT_DIR/"
    cp "$SRC_DIR/stylesheet.css" "$EXT_DIR/"
    ok "Extension files copied to $EXT_DIR"

    if ! command -v gnome-extensions >/dev/null 2>&1; then
        warn "gnome-extensions CLI not found."
        warn "Install GNOME Shell extensions utility or enable manually."
        print_post_install_instructions
        return 0
    fi

    if gnome-extensions list | grep -q "^${EXT_UUID}$"; then
        info "Extension already registered with this GNOME Shell session."
        if gnome-extensions is-enabled "${EXT_UUID}" >/dev/null 2>&1; then
            ok "Extension is already enabled."
            print_post_install_instructions
            return 0
        fi
        info "Enabling extension..."
        if gnome-extensions enable "${EXT_UUID}" 2>/dev/null; then
            ok "Extension enabled."
            print_post_install_instructions
            return 0
        fi
        warn "Failed to enable extension via CLI."
    else
        # Extension not yet known by running GNOME Shell (Wayland needs reload).
        warn "Extension files installed but not yet known by running GNOME Shell."
        warn "This is expected on Wayland: Shell must reload to discover new extensions."
    fi

    print_post_install_instructions
}

print_post_install_instructions() {
    echo ""
    info "Next steps:"
    if is_wayland; then
        echo "    - Log out and log back in (Wayland sessions cannot restart Shell in-place)"
    else
        echo "    - Press Alt+F2, type 'r', press Enter  (Xorg sessions only)"
    fi
    echo ""
    echo "    Verify with: $(basename "$0") verify"
    echo "    Or manually: cat ${WINDOW_JSON}"
}

# ──────────────────────────────────────────────────────────────────────────────
# verify command
# ──────────────────────────────────────────────────────────────────────────────

cmd_verify() {
    info "Verifying window tracking extension..."

    if [ -f "$WINDOW_JSON" ]; then
        ok "${WINDOW_JSON} exists."
        if [ -s "$WINDOW_JSON" ]; then
            ok "Contents:"
            echo "    $(cat "$WINDOW_JSON")"
        else
            warn "${WINDOW_JSON} exists but is empty."
            warn "  The extension may not be fully loaded yet."
        fi
    else
        warn "${WINDOW_JSON} does not exist."
        warn "  Window tracking is NOT working."
        echo ""
        info "Troubleshooting:"
        echo "    1. Confirm extension files exist:"
        echo "         ls -la ${EXT_DIR}"
        echo "    2. Confirm the extension is enabled:"
        echo "         gnome-extensions info ${EXT_UUID}"
        echo "    3. Log out and back in to allow Shell to load the extension."
        echo "    4. Check GNOME Shell logs:"
        echo "         journalctl -f -o cat /usr/bin/gnome-shell"
    fi

    if command -v gnome-extensions >/dev/null 2>&1; then
        if gnome-extensions list 2>/dev/null | grep -q "^${EXT_UUID}$"; then
            echo ""
            info "Extension status:"
            gnome-extensions info "${EXT_UUID}" 2>/dev/null | sed 's/^/    /'
        else
            warn "Extension not registered with this GNOME Shell session."
            warn "  Log out and log in to make Shell pick up the new files."
        fi
    fi
}

# ──────────────────────────────────────────────────────────────────────────────
# remove command
# ──────────────────────────────────────────────────────────────────────────────

cmd_remove() {
    info "Removing Insight Monitor GNOME Shell extension..."

    if command -v gnome-extensions >/dev/null 2>&1 \
            && gnome-extensions list 2>/dev/null | grep -q "^${EXT_UUID}$"; then
        if gnome-extensions disable "${EXT_UUID}" 2>/dev/null; then
            ok "Extension disabled."
        else
            warn "Failed to disable via CLI (may not be enabled)."
        fi
    fi

    if [ -d "$EXT_DIR" ]; then
        rm -rf "$EXT_DIR"
        ok "Extension files removed from $EXT_DIR"
    else
        warn "Extension directory not present: $EXT_DIR"
    fi

    if [ -f "$WINDOW_JSON" ]; then
        rm -f "$WINDOW_JSON"
        ok "${WINDOW_JSON} deleted."
    fi
}

# ──────────────────────────────────────────────────────────────────────────────
# main
# ──────────────────────────────────────────────────────────────────────────────

CMD="${1:-install}"
case "$CMD" in
    install) cmd_install ;;
    verify)  cmd_verify ;;
    remove)  cmd_remove ;;
    help|-h|--help) usage ;;
    *) err "Unknown command: $CMD"; usage; exit 1 ;;
esac
