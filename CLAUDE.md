# Taskvane: project guide for Claude

Taskvane is a free, open-source (GPL-3.0) **Task Manager alternative for Windows 11/10** with CPU/GPU temperatures, power draw in watts and battery health. Owner: Muhammad Ahsan (GitHub `Ahsuu27488`). The repo folder is still named `C:\dev\pc-monitor` (the app's pre-release name was "PC Monitor").

@docs/STATUS.md
@docs/DECISIONS.md

## Conventions

- Verify before saying something works: run it, measure it, capture it (see *Testing*).
- Ask before anything public or account-changing that wasn't requested (pushing a release, DNS, GitHub settings). Pushing code to `main` is normal work once a change was asked for.
- Never put personal details, private repo names or a personal email in public files. Commit as `Muhammad Ahsan <180838835+Ahsuu27488@users.noreply.github.com>` (already set repo-locally).
- End commit messages with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Personal working notes live in `CLAUDE.local.md` (gitignored), not here.

## Layout

| Path | What |
|---|---|
| `app.py` | Entry point: pywebview window, tray, alerts, settings, single-instance mutex, quit event, elevation hand-off, CLI flags. `VERSION` lives here (single source of truth) |
| `taskvane/monitor.py` | Collectors (system / processes / sensors) + 1-hour history; `summarize()` turns raw LHM sensors into headline numbers |
| `taskvane/ntproc.py` | All processes via one `NtQuerySystemInformation` call |
| `taskvane/lhm.py` + `lhm_host.ps1` | LibreHardwareMonitorLib in an **out-of-process** Windows PowerShell 5.1 helper streaming JSON; supervised and auto-restarted |
| `taskvane/actions.py` | Process actions, startup apps, PawnIO detection (not bundled), elevated scheduled tasks, autostart |
| `taskvane/paths.py`, `log.py` | Paths (portable mode via `portable.txt`), rotating log `%APPDATA%\Taskvane\taskvane.log` |
| `ui/` | Plain HTML/CSS/JS UI (no build step). `app.js` talks to Python via `window.pywebview.api` |
| `installer/Taskvane.iss` | Inno Setup installer |
| `tools/` | `fetch_deps.ps1` (pinned + SHA-256-verified LHM into `lib/`), `make_icon.py`, `make_version_info.py`, `snap.py` / `clickseq.py` (window capture + scripted clicks for testing) |
| `packaging/` | winget + Scoop manifests (update per release) |
| `website/` | Astro static site → GitHub Pages at https://taskvane.ahsandev.site |
| `.github/workflows/` | `build.yml` (exe/installer/portable + smoke test; publishes a release on `v*` tags), `website.yml` (deploys the site) |

## Build, run, release

```powershell
powershell -ExecutionPolicy Bypass -File tools\fetch_deps.ps1     # once; lib/ is gitignored
python app.py                                                     # run from source (--no-elevate to skip the admin task)
powershell -ExecutionPolicy Bypass -File build.ps1 -Release       # dist\Taskvane\Taskvane.exe + release\*-Setup.exe + *-Portable.zip
cd website; npm ci; npx astro build                               # site
```

Release: bump `VERSION` in `app.py` → add a `## x.y.z` section to `CHANGELOG.md` → commit → `git tag vX.Y.Z && git push --tags`. CI checks the tag matches `VERSION`, builds, smoke-tests and publishes the release; the website workflow then refreshes download links.

## Traps we already hit (don't repeat them)

- **Never call pywebview window methods or touch WinForms properties from inside window events** (`shown`, `closing`). The UI thread waits on the handler → deadlock (hung, blank window). Use async Win32 (`PostMessage`, `ShowWindowAsync`, `SWP_ASYNCWINDOWPOS`) or a `threading.Timer` (see `_present_window`, `style_window`).
- **pywebview x/y are multiplied by the display scale; Win32 coords are physical.** Position windows with Win32 after they exist (`center_on_monitor`, `_place_mini`).
- **Don't load LibreHardwareMonitorLib in-process via pythonnet**: it crashed the whole app intermittently. It lives in `lhm_host.ps1` on purpose.
- **WebView2 profile can't be shared across integrity levels**: admin runs use `%APPDATA%\Taskvane\webview-admin`. And WebView2 caches the UI over its local server: `clear_stale_ui_cache()` fingerprints `ui/` and clears the cache on change.
- **Kernel objects shared between normal and elevated instances** need the low-integrity SDDL (`SHARED_SDDL` in `app.py`), otherwise "access denied" breaks the single-instance check and `--quit`.
- **Expensive Windows APIs**: `PowerGetEffectiveOverlayScheme` hung when called concurrently (power mode was removed later). Poll slow APIs from one thread and cache.
- **psutil per-process calls cost ~6% CPU**; use `ntproc.snapshot()`. Target total app cost ≈0.4% CPU; measure if you touch a collector.
- **PawnIO detection = its Uninstall registry entry**, not the service key (that lingers after uninstall).
- **Never bundle PawnIO again** (or any signed, proprietary driver build) in the GPL-3.0 download: see DECISIONS.md. The app links to https://pawnio.eu/.
- **Inno Setup `/SUPPRESSMSGBOXES` answers Yes** to MsgBox; guard user-data deletion with `not UninstallSilent()`.
- **Windows PowerShell 5.1** (used by helper, CI, installer tests): `Expand-Archive` needs a `.zip` extension; `"$( ... 'text (with paren' ... )"` mis-parses; `Start-Process -Wait` waits for the whole child-process tree.
- **This machine:** `python.exe` is a launcher shim (the PID you start exits; find the real process by command line). Chrome headless can't render narrower than ~500 px (use the browser pane's mobile preset for phone checks). The Bash/PowerShell tool's safety parser rejects some command lines containing `Remove-Item` plus `/x`-style args: split such commands.
- **Phone-width captures:** the browser pane's screenshots often time out; Playwright (installed, `channel="chrome"`, `is_mobile=True`, 375 px, scroll first so lazy images load) gives reliable full-page shots. Run it from PowerShell: Git Bash rewrites `/features/`-style args into Windows paths.
- **Releases made by CI's `GITHUB_TOKEN` don't trigger other workflows**, so `website.yml`'s `release: published` never fires; `build.yml` now runs `gh workflow run website.yml` after publishing. If the site still links to an old version after a release: `gh workflow run website.yml --ref main`.
- `.gitignore` root patterns are anchored (`/lib/`, `/build/` …) so `website/src/lib` isn't ignored.

