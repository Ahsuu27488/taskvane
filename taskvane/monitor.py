"""Background collectors: system usage, processes, hardware sensors, history."""
import ctypes
import re
import subprocess
import threading
import time
from collections import deque

import psutil

from . import ntproc
from .lhm import LHM

NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
HISTORY_LEN = 3600  # one hour at 1 s
HISTORY_KEYS = ("cpu", "mem", "gpu", "cpu_temp", "gpu_temp", "power", "disk_r", "disk_w", "net_up", "net_down")


def is_admin():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def run(cmd, timeout=8):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, creationflags=NO_WINDOW).stdout
    except Exception:
        return ""


# ------------------------------------------------------------ file descriptions

_ver = ctypes.windll.version
_desc_cache = {}


def file_description(path):
    """'chrome.exe' -> 'Google Chrome' using the exe's version resource (cached)."""
    if not path:
        return None
    if path in _desc_cache:
        return _desc_cache[path]
    desc = None
    try:
        size = _ver.GetFileVersionInfoSizeW(path, None)
        if size:
            buf = ctypes.create_string_buffer(size)
            _ver.GetFileVersionInfoW(path, 0, size, buf)
            ptr, ln = ctypes.c_void_p(), ctypes.c_uint()
            if _ver.VerQueryValueW(buf, r"\VarFileInfo\Translation", ctypes.byref(ptr), ctypes.byref(ln)) and ln.value:
                lang, cp = ctypes.cast(ptr, ctypes.POINTER(ctypes.c_ushort * 2)).contents
                sub = rf"\StringFileInfo\{lang:04x}{cp:04x}\FileDescription"
                if _ver.VerQueryValueW(buf, sub, ctypes.byref(ptr), ctypes.byref(ln)) and ln.value:
                    desc = ctypes.wstring_at(ptr, ln.value).rstrip("\x00").strip() or None
    except Exception:
        pass
    _desc_cache[path] = desc
    return desc


# ------------------------------------------------------------ monitor

