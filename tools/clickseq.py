"""Dev test (run elevated for an elevated app): drive Taskvane with a click script.
    python tools/clickseq.py OUTDIR "click:110,328" "wait:2" "snap:name.png" "cmd:powershell ...>file" ...
Coordinates are CSS px relative to the window's top-left (incl. title bar).
"""
import ctypes
import os
import subprocess
import sys
import time
from ctypes import wintypes

user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SNAP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snap.py")
hwnd = user32.FindWindowW(None, "Taskvane")


def widget():
    found = []
    cb_t = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def cb(h, _):
        b = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(h, b, 256)
        if b.value == "Chrome_RenderWidgetHostHWND":
            found.append(h)
        return True
    user32.EnumChildWindows(hwnd, cb_t(cb), 0)
    return found[0]


def rect(h):
    r = wintypes.RECT()
    user32.GetWindowRect(h, ctypes.byref(r))
    return r


rw = widget()
win, wid = rect(hwnd), rect(rw)
scale = (win.right - win.left) / 1280
for step in sys.argv[2:]:
    kind, _, arg = step.partition(":")
    if kind == "click":
        x, y = (int(v) for v in arg.split(","))
        sx, sy = win.left + int(x * scale), win.top + int(y * scale)
        lp = ((sy - wid.top) << 16) | ((sx - wid.left) & 0xFFFF)
        user32.PostMessageW(rw, 0x0201, 1, lp)
        user32.PostMessageW(rw, 0x0202, 0, lp)
    elif kind == "wait":
        time.sleep(float(arg))
    elif kind == "snap":
        subprocess.run([sys.executable, SNAP, "Taskvane", os.path.join(OUT, arg)])
    elif kind == "cmd":
        subprocess.run(arg, shell=True)
