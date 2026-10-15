"""User-triggered actions: process control, startup apps, power modes, autostart."""
import ctypes
import os
import re
import struct
import subprocess
import sys
import time
import winreg

import psutil

from .log import log
from .monitor import NO_WINDOW, file_description, run
from .paths import PAWNIO_SETUP

PRIORITIES = {
    "idle": psutil.IDLE_PRIORITY_CLASS, "below": psutil.BELOW_NORMAL_PRIORITY_CLASS,
    "normal": psutil.NORMAL_PRIORITY_CLASS, "above": psutil.ABOVE_NORMAL_PRIORITY_CLASS,
    "high": psutil.HIGH_PRIORITY_CLASS, "realtime": psutil.REALTIME_PRIORITY_CLASS,
}
PRIORITY_NAMES = {v: k for k, v in PRIORITIES.items()}


def _err(e):
    if isinstance(e, psutil.AccessDenied):
        return "Access denied. Restart Taskvane as administrator to manage this process."
    if isinstance(e, psutil.NoSuchProcess):
        return "The process has already exited."
    return str(e)


# ------------------------------------------------------------ processes

def process_details(pid):
    try:
        p = psutil.Process(pid)
        with p.oneshot():
            d = {"pid": pid, "name": p.name(), "status": p.status(), "created": p.create_time(),
                 "ppid": p.ppid(), "threads": p.num_threads()}
            for key, fn in (("exe", p.exe), ("cmdline", lambda: " ".join(p.cmdline())), ("cwd", p.cwd),
                            ("user", p.username), ("handles", p.num_handles),
                            ("priority", lambda: PRIORITY_NAMES.get(p.nice(), str(p.nice()))),
                            ("affinity", lambda: len(p.cpu_affinity()))):
                try:
                    d[key] = fn()
                except Exception:
                    d[key] = None
            try:
                mi = p.memory_full_info()
                d["mem"] = {"working": mi.rss, "private": mi.private, "peak": mi.peak_wset}
            except Exception:
                try:
                    d["mem"] = {"working": p.memory_info().rss}
                except Exception:
                    d["mem"] = {}
            try:
                d["parent"] = psutil.Process(d["ppid"]).name()
            except Exception:
                d["parent"] = None
            d["children"] = len(p.children(recursive=True))
            try:
                d["connections"] = len(p.net_connections())
            except Exception:
                d["connections"] = None
            d["desc"] = file_description(d.get("exe"))
        return {"ok": True, "data": d}
    except Exception as e:
        return {"ok": False, "error": _err(e)}


def end_process(pid, tree=False):
    if pid in (0, 4) or pid == os.getpid():
        return {"ok": False, "error": "That process can't be ended."}
    try:
        p = psutil.Process(pid)
        name = p.name()
        procs = (p.children(recursive=True) if tree else []) + [p]
        for c in procs:
            try:
                c.terminate()
            except psutil.NoSuchProcess:
                pass
        gone, alive = psutil.wait_procs(procs, timeout=3)
        for c in alive:
            try:
                c.kill()
            except Exception:
                pass
        return {"ok": True, "name": name, "count": len(procs)}
    except Exception as e:
        return {"ok": False, "error": _err(e)}


def set_priority(pid, level):
    try:
        psutil.Process(pid).nice(PRIORITIES[level])
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": _err(e)}


def open_location(path):
    if path and os.path.exists(path):
        subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
        return {"ok": True}
    return {"ok": False, "error": "File location unavailable."}


# ------------------------------------------------------------ startup apps

RUN = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN32 = r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"
APPROVED = r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved"
HIVES = {"HKCU": winreg.HKEY_CURRENT_USER, "HKLM": winreg.HKEY_LOCAL_MACHINE}


def _exe_from_command(cmd):
    cmd = os.path.expandvars(cmd.strip())
    m = re.match(r'^"([^"]+)"', cmd) or re.match(r"^(\S+?\.exe)\b", cmd, re.I)
    return m.group(1) if m else None


def _approved_state(hive, sub, name):
    try:
        with winreg.OpenKey(HIVES[hive], f"{APPROVED}\\{sub}") as k:
            data, _ = winreg.QueryValueEx(k, name)
            return not (data and data[0] & 1)  # odd first byte = disabled
    except OSError:
        return True


