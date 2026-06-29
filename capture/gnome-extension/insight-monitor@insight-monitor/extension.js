const St = imports.gi.St;
const Shell = imports.gi.Shell;
const Main = imports.ui.main;
const GLib = imports.gi.GLib;
const Gio = imports.gi.Gio;

const WINDOW_JSON_PATH = '/tmp/insight-window.json';

let _focusHandlerId = null;

function _onFocusWindowChanged(display) {
    let focusedWindow = display.focus_window;
    
    let data = {
        title: null,
        wm_class: null,
        pid: null,
    };

    if (focusedWindow) {
        data.title = focusedWindow.title || null;
        data.wm_class = focusedWindow.wm_class || null;
        
        let pid = Shell.WindowTracker.get_default().get_window_pid(focusedWindow);
        data.pid = pid > 0 ? pid : null;
    }

    let json = JSON.stringify(data, null, 0);
    GLib.file_set_contents(WINDOW_JSON_PATH, json);
}

function enable() {
    _focusHandlerId = global.display.connect('notify::focus-window', _onFocusWindowChanged);
    _onFocusWindowChanged(global.display);
}

function disable() {
    if (_focusHandlerId !== null) {
        global.display.disconnect(_focusHandlerId);
        _focusHandlerId = null;
    }
    
    let file = Gio.File.new_for_path(WINDOW_JSON_PATH);
    if (file.query_exists(null)) {
        file.delete(null);
    }
}
