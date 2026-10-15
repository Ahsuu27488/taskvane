"""Hardware sensors via LibreHardwareMonitorLib, hosted in a separate helper process.

The helper (lhm_host.ps1, run by Windows PowerShell 5.1 on .NET Framework) prints one
JSON line per second. Keeping it out of process means a driver or .NET fault can't
take the app down; if the helper dies it is restarted.

Without admin rights it still reports GPU, battery, memory and load sensors.
CPU temperatures / package power additionally need admin and the PawnIO driver.
"""
import json
import os
import subprocess
import threading
import time

from .log import log
from .paths import LHM_DIR, PKG_DIR

HOST_SCRIPT = os.path.join(PKG_DIR, "lhm_host.ps1")
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
POWERSHELL = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), r"System32\WindowsPowerShell\v1.0\powershell.exe")


class LHM:
    def __init__(self):
        self.ok = os.path.exists(os.path.join(LHM_DIR, "LibreHardwareMonitorLib.dll"))
        self.error = None if self.ok else "LibreHardwareMonitorLib.dll not found in " + LHM_DIR
        self.restarts = 0
        self._sensors = []
        self._minmax = {}
        self._lock = threading.Lock()
        self._proc = None
        self._stopped = False
        self._logged_first = False
        if self.ok:
            threading.Thread(target=self._supervise, name="lhm-supervisor", daemon=True).start()
        else:
            log.error(self.error)

    def _supervise(self):
        backoff = 2
        while not self._stopped:
            started = time.time()
            try:
                self._proc = subprocess.Popen(
                    [POWERSHELL, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", HOST_SCRIPT,
                     "-LibDir", LHM_DIR, "-ParentPid", str(os.getpid())],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
                    creationflags=NO_WINDOW, text=True, encoding="utf-8", errors="replace", bufsize=1)
                log.info("sensor helper started (pid %s)", self._proc.pid)
                threading.Thread(target=self._drain_stderr, args=(self._proc,), name="lhm-stderr", daemon=True).start()
                self._logged_first = False
                for line in self._proc.stdout:
                    try:
                        msg = json.loads(line)
                    except ValueError:
                        continue
                    if "error" in msg:
                        self.error = msg["error"]
                        log.error("sensor helper error: %s", self.error)
                        continue
                    self.error = None
                    self._ingest(msg.get("sensors") or [])
                code = self._proc.wait()
                if not self._stopped:
                    log.warning("sensor helper exited with code %s after %.0fs", code, time.time() - started)
            except Exception as e:
                self.error = f"{type(e).__name__}: {e}"
                log.exception("sensor helper failed to start")
            if self._stopped:
                break
            self.restarts += 1
            backoff = 1 if getattr(self, "_restart_requested", False) else (2 if time.time() - started > 60 else min(backoff * 2, 60))
            self._restart_requested = False
            with self._lock:
                self._sensors = []
            time.sleep(backoff)

    @staticmethod
    def _drain_stderr(proc):
        for line in proc.stderr:
            line = line.strip()
            if line:
                log.warning("sensor helper stderr: %s", line[:500])

    def _ingest(self, sensors):
        for s in sensors:
            v = s["value"]
            mn, mx = self._minmax.get(s["id"], (v, v))
            mn, mx = min(mn, v), max(mx, v)
            self._minmax[s["id"]] = (mn, mx)
            s["min"], s["max"] = mn, mx
        if not self._logged_first:
            self._logged_first = True
            cpu_t = [s["value"] for s in sensors if s["hw_type"] == "Cpu" and s["type"] == "Temperature"]
            cpu_p = [s["value"] for s in sensors if s["hw_type"] == "Cpu" and s["type"] == "Power"]
            log.info("first sensor reading: %d sensors; CPU temps %s; CPU power %s", len(sensors), cpu_t[:3] or "none",
                     [round(v, 1) for v in cpu_p[:2]] or "none")
        with self._lock:
            self._sensors = sensors

    def read(self):
        with self._lock:
            return self._sensors

    def restart(self):
        """Restart the helper (e.g. after PawnIO was installed) so LHM re-opens its drivers."""
        self._restart_requested = True
        p = self._proc
        if p and p.poll() is None:
            log.info("restarting sensor helper")
            try:
                p.kill()
            except Exception:
                pass

    def reset_minmax(self):
        self._minmax.clear()

    def close(self):
        self._stopped = True
        if self._proc and self._proc.poll() is None:
            try:
                self._proc.kill()
            except Exception:
                pass