def startup_apps():
    items = []
    for hive in ("HKCU", "HKLM"):
        for path, sub in ((RUN, "Run"), (RUN32, "Run32")):
            if hive == "HKCU" and path == RUN32:
                continue
            try:
                with winreg.OpenKey(HIVES[hive], path) as k:
                    i = 0
                    while True:
                        try:
                            name, cmd, _ = winreg.EnumValue(k, i)
                        except OSError:
                            break
                        i += 1
                        exe = _exe_from_command(str(cmd))
                        items.append({"id": f"{hive}|{sub}|{name}", "name": name, "command": str(cmd), "exe": exe,
                                      "desc": file_description(exe) if exe and os.path.exists(exe) else None,
                                      "source": f"{hive} registry", "scope": "user" if hive == "HKCU" else "machine",
                                      "enabled": _approved_state(hive, sub, name)})
            except OSError:
                pass
    folders = [("HKCU", os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\Startup")),
               ("HKLM", os.path.join(os.environ.get("PROGRAMDATA", ""), r"Microsoft\Windows\Start Menu\Programs\StartUp"))]
    for hive, folder in folders:
        if not os.path.isdir(folder):
            continue
        for f in os.listdir(folder):
            if f.lower() == "desktop.ini":
                continue
            full = os.path.join(folder, f)
            items.append({"id": f"{hive}|StartupFolder|{f}", "name": os.path.splitext(f)[0], "command": full, "exe": full,
                          "desc": None, "source": "Startup folder", "scope": "user" if hive == "HKCU" else "machine",
                          "enabled": _approved_state(hive, "StartupFolder", f)})
    items.sort(key=lambda x: x["name"].lower())
    return items


def set_startup_enabled(item_id, enabled):
    hive, sub, name = item_id.split("|", 2)
    # Same format Task Manager writes: 12 bytes, first byte 2=enabled / 3=disabled, then a FILETIME.
    ft = int((time.time() + 11644473600) * 10_000_000)
    data = struct.pack("<IQ", 2 if enabled else 3, 0 if enabled else ft)
    try:
        with winreg.CreateKeyEx(HIVES[hive], f"{APPROVED}\\{sub}", 0, winreg.KEY_SET_VALUE) as k:
            winreg.SetValueEx(k, name, 0, winreg.REG_BINARY, data)
        return {"ok": True}
    except PermissionError:
        return {"ok": False, "error": "Machine-wide startup items need administrator rights."}
    except OSError as e:
        return {"ok": False, "error": str(e)}


# ------------------------------------------------------------ app integration

AUTOSTART_NAME = "Taskvane"


def _launch_command(extra=""):
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}" {extra}'.strip()
    pyw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    script = os.path.abspath(sys.argv[0])
    return f'"{pyw if os.path.exists(pyw) else sys.executable}" "{script}" {extra}'.strip()


def get_autostart():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN) as k:
            winreg.QueryValueEx(k, AUTOSTART_NAME)
            return True
    except OSError:
        return False


def set_autostart(enabled):
    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, RUN, 0, winreg.KEY_SET_VALUE) as k:
        if enabled:
            winreg.SetValueEx(k, AUTOSTART_NAME, 0, winreg.REG_SZ, _launch_command("--minimized"))
        else:
            try:
                winreg.DeleteValue(k, AUTOSTART_NAME)
            except OSError:
                pass
    return {"ok": True}


def relaunch_as_admin(extra=""):
    if getattr(sys, "frozen", False):
        exe, params = sys.executable, extra
    else:
        pyw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
        exe, params = (pyw if os.path.exists(pyw) else sys.executable), f'"{os.path.abspath(sys.argv[0])}" {extra}'
    log.info("requesting elevation: %s %s", exe, params)
    rc = ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, params, os.path.dirname(exe), 1)  # SW_SHOWNORMAL
    log.info("ShellExecute runas returned %s (%s)", rc, "ok" if rc > 32 else "declined/failed")
    return rc > 32  # False if the user declined the UAC prompt


# ------------------------------------------------------------ PawnIO driver (CPU sensors)

PAWNIO_BUNDLED_VERSION = (2, 2, 0)


def _ver_tuple(s):
    return tuple(int(x) for x in re.findall(r"\d+", s or "")[:3]) or None


def pawnio_status():
    """{'installed': bool, 'version': 'x.y.z'|None, 'outdated': bool, 'bundled': bool}"""
    # The setup's Uninstall entry is authoritative: after an uninstall the driver
    # service key lingers (until reboot), so it can't be used to detect PawnIO.
    installed, version = False, None
    for view in (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                                0, winreg.KEY_READ | view) as root:
                for i in range(winreg.QueryInfoKey(root)[0]):
                    try:
                        with winreg.OpenKey(root, winreg.EnumKey(root, i)) as k:
                            if "PawnIO" in str(winreg.QueryValueEx(k, "DisplayName")[0]):
                                version = str(winreg.QueryValueEx(k, "DisplayVersion")[0])
                                installed = True
                    except OSError:
                        continue
        except OSError:
            pass
    vt = _ver_tuple(version)
    return {"installed": installed, "version": version, "bundled": os.path.exists(PAWNIO_SETUP),
            "outdated": bool(installed and vt and vt < PAWNIO_BUNDLED_VERSION)}


