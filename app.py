"""Taskvane - native Windows app for live usage, temperatures and power."""
import csv
import logging
import ctypes
import json
import os
import sys
import threading
import time
import webbrowser
from ctypes import wintypes

import webview
from PIL import Image, ImageDraw, ImageFont
import pystray

from taskvane import actions
from taskvane.log import LOG_FILE, log, setup as setup_logging
from taskvane.monitor import Monitor, is_admin
from taskvane.paths import DATA_DIR, ICON, PORTABLE, UI_DIR

VERSION = "1.2.1"

APP_TITLE = "Taskvane"
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
DEFAULTS = {
    "unit": "C", "close_to_tray": True, "tray_metric": "cpu",
    "alerts": {"enabled": True, "cpu_temp": 90, "gpu_temp": 85, "mem": 90, "battery_low": 15, "cpu_load": 95},
    "window": {"width": 1280, "height": 820},
    "mini": {"x": None, "y": None},
}

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


def load_settings():
    s = json.loads(json.dumps(DEFAULTS))
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            saved = json.load(f)
        for k, v in saved.items():
            if isinstance(v, dict) and isinstance(s.get(k), dict):
                s[k].update(v)
            else:
                s[k] = v
    except Exception:
        pass
    return s


def write_settings(s):
    tmp = SETTINGS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2)
    os.replace(tmp, SETTINGS_FILE)


# ------------------------------------------------------------ single instance

ERROR_ALREADY_EXISTS = 183


ERROR_ACCESS_DENIED = 5
# Kernel objects shared between a normal and an elevated instance need an explicit
# DACL (everyone) and a low mandatory label, or the lower-integrity side gets
# "access denied" and can't see/signal the other one.
SHARED_SDDL = "D:(A;;GA;;;WD)S:(ML;;NW;;;LW)"


class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [("nLength", wintypes.DWORD), ("lpSecurityDescriptor", ctypes.c_void_p), ("bInheritHandle", wintypes.BOOL)]


def _shared_sa():
    sd = ctypes.c_void_p()
    if not ctypes.windll.advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW(SHARED_SDDL, 1, ctypes.byref(sd), None):
        return None
    return SECURITY_ATTRIBUTES(ctypes.sizeof(SECURITY_ATTRIBUTES), sd, False)


kernel32.CreateMutexW.restype = wintypes.HANDLE
kernel32.CreateEventW.restype = wintypes.HANDLE
kernel32.OpenEventW.restype = wintypes.HANDLE
QUIT_EVENT = r"Local\TaskvaneQuit"


def acquire_instance_lock(wait):
    """Return a mutex handle, or None if another instance (any elevation) owns it."""
    deadline = time.time() + (30 if wait else 0)
    sa = _shared_sa()
    while True:
        h = kernel32.CreateMutexW(ctypes.byref(sa) if sa else None, False, r"Local\TaskvaneSingleInstance")
        err = kernel32.GetLastError()
        if h and err != ERROR_ALREADY_EXISTS:
            return h
        if h:
            kernel32.CloseHandle(h)
        # ERROR_ACCESS_DENIED: an elevated instance created it without a shared DACL
        if err not in (ERROR_ALREADY_EXISTS, ERROR_ACCESS_DENIED) or time.time() >= deadline:
            return None
        time.sleep(0.3)


def signal_quit():
    """`Taskvane.exe --quit`: ask the running instance (even an elevated one) to exit."""
    h = kernel32.OpenEventW(0x0002, False, QUIT_EVENT)  # EVENT_MODIFY_STATE
    if not h:
        return False
    kernel32.SetEvent(h)
    kernel32.CloseHandle(h)
    # Block until it has really exited (its instance lock is free), so an installer
    # or uninstaller can safely replace/delete the files right after we return.
    deadline = time.time() + 10
    while time.time() < deadline:
        lock = acquire_instance_lock(wait=False)
        if lock:
            kernel32.CloseHandle(lock)
            time.sleep(0.5)  # let its sensor helper (holds DLLs open) finish exiting too
            return True
        time.sleep(0.2)
    log.warning("--quit: running instance did not exit within 10s")
    return False