## Testing (do this, don't skip it)

- Run the app and read the log (`%APPDATA%\Taskvane\taskvane.log`): look for `UI connected`, `first sensor reading`, no `ERROR`/`Traceback`.
- Window capture without screen access: `python tools\snap.py "Taskvane" out.png` (PrintWindow).
- **Elevated window**: normal processes can't capture or click it. Run `tools\clickseq.py` elevated (`Start-Process python -Verb RunAs …`) to click sidebar items and capture pages; sidebar CSS y: overview 107, performance 144, processes 181, sensors 218, power 254, startup 291, settings 328 (x 110).
- `Taskvane.exe --quit` closes any running copy (even elevated) and waits until it has exited.
- Installer lifecycle: silent install with `/TASKS="desktopicon,alwaysadmin"`, run via `schtasks /Run /TN "Taskvane (administrator)"`, silent uninstall with `/LOG=…`, then check nothing is left (folder, shortcuts, tasks, uninstall entry).
- Website: `npx astro dev`, then the browser pane, or `website\scripts\shoot.ps1` for full-page captures.

## Keeping these docs current

A Stop hook (local `.claude/`, not in git) blocks finishing when code changed but `docs/STATUS.md` / `CHANGELOG.md` didn't. When you finish work: update **docs/STATUS.md** (what changed, what's next), add user-visible changes to **CHANGELOG.md** (under an `## Unreleased` heading if no version bump), and add any new trap or design choice to this file or **docs/DECISIONS.md**.
