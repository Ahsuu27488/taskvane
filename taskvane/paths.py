import os
import sys

# When frozen by PyInstaller, bundled data lives in sys._MEIPASS.
BASE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UI_DIR = os.path.join(BASE, "ui")
LHM_DIR = os.path.join(BASE, "lib", "lhm")
PKG_DIR = os.path.join(BASE, "taskvane")
PAWNIO_SETUP = os.path.join(BASE, "lib", "pawnio", "PawnIO_setup.exe")
ICON = os.path.join(BASE, "assets", "icon.ico")
APP_DIR = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(BASE + os.sep)

# Portable build: a "portable.txt" next to Taskvane.exe keeps settings, logs and the
# WebView2 profile in .\data beside the exe instead of %APPDATA%, so nothing is left behind.
PORTABLE = os.path.exists(os.path.join(APP_DIR, "portable.txt"))
if PORTABLE:
    DATA_DIR = os.path.join(APP_DIR, "data")
else:
    DATA_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "Taskvane")
    # One-time migration from the app's pre-release name ("PC Monitor").
    _old = os.path.join(os.environ.get("APPDATA", ""), "PCMonitor", "settings.json")
    if not os.path.exists(DATA_DIR) and os.path.exists(_old):
        try:
            import shutil
            os.makedirs(DATA_DIR)
            shutil.copy2(_old, os.path.join(DATA_DIR, "settings.json"))
        except OSError:
            pass
try:
    os.makedirs(DATA_DIR, exist_ok=True)
except OSError:  # portable copy on a read-only location: fall back to %APPDATA%
    PORTABLE = False
    DATA_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "Taskvane")
    os.makedirs(DATA_DIR, exist_ok=True)
