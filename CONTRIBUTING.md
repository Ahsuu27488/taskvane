# Contributing to Taskvane

Thanks for helping! Bug reports, ideas and pull requests are all welcome.

- **Bugs:** open an [issue](https://github.com/Ahsuu27488/taskvane/issues/new/choose) and attach `%APPDATA%\Taskvane\taskvane.log` (Settings → Sensor engine → Open log), plus your Windows version and hardware.
- **Features:** open an issue first so we can agree on the approach.
- **Pull requests:** keep them focused, match the surrounding code style, and describe how you tested.

## Development setup

```powershell
pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File tools\fetch_deps.ps1   # downloads + verifies LibreHardwareMonitor into lib\
python app.py                 # run from source
python app.py --debug         # with WebView2 DevTools
powershell -ExecutionPolicy Bypass -File build.ps1 -Release    # exe + portable zip + installer
```

Python 3.12+ on Windows 10/11 x64. Building the installer needs Inno Setup 6 (`winget install JRSoftware.InnoSetup`).

## How it works

| Path | What it does |
|---|---|
| `app.py` | pywebview (WebView2) window, tray icon, alerts, settings, single-instance lock, elevation hand-off, CLI (`--quit`, `--set-startup`, …) |
| `taskvane/monitor.py` | Background collectors (system, processes, sensors) and the 1-hour history |
| `taskvane/ntproc.py` | Every process's counters in one `NtQuerySystemInformation` call, the same source Task Manager uses (~15 ms for 250 processes) |
| `taskvane/lhm.py` + `lhm_host.ps1` | LibreHardwareMonitorLib runs in a separate Windows PowerShell 5.1 helper (it needs .NET Framework) that streams JSON. Out of process, so a driver/.NET fault can't crash the app; it's restarted automatically |
| `taskvane/actions.py` | Process actions, startup apps, PawnIO detection, elevated scheduled tasks, autostart |
| `ui/` | The interface: plain HTML/CSS/JS, no framework, no build step |
| `installer/Taskvane.iss` | Inno Setup installer |
| `tools/fetch_deps.ps1` | Pinned, SHA-256-verified third-party downloads (not committed to the repo) |

Design notes worth knowing before you change things:

- **Elevated vs normal runs use separate WebView2 profiles.** A profile folder can't be shared across integrity levels.
- **Kernel objects** (instance mutex, quit event) use a shared DACL with a low integrity label, so normal and elevated instances can see and signal each other.
- **Don't call pywebview window methods from inside window events.** The UI thread waits on event handlers, so a synchronous call deadlocks. Use async Win32 calls or a short timer (see `_present_window`).
- **The UI files are fingerprinted at startup** to clear WebView2's HTTP cache after updates.
- Keep CPU cost low: the whole app idles around 0.4% CPU. Measure before and after if you touch a collector.

## Releasing

1. Bump `VERSION` in `app.py` and add a section to `CHANGELOG.md`.
2. Commit, then tag and push: `git tag v1.3.0 && git push --tags`.
3. GitHub Actions builds the installer, portable zip and SHA-256 checksums, and publishes the release.