def install_pawnio():
    """Silently install the bundled, signed PawnIO driver. Requires an elevated process."""
    if not os.path.exists(PAWNIO_SETUP):
        return {"ok": False, "error": "PawnIO installer is missing from this build."}
    log.info("installing PawnIO from %s", PAWNIO_SETUP)
    try:
        r = subprocess.run([PAWNIO_SETUP, "-install", "-silent"], capture_output=True, timeout=180, creationflags=NO_WINDOW)
    except Exception as e:
        log.exception("PawnIO install failed to run")
        return {"ok": False, "error": str(e)}
    code = r.returncode
    log.info("PawnIO setup exit code %s; status now %s", code, pawnio_status())
    if code in (0, 3010):  # ERROR_SUCCESS, ERROR_SUCCESS_REBOOT_REQUIRED
        return {"ok": True, "reboot": code == 3010}
    if code == 5:
        return {"ok": False, "error": "Access denied. PawnIO can only be installed from administrator mode."}
    return {"ok": False, "error": f"PawnIO setup failed (error {code})."}


# ------------------------------------------------------------ "always run as administrator" (no UAC prompt)
# Elevated scheduled tasks are the standard way monitoring tools start with admin
# rights without a UAC prompt each time. Creating/removing them needs admin.

ADMIN_TASK = "Taskvane (administrator)"
ADMIN_LOGON_TASK = "Taskvane (administrator, sign-in)"


def _exe_and_args(extra):
    if getattr(sys, "frozen", False):
        return sys.executable, extra
    pyw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    return (pyw if os.path.exists(pyw) else sys.executable), f'"{os.path.abspath(sys.argv[0])}" {extra}'.strip()


def _task_xml(args, logon):
    import getpass
    from xml.sax.saxutils import escape
    exe, arguments = _exe_and_args(args)
    user = escape(os.environ.get("USERDOMAIN", "") + "\\" + getpass.getuser())
    trigger = f"<Triggers><LogonTrigger><Enabled>true</Enabled><UserId>{user}</UserId><Delay>PT10S</Delay></LogonTrigger></Triggers>" if logon else "<Triggers />"
    return f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo><Description>Starts Taskvane with administrator rights (CPU temperature and power sensors) without a UAC prompt.</Description></RegistrationInfo>
  {trigger}
  <Principals><Principal id="Author"><UserId>{user}</UserId><LogonType>InteractiveToken</LogonType><RunLevel>HighestAvailable</RunLevel></Principal></Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>5</Priority>
    <AllowHardTerminate>true</AllowHardTerminate>
  </Settings>
  <Actions Context="Author"><Exec><Command>{escape(exe)}</Command><Arguments>{escape(arguments)}</Arguments><WorkingDirectory>{escape(os.path.dirname(exe))}</WorkingDirectory></Exec></Actions>
</Task>"""


def _schtasks(*args):
    r = subprocess.run(["schtasks", *args], capture_output=True, text=True, creationflags=NO_WINDOW)
    return r.returncode, (r.stdout + r.stderr).strip()


def task_exists(name):
    return _schtasks("/Query", "/TN", name)[0] == 0


def _create_task(name, args, logon):
    import tempfile
    path = os.path.join(tempfile.gettempdir(), "taskvane-task.xml")
    with open(path, "w", encoding="utf-16") as f:
        f.write(_task_xml(args, logon))
    try:
        code, out = _schtasks("/Create", "/TN", name, "/XML", path, "/F")
    finally:
        os.remove(path)
    log.info("create task %r: %s %s", name, code, out)
    return code == 0, out


def _delete_task(name):
    if task_exists(name):
        code, out = _schtasks("/Delete", "/TN", name, "/F")
        log.info("delete task %r: %s %s", name, code, out)


def configure_startup(admin_auto, autostart):
    """Reconcile startup mechanisms:
       admin_auto  -> on-demand elevated task (plus a sign-in task if autostart)
       otherwise   -> plain HKCU Run entry for autostart, no tasks."""
    from .monitor import is_admin
    if admin_auto:
        if not is_admin():
            return {"ok": False, "error": "Turn this on from administrator mode."}
        ok, out = _create_task(ADMIN_TASK, "--from-task", logon=False)
        if not ok:
            return {"ok": False, "error": out}
        if autostart:
            ok, out = _create_task(ADMIN_LOGON_TASK, "--from-task --minimized", logon=True)
            if not ok:
                return {"ok": False, "error": out}
        else:
            _delete_task(ADMIN_LOGON_TASK)
        set_autostart(False)  # the sign-in task replaces the Run entry
    else:
        if task_exists(ADMIN_TASK) or task_exists(ADMIN_LOGON_TASK):
            if not is_admin():
                return {"ok": False, "error": "Turn this off from administrator mode."}
            _delete_task(ADMIN_TASK)
            _delete_task(ADMIN_LOGON_TASK)
        set_autostart(autostart)
    return {"ok": True}


def run_admin_task():
    code, out = _schtasks("/Run", "/TN", ADMIN_TASK)
    log.info("run admin task: %s %s", code, out)
    return code == 0