def focus_existing():
    hwnd = user32.FindWindowW(None, APP_TITLE)
    if hwnd:
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        user32.SetForegroundWindow(hwnd)


# ------------------------------------------------------------ window chrome

def fit_to_work_area(width, height, frac=0.92):
    """Clamp a window size to the desktop work area.

    Must run before webview.start(): until then the process is DPI-unaware, so the
    work area comes back in the same scaled units pywebview uses for window sizes.
    """
    rect = wintypes.RECT()
    if user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0):  # SPI_GETWORKAREA
        width = min(width, int((rect.right - rect.left) * frac))
        height = min(height, int((rect.bottom - rect.top) * frac))
    return max(width, 900), max(height, 600)

class MONITORINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", wintypes.RECT), ("rcWork", wintypes.RECT), ("dwFlags", wintypes.DWORD)]


def center_on_monitor(hwnd):
    """Center the window in its monitor's work area (physical pixels, async so it can't deadlock)."""
    user32.MonitorFromWindow.restype = wintypes.HMONITOR
    mon = user32.MonitorFromWindow(hwnd, 2)  # MONITOR_DEFAULTTONEAREST
    mi = MONITORINFO(ctypes.sizeof(MONITORINFO))
    r = wintypes.RECT()
    if not (mon and user32.GetMonitorInfoW(mon, ctypes.byref(mi)) and user32.GetWindowRect(hwnd, ctypes.byref(r))):
        return
    wa, w, h = mi.rcWork, r.right - r.left, r.bottom - r.top
    x = wa.left + max(0, (wa.right - wa.left - w) // 2)
    y = wa.top + max(0, (wa.bottom - wa.top - h) // 2)
    # SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE | SWP_ASYNCWINDOWPOS
    user32.SetWindowPos(hwnd, None, x, y, 0, 0, 0x0001 | 0x0004 | 0x0010 | 0x4000)


def style_window(window, caption=0x001C1A1A):
    """Dark title bar + matching caption colour, and the app icon."""
    try:
        hwnd = window.native.Handle.ToInt64()
        dwm = ctypes.windll.dwmapi
        on = ctypes.c_int(1)
        dwm.DwmSetWindowAttribute(wintypes.HWND(hwnd), 20, ctypes.byref(on), 4)   # immersive dark mode
        color = ctypes.c_int(caption)                                              # COLORREF 0x00BBGGRR
        dwm.DwmSetWindowAttribute(wintypes.HWND(hwnd), 35, ctypes.byref(color), 4)  # caption colour
        border = ctypes.c_int(0x00332F2E)
        dwm.DwmSetWindowAttribute(wintypes.HWND(hwnd), 34, ctypes.byref(border), 4)
    except Exception:
        pass
    # Post (not send) WM_SETICON: touching the WinForms Icon property from this
    # event thread does a synchronous cross-thread call and deadlocks the UI.
    try:
        load = user32.LoadImageW
        load.restype = wintypes.HANDLE
        load.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT, ctypes.c_int, ctypes.c_int, wintypes.UINT]
        big = load(None, ICON, 1, 32, 32, 0x10)    # IMAGE_ICON, LR_LOADFROMFILE
        small = load(None, ICON, 1, 16, 16, 0x10)
        user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        user32.PostMessageW(hwnd, 0x0080, 1, big)    # WM_SETICON, ICON_BIG
        user32.PostMessageW(hwnd, 0x0080, 0, small)  # ICON_SMALL
    except Exception:
        pass


# ------------------------------------------------------------ tray icon image

def _font(size):
    for name in ("segoeuib.ttf", "arialbd.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            pass
    return ImageFont.load_default()


STATUS_COLORS = {"good": (12, 163, 12), "warning": (250, 178, 25), "serious": (236, 131, 90), "critical": (208, 59, 59)}


def tray_image(text, level="neutral"):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bg = (57, 135, 229) if level == "neutral" else STATUS_COLORS[level]
    d.rounded_rectangle((0, 0, 63, 63), radius=14, fill=bg)
    size = 40 if len(text) <= 2 else 30
    f = _font(size)
    box = d.textbbox((0, 0), text, font=f)
    w, h = box[2] - box[0], box[3] - box[1]
    d.text(((64 - w) / 2 - box[0], (64 - h) / 2 - box[1]), text, font=f, fill=(255, 255, 255))
    return img


# ------------------------------------------------------------ app

class App:
    def __init__(self, start_hidden):
        self.settings = load_settings()
        self.monitor = Monitor()
        self.monitor.start()
        self.quitting = False
        self.start_hidden = start_hidden
        self.mini = None
        self.tray = None
        self.last_alert = {}
        self.notice = None
        self.pawnio = actions.pawnio_status()
        self.api = Api(self)
        width, height = fit_to_work_area(self.settings["window"].get("width", 1280), self.settings["window"].get("height", 820))
        self.window = webview.create_window(
            APP_TITLE, os.path.join(UI_DIR, "index.html"), js_api=self.api,
            width=width, height=height, min_size=(900, 600),
            background_color="#111214", hidden=start_hidden, text_select=False)
        self.window.events.shown += self.on_shown
        self.window.events.closing += self.on_closing
        self.window.events.resized += self.on_resized

    # ---- window events
    def on_shown(self):
        style_window(self.window, 0x00141211)
        if not self.start_hidden:
            # Run after this event returns: the UI thread waits on shown handlers,
            # so synchronous window calls made from here would deadlock.
            threading.Timer(0.25, self._present_window).start()

    def _present_window(self):
        """Open as a normal, centered, focused window even if a launcher (UAC
        relaunch, py shim, minimized console) handed us a minimized show state."""
        try:
            hwnd = wintypes.HWND(self.window.native.Handle.ToInt64())
            iconic = bool(user32.IsIconic(hwnd))
            if iconic:
                user32.ShowWindow(hwnd, 9)  # SW_RESTORE (sync: UI thread is free now)
            center_on_monitor(hwnd)
            user32.SetForegroundWindow(hwnd)
            r = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(r))
            log.info("window shown (was minimized: %s) at %d,%d %dx%d", iconic, r.left, r.top, r.right - r.left, r.bottom - r.top)
        except Exception:
            log.exception("presenting window failed")

    def on_closing(self):
        if self.quitting or not self.settings.get("close_to_tray", True):
            self.quitting = True
            self._teardown()
            return True
        self.window.hide()
        if not self.settings.get("_tray_hint_shown"):
            self.settings["_tray_hint_shown"] = True
            write_settings(self.settings)
            self.notify("Taskvane is still running", "It's in the notification area. Right-click the icon to quit.")
        return False

    def on_resized(self, width, height):
        if width > 400 and height > 300:
            self.settings["window"] = {"width": width, "height": height}

    def show_main(self, page=None):
        self.window.show()
        self.window.restore()
        if page:
            self.window.evaluate_js(f"window.taskvaneGo && taskvaneGo({json.dumps(page)})")
        try:
            hwnd = self.window.native.Handle.ToInt64()
            user32.SetForegroundWindow(wintypes.HWND(hwnd))
        except Exception:
            pass

    def toggle_mini(self):
        if self.mini is not None:
            try:
                r = wintypes.RECT()
                if user32.GetWindowRect(wintypes.HWND(self.mini.native.Handle.ToInt64()), ctypes.byref(r)):
                    self.settings["mini"] = {"x": r.left, "y": r.top}  # physical pixels
                    write_settings(self.settings)
                self.mini.destroy()
            except Exception:
                pass
            self.mini = None
            return False
        self.mini = webview.create_window(
            "Taskvane Mini", os.path.join(UI_DIR, "mini.html"), js_api=self.api, width=250, height=168,
            resizable=False, frameless=True, easy_drag=False, on_top=True, background_color="#1a1a1c", focus=False)
        self.mini.events.shown += self._place_mini
        self.mini.events.closed += lambda: setattr(self, "mini", None)
        return True

    def _place_mini(self):
        """Put the widget at its saved spot, or bottom-right of the work area.

        Done with Win32 in physical pixels: pywebview scales x/y by the display
        scale factor, which pushes a physical-pixel position off screen.
        """
        try:
            hwnd = wintypes.HWND(self.mini.native.Handle.ToInt64())
            r = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(r))
            w, h = r.right - r.left, r.bottom - r.top
            pos = self.settings.get("mini") or {}
            x, y = pos.get("x"), pos.get("y")
            user32.MonitorFromPoint.restype = wintypes.HMONITOR
            if x is None or not user32.MonitorFromPoint(wintypes.POINT(x + 20, y + 20), 0):  # off every monitor?
                wa = wintypes.RECT()
                user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(wa), 0)
                x, y = wa.right - w - 16, wa.bottom - h - 16
            user32.SetWindowPos(hwnd, None, x, y, 0, 0, 0x0001 | 0x0004 | 0x0010 | 0x4000)
        except Exception:
            pass

    def watch_pawnio(self):
        """After sending the user to pawnio.eu, notice when the driver gets installed so the
        UI moves on to "Restart as administrator" (or, when already elevated, starts reading)."""
        if getattr(self, "_pawnio_watch", None) and self._pawnio_watch.is_alive():
            return

        def watch():
            for _ in range(600):  # 30 minutes
                time.sleep(3)
                if self.quitting:
                    return
                pw = actions.pawnio_status()
                if pw["installed"] and not pw["outdated"]:
                    log.info("PawnIO installed: %s", pw)
                    self.pawnio = pw
                    if self.monitor.admin:
                        self.monitor.lhm.restart()
                    return
        self._pawnio_watch = threading.Thread(target=watch, name="pawnio-watch", daemon=True)
        self._pawnio_watch.start()

    def quit(self):
        log.info("quit requested")
        self.quitting = True
        # Failsafe: never linger holding the single-instance lock (an elevated
        # relaunch is waiting for it), even if a window teardown stalls.
        threading.Timer(4.0, lambda: (log.warning("forced exit after quit timeout"), os._exit(0))).start()
        self._teardown()
        for w in list(webview.windows):
            try:
                w.destroy()
            except Exception:
                pass

    def _teardown(self):
        try:
            write_settings(self.settings)
        except Exception:
            pass
        if self.tray:
            try:
                self.tray.stop()
            except Exception:
                pass
        self.monitor.lhm.close()

    # ---- tray
    def start_tray(self):
        menu = pystray.Menu(
            pystray.MenuItem("Open Taskvane", lambda: self.show_main(), default=True),
            pystray.MenuItem("Mini widget", lambda: self.toggle_mini(), checked=lambda _: self.mini is not None),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Processes", lambda: self.show_main("processes")),
            pystray.MenuItem("Power", lambda: self.show_main("power")),
            pystray.MenuItem("Sensors", lambda: self.show_main("sensors")),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", lambda: self.quit()),
        )
        self.tray = pystray.Icon("Taskvane", tray_image("--"), APP_TITLE, menu)
        threading.Thread(target=self.tray.run, daemon=True).start()
        threading.Thread(target=self._tray_loop, daemon=True).start()

    def _tray_loop(self):
        time.sleep(2)
        while not self.quitting:
            try:
                self._update_tray()
                self._check_alerts()
            except Exception:
                pass
            time.sleep(2)

    def _update_tray(self):
        snap = self.monitor.snapshot()
        s, hw = snap["system"], snap["hw"]
        if not s:
            return
        gpus = hw.get("gpus") or []
        g = next((x for x in gpus if x.get("discrete")), gpus[0] if gpus else None)
        metric = self.settings.get("tray_metric", "cpu")
        f = self.settings.get("unit") == "F"
        conv = lambda c: c * 9 / 5 + 32 if f else c
        level = "neutral"
        if metric == "cpu_temp" and hw.get("cpu_temp") is not None:
            text, level = f"{conv(hw['cpu_temp']):.0f}", self._temp_level(hw["cpu_temp"], 85)
        elif metric == "gpu_temp" and g and g.get("temp") is not None:
            text, level = f"{conv(g['temp']):.0f}", self._temp_level(g["temp"], 83)
        elif metric == "power" and hw.get("power_w") is not None:
            text = f"{hw['power_w']:.0f}"
        elif metric == "mem":
            text = f"{s['mem']['percent']:.0f}"
        else:
            text = f"{s['cpu']:.0f}"
        self.tray.icon = tray_image(text, level)
        tip = [f"CPU {s['cpu']:.0f}%" + (f" · {conv(hw['cpu_temp']):.0f}°" if hw.get("cpu_temp") else ""),
               f"Memory {s['mem']['percent']:.0f}%"]
        if g:
            tip.append(f"GPU {g.get('load') or 0:.0f}%" + (f" · {conv(g['temp']):.0f}°" if g.get("temp") is not None else ""))
        if hw.get("power_w") is not None:
            tip.append(f"Power {hw['power_w']:.1f} W")
        b = hw.get("battery") or {}
        if b.get("percent") is not None:
            tip.append(f"Battery {b['percent']:.0f}%" + (" (plugged in)" if b.get("plugged") else ""))
        self.tray.title = "\n".join(tip)[:127]

    @staticmethod
    def _temp_level(c, hot):
        return "critical" if c >= hot + 10 else "serious" if c >= hot else "warning" if c >= hot - 15 else "good"

    def notify(self, title, msg):
        if self.tray:
            try:
                self.tray.notify(msg, title)
            except Exception:
                pass

    def _check_alerts(self):
        a = self.settings.get("alerts", {})
        if not a.get("enabled"):
            return
        snap = self.monitor.snapshot()
        s, hw = snap["system"], snap["hw"]
        gpus = hw.get("gpus") or []
        unit = "°F" if self.settings.get("unit") == "F" else "°C"
        conv = (lambda c: c * 9 / 5 + 32) if unit == "°F" else (lambda c: c)
        checks = []
        if hw.get("cpu_temp") is not None and hw["cpu_temp"] >= a.get("cpu_temp", 999):
            checks.append(("cpu_temp", "CPU is running hot", f"CPU temperature is {conv(hw['cpu_temp']):.0f}{unit}."))
        for g in gpus:
            if g.get("temp") is not None and g["temp"] >= a.get("gpu_temp", 999):
                checks.append(("gpu_temp", "GPU is running hot", f"{g['name']} is at {conv(g['temp']):.0f}{unit}."))
        if s["mem"]["percent"] >= a.get("mem", 999):
            checks.append(("mem", "Memory almost full", f"{s['mem']['percent']:.0f}% of memory is in use."))
        b = hw.get("battery") or {}
        if b.get("percent") is not None and not b.get("plugged") and b["percent"] <= a.get("battery_low", -1):
            checks.append(("battery", "Battery low", f"{b['percent']:.0f}% remaining."))
        hist = list(self.monitor.history["cpu"])[-60:]
        if len(hist) >= 60 and sum(hist) / len(hist) >= a.get("cpu_load", 999):
            top = sorted(self.monitor.get_processes(), key=lambda p: -p["cpu"])
            top = next((p for p in top if p["pid"] != 0), None)
            checks.append(("cpu_load", "CPU busy for over a minute",
                           f"Average {sum(hist) / len(hist):.0f}%." + (f" Top process: {top['desc'] or top['name']}." if top else "")))
        now = time.time()
        for key, title, msg in checks:
            if now - self.last_alert.get(key, 0) > 600:  # at most once every 10 minutes per alert
                self.last_alert[key] = now
                self.notify(title, msg)

    def run(self):
        self.start_tray()
        # Separate WebView2 profiles per elevation: a profile folder can't be used by
        # browser processes at different integrity levels, and the previous
        # (non-elevated) instance's WebView2 may still be shutting down.
        storage = os.path.join(DATA_DIR, "webview-admin" if self.monitor.admin else "webview")
        threading.Thread(target=self._quit_event_loop, name="quit-event", daemon=True).start()
        threading.Timer(20, self._check_ui_connected).start()
        webview.start(gui="edgechromium", debug="--debug" in sys.argv, private_mode=False, storage_path=storage)

    def _quit_event_loop(self):
        sa = _shared_sa()
        ev = kernel32.CreateEventW(ctypes.byref(sa) if sa else None, True, False, QUIT_EVENT)
        if not ev:
            log.warning("could not create quit event (error %s)", kernel32.GetLastError())
            return
        kernel32.WaitForSingleObject(ev, 0xFFFFFFFF)
        log.info("quit signalled by another process")
        self.quit()

    def _check_ui_connected(self):
        if not self.api._connected and not self.quitting and not self.start_hidden:
            log.error("UI has not connected 20s after start: WebView2 failed to load the interface")