class Monitor:
    def __init__(self):
        self.lock = threading.Lock()
        self.admin = is_admin()
        self.lhm = LHM()
        self.cpu_name = self._cpu_name()
        self.system = {}
        self.sensors = []
        self.hw = {}
        self.processes = []
        self.history = {k: deque(maxlen=HISTORY_LEN) for k in HISTORY_KEYS + ("t",)}
        self.session_wh = 0.0
        self.session_start = time.time()
        self._threads_started = False

    def start(self):
        if self._threads_started:
            return
        self._threads_started = True
        for fn in (self._system_loop, self._process_loop, self._sensor_loop):
            threading.Thread(target=fn, daemon=True).start()

    # ---------------------------------------------------- system

    def _cpu_name(self):
        out = run(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_Processor).Name"])
        return re.sub(r"\s+", " ", out.strip()) or "CPU"

    def _system_loop(self):
        last_disk, last_net, last_t = psutil.disk_io_counters(), psutil.net_io_counters(), time.time()
        psutil.cpu_percent(percpu=True)
        drives, drives_t = [], 0
        while True:
            time.sleep(1)
            now = time.time()
            dt = max(now - last_t, 1e-3)
            disk, net = psutil.disk_io_counters(), psutil.net_io_counters()
            vm, sw = psutil.virtual_memory(), psutil.swap_memory()
            freq = psutil.cpu_freq()
            cores = psutil.cpu_percent(percpu=True)
            if now - drives_t > 15:
                drives, drives_t = self._drives(), now
            snap = {
                "cpu": sum(cores) / len(cores), "cores": cores,
                "freq": freq.current if freq else None, "freq_max": freq.max if freq else None,
                "cpu_name": self.cpu_name, "logical": psutil.cpu_count(), "physical": psutil.cpu_count(logical=False),
                "mem": {"total": vm.total, "used": vm.total - vm.available, "percent": vm.percent, "available": vm.available},
                "swap": {"total": sw.total, "used": sw.used, "percent": sw.percent},
                "disk_r": (disk.read_bytes - last_disk.read_bytes) / dt if disk else 0,
                "disk_w": (disk.write_bytes - last_disk.write_bytes) / dt if disk else 0,
                "net_up": (net.bytes_sent - last_net.bytes_sent) / dt,
                "net_down": (net.bytes_recv - last_net.bytes_recv) / dt,
                "net_total": {"sent": net.bytes_sent, "recv": net.bytes_recv},
                "drives": drives, "boot": psutil.boot_time(), "procs": len(psutil.pids()),
            }
            last_disk, last_net, last_t = disk, net, now
            with self.lock:
                self.system = snap
                hw = self.hw
                h = self.history
                h["t"].append(now)
                h["cpu"].append(round(snap["cpu"], 1))
                h["mem"].append(round(vm.percent, 1))
                h["disk_r"].append(snap["disk_r"])
                h["disk_w"].append(snap["disk_w"])
                h["net_up"].append(snap["net_up"])
                h["net_down"].append(snap["net_down"])
                g = hw.get("gpus") or []
                dg = next((x for x in g if x.get("discrete")), g[0] if g else {})
                h["gpu"].append(dg.get("load"))
                h["gpu_temp"].append(dg.get("temp"))
                # per-GPU load, so every GPU in the Performance list has a graph
                for i, gx in enumerate(g):
                    k = f"gpu{i}"
                    if k not in h:
                        h[k] = deque([None] * (len(h["t"]) - 1), maxlen=HISTORY_LEN)
                    h[k].append(gx.get("load"))
                for k in [k for k in h if re.fullmatch(r"gpu\d+", k) and int(k[3:]) >= len(g)]:
                    h[k].append(None)
                h["cpu_temp"].append(hw.get("cpu_temp"))
                h["power"].append(hw.get("power_w"))
                if hw.get("power_src") == "battery" and hw.get("power_w"):
                    self.session_wh += hw["power_w"] * dt / 3600

    def _drives(self):
        out = []
        for p in psutil.disk_partitions(all=False):
            try:
                u = psutil.disk_usage(p.mountpoint)
                out.append({"mount": p.mountpoint, "fs": p.fstype, "total": u.total, "used": u.used,
                            "free": u.free, "percent": u.percent})
            except Exception:
                pass
        return out

    # ---------------------------------------------------- processes

    def _process_loop(self):
        # One NtQuerySystemInformation call per cycle gives every process's counters.
        # Static info (exe path, user, description) is looked up once per new process.
        static = {}  # (pid, created) -> dict
        ncpu = psutil.cpu_count() or 1
        prev, prev_t = {}, None
        while True:
            t0 = time.time()
            try:
                snap = ntproc.snapshot()
            except OSError:
                time.sleep(2)
                continue
            dt = (t0 - prev_t) if prev_t else None
            rows, alive = [], set()
            for pid, p in snap.items():
                key = (pid, p["created"])
                alive.add(key)
                info = static.get(key)
                if info is None:
                    info = static[key] = self._static_info(pid, p["name"])
                old = prev.get(key)
                if old and dt:
                    cpu = (p["cpu_time"] - old["cpu_time"]) / 1e7 / dt / ncpu * 100
                    io_rate = max(0.0, (p["io_total"] - old["io_total"]) / dt)
                else:
                    cpu, io_rate = 0.0, 0.0
                rows.append({"pid": pid, "ppid": p["ppid"], "name": p["name"], "exe": info["exe"], "desc": info["desc"],
                             "user": info["user"], "created": p["created"], "cpu": max(0.0, min(cpu, 100.0)),
                             "mem": p["mem"], "threads": p["threads"], "handles": p["handles"], "io_rate": io_rate})
            prev = {(pid, p["created"]): p for pid, p in snap.items()}
            prev_t = t0
            for k in list(static):
                if k not in alive:
                    del static[k]
            with self.lock:
                self.processes = rows
            time.sleep(max(0.5, 2 - (time.time() - t0)))

    @staticmethod
    def _static_info(pid, name):
        info = {"exe": None, "user": "", "desc": None}
        if pid in (0, 4):
            info["user"] = "SYSTEM"
            return info
        try:
            p = psutil.Process(pid)
            try:
                info["exe"] = p.exe()
            except Exception:
                pass
            try:
                info["user"] = (p.username() or "").split("\\")[-1]
            except Exception:
                pass
        except Exception:
            pass
        info["desc"] = file_description(info["exe"])
        return info

    # ---------------------------------------------------- sensors

    def _sensor_loop(self):
        while True:
            sensors = self.lhm.read() if self.lhm.ok else []
            hw = summarize(sensors)
            if not sensors:
                hw.update(self._fallback())
            with self.lock:
                self.sensors = sensors
                self.hw = hw
            time.sleep(1)

    def _fallback(self):
        """Used only when LibreHardwareMonitorLib could not be loaded."""
        out = {}
        b = psutil.sensors_battery()
        if b:
            out["battery"] = {"percent": b.percent, "plugged": b.power_plugged}
        txt = run(["nvidia-smi", "--query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total",
                   "--format=csv,noheader,nounits"], timeout=4)
        gpus = []
        for line in txt.strip().splitlines():
            v = [x.strip() for x in line.split(",")]
            try:
                gpus.append({"name": v[0], "temp": float(v[1]), "load": float(v[2]), "mem_used": float(v[3]),
                             "mem_total": float(v[4]), "discrete": True})
            except Exception:
                pass
        out["gpus"] = gpus
        return out

    # ---------------------------------------------------- api

    def snapshot(self):
        with self.lock:
            b = psutil.sensors_battery()
            hw = dict(self.hw)
            bat = dict(hw.get("battery") or {})
            if b:
                bat.setdefault("percent", b.percent)
                bat["plugged"] = b.power_plugged
                if b.secsleft not in (psutil.POWER_TIME_UNLIMITED, psutil.POWER_TIME_UNKNOWN):
                    bat["secs_left"] = b.secsleft
            hw["battery"] = bat if (bat or b) else None
            return {
                "system": self.system, "hw": hw, "admin": self.admin,
                "lhm": {"ok": self.lhm.ok, "error": self.lhm.error, "count": len(self.sensors), "restarts": self.lhm.restarts},
                "session_wh": self.session_wh, "session_start": self.session_start,
            }

    def get_history(self, seconds):
        with self.lock:
            n = min(int(seconds), len(self.history["t"]))
            return {k: list(v)[-n:] if n else [] for k, v in self.history.items()}

    def get_sensors(self):
        with self.lock:
            return list(self.sensors)

    def get_processes(self):
        with self.lock:
            return list(self.processes)


