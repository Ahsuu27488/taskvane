# Decisions

Why things are the way they are. Don't reverse these without asking the owner.

| Decision | Why |
|---|---|
| **Python + pywebview (WebView2) desktop app** | Reused the HTML UI as a native window; light, no Electron. Packaged with PyInstaller (one-folder: faster start, fewer AV false positives than one-file). |
| **LibreHardwareMonitorLib in a separate PowerShell 5.1 process** | In-process pythonnet loading crashed the app intermittently. PS 5.1 runs .NET Framework natively and catches .NET exceptions; a helper crash can't kill the window. |
| **Process stats via `NtQuerySystemInformation`** | psutil opened every process each cycle (~6.7% CPU). One syscall ≈15 ms for 250 processes; also gives Task Manager's private-working-set memory. |
| **Don't bundle PawnIO; send users to https://pawnio.eu/** (since 1.2.1) | PawnIO's author (namazso) said unmodified redistribution of PawnIO is fine on its own, but they hold copyright on a GPL patch inside LibreHardwareMonitor, and shipping a GPL-3.0 app together with a signed, proprietary driver build breaks GPL-3's "Installation Information" clause (it would require handing over the signing keys). GPL-3 projects like OpenRGB link to the PawnIO homepage instead, so we do too. "Enable CPU sensors" opens the site, the app detects the install (Uninstall registry entry) and then offers the admin restart. 1.2.0 bundled it; that's what we're moving away from. |
| **"Always start as administrator" = elevated scheduled task** | Standard way (HWiNFO etc.) to avoid a UAC prompt per launch. Off by default; only changeable from admin mode. |
| **Update check = notify only, once a day, can be turned off** | Users had no way to learn about new versions. One GET to the public GitHub releases API (generic User-Agent, no IDs), at most daily, 30 s after start, result cached in settings.json; the user downloads the update themselves. No silent download/install: running a downloaded installer without code signing would train users to accept unsigned binaries and makes a compromised release account far worse; revisit after SignPath signing. Default ON (proposed; owner to confirm). |
| **Guides publish on a schedule, two at a time** | A brand-new site that drops many AI-assisted articles at once looks like scaled content to search engines; pairs a few days apart, each fact-checked against the app, are safer and let the owner review. Scheduling is build-time (`published` date + daily rebuild), so it needs no server and works with the owner's PC off. |
| **Removed power mode / power plan switching** | Taskvane is a monitoring app; changing system settings is out of scope (owner's call, 2026-10-15). |
| **Name "Taskvane"** | "PC Monitor" can't rank (means display screens). Taskvane had zero GitHub/web collisions. Tagline: "a better Task Manager for Windows 11". |
| **GPL-3.0** | Keeps forks open so no one can ship a closed clone; owner's choice. |
| **Third-party binaries not committed** | `tools/fetch_deps.ps1` downloads pinned versions and verifies SHA-256. |
| **Website: Astro on GitHub Pages at a subdomain of ahsandev.site** | Free, fast static site; doubles as the owner's portfolio (About page). Honest comparison pages + FAQ + JSON-LD + `llms.txt` for search and AI assistants. |
| **Website design** | Cool fog background, slate ink, brand blue; thermal ramp only where it encodes temperature; Instrument Sans (condensed for headings); one signature element: the interactive temperature scale using the app's real thresholds. |
| **Separate WebView2 profiles for admin/normal runs** | A profile can't be used across integrity levels; the elevated window was blank. |
| **Commits use the GitHub no-reply email** | Keeps the owner's Gmail out of a public repo. |