class Api:
    """Methods callable from JavaScript as window.pywebview.api.<name>()."""

    def __init__(self, app):
        self._app = app
        self._connected = False

    # data
    def get_stats(self):
        snap = self._app.monitor.snapshot()
        snap["version"] = VERSION
        snap["pawnio"] = self._app.pawnio
        return snap

    def get_history(self, seconds):
        return self._app.monitor.get_history(seconds)

    def get_processes(self):
        return self._app.monitor.get_processes()

    def get_sensors(self):
        return self._app.monitor.get_sensors()

    def reset_minmax(self):
        self._app.monitor.lhm.reset_minmax()
        return True

    # processes
    def process_details(self, pid):
        return actions.process_details(int(pid))

    def end_process(self, pid, tree=False):
        return actions.end_process(int(pid), bool(tree))

    def set_priority(self, pid, level):
        return actions.set_priority(int(pid), level)

    def open_location(self, path):
        return actions.open_location(path)

    def open_url(self, url):
        if isinstance(url, str) and url.startswith("https://"):
            webbrowser.open(url)
        return True

    # startup / power
    def startup_apps(self):
        return actions.startup_apps()

    def set_startup(self, item_id, enabled):
        return actions.set_startup_enabled(item_id, bool(enabled))

    # settings
    def get_settings(self):
        s = dict(self._app.settings)
        s["admin_auto"] = actions.task_exists(actions.ADMIN_TASK)
        s["autostart"] = actions.get_autostart() or actions.task_exists(actions.ADMIN_LOGON_TASK)
        s["is_admin"] = self._app.monitor.admin
        return s

    def save_settings(self, new):
        try:
            cur = self.get_settings()
            want_admin, want_auto = bool(new.get("admin_auto")), bool(new.get("autostart"))
            if (want_admin, want_auto) != (cur["admin_auto"], cur["autostart"]):
                r = actions.configure_startup(want_admin, want_auto)
                if not r["ok"]:
                    return r
            s = self._app.settings
            for k in ("unit", "close_to_tray", "tray_metric"):
                if k in new:
                    s[k] = new[k]
            if isinstance(new.get("alerts"), dict):
                s["alerts"].update({k: v for k, v in new["alerts"].items() if k in DEFAULTS["alerts"]})
            write_settings(s)
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def export_history(self):
        save = getattr(getattr(webview, "FileDialog", None), "SAVE", None) or webview.SAVE_DIALOG
        res = self._app.window.create_file_dialog(save, save_filename=time.strftime("taskvane-%Y%m%d-%H%M.csv"),
                                                  file_types=("CSV files (*.csv)",))
        if not res:
            return {"ok": False}
        path = res if isinstance(res, str) else res[0]
        h = self._app.monitor.get_history(3600)
        keys = [k for k in h if k != "t"]
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["time"] + keys)
            for i, t in enumerate(h["t"]):
                w.writerow([time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))] + [h[k][i] for k in keys])
        return {"ok": True, "path": path}

    # app
    def relaunch_admin(self):
        # Prefer the elevated task when it exists: no UAC prompt.
        if actions.task_exists(actions.ADMIN_TASK) and actions.run_admin_task():
            threading.Timer(0.3, self._app.quit).start()
            return {"ok": True}
        if actions.relaunch_as_admin("--relaunch"):
            threading.Timer(0.3, self._app.quit).start()
            return {"ok": True}
        return {"ok": False}

    def pawnio_status(self):
        return actions.pawnio_status()

    def enable_cpu_sensors(self):
        """CPU temperature/power need the PawnIO driver + admin. PawnIO isn't bundled (see
        actions.PAWNIO_URL), so a missing or old driver opens its author's site."""
        pw = self._app.pawnio = actions.pawnio_status()
        if not pw["installed"] or pw["outdated"]:
            webbrowser.open(actions.PAWNIO_URL)
            self._app.watch_pawnio()
            return {"ok": True, "opened": True}
        if not self._app.monitor.admin:
            return self.relaunch_admin()
        self._app.monitor.lhm.restart()
        return {"ok": True}

    def take_notice(self):
        # called once by the UI at boot: proves WebView2 + the JS bridge work
        if not self._connected:
            self._connected = True
            log.info("UI connected")
        n, self._app.notice = self._app.notice, None
        return n

    def open_log(self):
        os.startfile(LOG_FILE) if os.path.exists(LOG_FILE) else None
        return True

    def log_js_error(self, msg):
        log.error("UI error: %s", str(msg)[:2000])
        return True

    def toggle_mini(self):
        return self._app.toggle_mini()

    def show_main(self):
        self._app.show_main()
        return True

    def resize_mini(self, css_height):
        m = self._app.mini
        if m is not None and 60 < css_height < 400:
            m.resize(250, int(css_height))
        return True


