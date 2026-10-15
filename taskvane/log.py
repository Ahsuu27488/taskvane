"""App log at %APPDATA%\\Taskvane\\taskvane.log (rotates at 1 MB, keeps 2 old files)."""
import logging
import os
import sys
import threading
from logging.handlers import RotatingFileHandler

from .paths import DATA_DIR

LOG_FILE = os.path.join(DATA_DIR, "taskvane.log")
log = logging.getLogger("taskvane")


def setup():
    if log.handlers:
        return log
    log.setLevel(logging.INFO)
    h = RotatingFileHandler(LOG_FILE, maxBytes=1 << 20, backupCount=2, encoding="utf-8")
    h.setFormatter(logging.Formatter("%(asctime)s [%(process)d %(threadName)s] %(levelname)s %(message)s"))
    log.addHandler(h)
    if sys.stderr and not getattr(sys, "frozen", False):
        log.addHandler(logging.StreamHandler(sys.stderr))

    def excepthook(exc_type, exc, tb):
        log.error("Unhandled exception", exc_info=(exc_type, exc, tb))
    sys.excepthook = excepthook
    threading.excepthook = lambda a: log.error("Unhandled exception in %s", a.thread.name if a.thread else "?",
                                               exc_info=(a.exc_type, a.exc_value, a.exc_traceback))
    return log
