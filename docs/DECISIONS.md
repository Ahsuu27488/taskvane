# Decisions

Why things are the way they are. Don't reverse these without asking the owner.

| Decision | Why |
|---|---|
| **Python + pywebview (WebView2) desktop app** | Reused the HTML UI as a native window; light, no Electron. Packaged with PyInstaller (one-folder: faster start, fewer AV false positives than one-file). |
| **LibreHardwareMonitorLib in a separate PowerShell 5.1 process** | In-process pythonnet loading crashed the app intermittently. PS 5.1 runs .NET Framework natively and catches .NET exceptions; a helper crash can't kill the window. |
| **Process stats via `NtQuerySystemInformation`** | psutil opened every process each cycle (~6.7% CPU). One syscall ≈15 ms for 250 processes; also gives Task Manager's private-working-set memory. |
| **Bundle PawnIO's signed installer; install only on user action** | Same approach as LibreHardwareMonitor. One UAC prompt: elevated relaunch with `--install-pawnio`. Redistribution permission still to be confirmed with the author. |
| **"Always start as administrator" = elevated scheduled task** | Standard way (HWiNFO etc.) to avoid a UAC prompt per launch. Off by default; only changeable from admin mode. |
| **Removed power mode / power plan switching** | Taskvane is a monitoring app; changing system settings is out of scope (owner's call, 2026-10-15). |
| **Name "Taskvane"** | "PC Monitor" can't rank (means display screens). Taskvane had zero GitHub/web collisions. Tagline: "a better Task Manager for Windows 11". |
| **GPL-3.0** | Keeps forks open so no one can ship a closed clone; owner's choice. |
| **Third-party binaries not committed** | `tools/fetch_deps.ps1` downloads pinned versions and verifies SHA-256. |
| **Website: Astro on GitHub Pages at a subdomain of ahsandev.site** | Free, fast static site; doubles as the owner's portfolio (About page). Honest comparison pages + FAQ + JSON-LD + `llms.txt` for search and AI assistants. |
| **Website design** | Cool fog background, slate ink, brand blue; thermal ramp only where it encodes temperature; Instrument Sans (condensed for headings); one signature element: the interactive temperature scale using the app's real thresholds. |
| **Separate WebView2 profiles for admin/normal runs** | A profile can't be used across integrity levels; the elevated window was blank. |
| **Commits use the GitHub no-reply email** | Keeps the owner's Gmail out of a public repo. |