def clear_stale_ui_cache():
    """WebView2 caches the UI's html/js/css over its local HTTP server, so after an
    update users would keep seeing the old interface. Fingerprint the UI files and
    drop the HTTP caches whenever they change."""
    import hashlib
    import shutil
    h = hashlib.sha1(VERSION.encode())
    for name in sorted(os.listdir(UI_DIR)):
        with open(os.path.join(UI_DIR, name), "rb") as f:
            h.update(name.encode() + f.read())
    stamp = h.hexdigest()
    stamp_file = os.path.join(DATA_DIR, "ui.stamp")
    try:
        with open(stamp_file) as f:
            if f.read().strip() == stamp:
                return
    except OSError:
        pass
    for folder in ("webview", "webview-admin"):
        profile = os.path.join(DATA_DIR, folder, "EBWebView", "Default")
        for sub in ("Cache", "Code Cache", "Service Worker"):
            shutil.rmtree(os.path.join(profile, sub), ignore_errors=True)
    with open(stamp_file, "w") as f:
        f.write(stamp)
    log.info("UI changed; cleared WebView2 cache")


def main():
    setup_logging()
    logging.getLogger("pywebview").addHandler(log.handlers[0])  # WebView2 / bridge errors into our log
    if "--quit" in sys.argv:
        sys.exit(0 if signal_quit() else 1)
    if "--set-startup" in sys.argv:
        # Used by the installer/uninstaller: --set-startup <always_admin 0|1> <autostart 0|1>
        i = sys.argv.index("--set-startup")
        admin_auto, autostart = (sys.argv[i + 1:i + 3] + ["0", "0"])[:2]
        r = actions.configure_startup(admin_auto == "1", autostart == "1")
        log.info("--set-startup %s %s -> %s", admin_auto, autostart, r)
        sys.exit(0 if r["ok"] else 1)
    admin = is_admin()
    log.info("Taskvane %s starting: admin=%s frozen=%s portable=%s data=%s argv=%s", VERSION, admin, getattr(sys, "frozen", False), PORTABLE, DATA_DIR, sys.argv[1:])
    # --from-task: started by the elevated scheduled task, possibly while the
    # instance that triggered it is still shutting down, so wait like a relaunch.
    relaunch = "--relaunch" in sys.argv or "--from-task" in sys.argv
    t0 = time.time()
    lock = acquire_instance_lock(wait=relaunch)
    if not lock:
        log.info("another instance owns the lock%s; focusing it and exiting",
                 f" (waited {time.time() - t0:.1f}s)" if relaunch else "")
        focus_existing()
        return
    if relaunch:
        log.info("previous instance released the lock after %.1fs", time.time() - t0)

    # "Always start as administrator": hand off to the elevated task (no UAC prompt).
    if not admin and not relaunch and "--no-elevate" not in sys.argv and actions.task_exists(actions.ADMIN_TASK):
        kernel32.CloseHandle(lock)
        if actions.run_admin_task():
            log.info("handed off to the elevated task")
            return
        log.warning("elevated task failed to start; continuing without admin rights")
        lock = acquire_instance_lock(wait=True)
        if not lock:
            return

    log.info("PawnIO: %s", actions.pawnio_status())
    try:
        clear_stale_ui_cache()
    except Exception:
        log.exception("clearing UI cache failed")

    app = App(start_hidden="--minimized" in sys.argv)
    app.run()
    log.info("exiting")
    os._exit(0)  # don't wait on background threads


if __name__ == "__main__":
    main()