# ------------------------------------------------------------ sensor summary

def _find(sensors, hw_type=None, type_=None, name=None, hw_match=None):
    for s in sensors:
        if hw_type and not s["hw_type"].startswith(hw_type):
            continue
        if hw_match and s["hw"] != hw_match:
            continue
        if type_ and s["type"] != type_:
            continue
        if name and not re.search(name, s["name"], re.I):
            continue
        return s
    return None


def summarize(sensors):
    """Turn the flat LHM sensor list into the handful of numbers the UI headlines."""
    hw = {}
    val = lambda s: s["value"] if s else None

    # CPU
    t = _find(sensors, "Cpu", "Temperature", r"^(Core Max|CPU Package)$")
    hw["cpu_temp"] = val(t) if t and t["value"] > 0 else None
    p = _find(sensors, "Cpu", "Power", r"^(CPU )?Package$")
    hw["cpu_power"] = val(p) if p and p["value"] > 0 else None
    hw["core_temps"] = [s["value"] for s in sensors if s["hw_type"] == "Cpu" and s["type"] == "Temperature"
                        and re.match(r"^CPU Core #\d+$", s["name"])]
    hw["core_clocks"] = [s["value"] for s in sensors if s["hw_type"] == "Cpu" and s["type"] == "Clock"
                         and re.match(r"^(CPU )?Core #\d+$", s["name"])]

    # GPUs
    gpus = []
    for name in dict.fromkeys(s["hw"] for s in sensors if s["hw_type"].startswith("Gpu")):
        g = lambda **kw: _find(sensors, hw_match=name, **kw)
        load = g(type_="Load", name=r"^GPU Core$") or g(type_="Load", name=r"^D3D 3D$")
        used = g(type_="SmallData", name=r"GPU Memory Used|D3D Dedicated Memory Used") \
            or g(type_="SmallData", name=r"D3D Shared Memory Used")
        total = g(type_="SmallData", name=r"GPU Memory Total") or g(type_="SmallData", name=r"D3D Shared Memory Total")
        power = g(type_="Power", name=r"GPU (Package|Power)")
        gpus.append({
            "name": name, "discrete": not _find(sensors, hw_match=name, hw_type="GpuIntel"),
            "load_label": "3D engine" if load and load["name"] == "D3D 3D" else "Core",
            "shared_mem": bool(used and "Shared" in used["name"]),
            "temp": val(g(type_="Temperature", name=r"^GPU Core$")),
            "hotspot": val(g(type_="Temperature", name=r"Hot ?Spot")),
            "load": val(load), "clock": val(g(type_="Clock", name=r"^GPU Core$")),
            "mem_used": val(used), "mem_total": val(total),
            "power": val(power) if power and power["value"] > 0 else None,
        })
    hw["gpus"] = gpus

    # Battery (Energy sensors are in mWh)
    bat = {}
    pb = psutil.sensors_battery()
    plugged = pb.power_plugged if pb else None
    for s in sensors:
        if s["hw_type"] != "Battery":
            continue
        n, v = s["name"], s["value"]
        if n == "Discharge Rate": bat["discharge_w"] = abs(v)
        elif n == "Charge Rate": bat["charge_w"] = abs(v)
        elif n == "Charge/Discharge Rate" and v:
            bat["charge_w" if plugged else "discharge_w"] = abs(v)
        elif n == "Charge Level": bat["percent"] = v
        elif n == "Degradation Level": bat["wear"] = v
        elif n == "Voltage": bat["voltage"] = v
        elif n == "Designed Capacity": bat["design_wh"] = v / 1000
        elif n == "Fully-Charged Capacity": bat["full_wh"] = v / 1000
        elif n == "Remaining Capacity": bat["remaining_wh"] = v / 1000
        elif n == "Charge Current": bat["current"] = v
        bat["name"] = s["hw"]
    if bat.get("design_wh") and bat.get("full_wh"):
        bat["health"] = bat["full_wh"] / bat["design_wh"] * 100
    hw["battery"] = bat or None

    # Headline power figure: whole-system while on battery, else sum of known components
    if bat.get("discharge_w"):
        hw["power_w"], hw["power_src"] = bat["discharge_w"], "battery"
    else:
        parts = [("CPU", hw["cpu_power"])] + [("GPU", g["power"]) for g in gpus]
        parts = [(n, v) for n, v in parts if v]
        hw["power_w"], hw["power_src"] = (sum(v for _, v in parts), "components") if parts else (None, None)
        hw["power_parts"] = sorted({n for n, _ in parts})  # e.g. ["CPU"] or ["CPU", "GPU"]

    hw["storage"] = [{"name": s["hw"], "temp": s["value"]} for s in sensors
                     if s["hw_type"] == "Storage" and s["type"] == "Temperature" and s["name"] in ("Temperature", "Composite Temperature")]
    hw["fans"] = [{"name": s["name"], "rpm": s["value"]} for s in sensors if s["type"] == "Fan"]
    return hw
