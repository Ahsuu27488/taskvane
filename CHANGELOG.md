# Changelog

## Unreleased

- **Update notifications.** Once a day Taskvane asks GitHub for the latest version number and, when there's a newer one, shows a banner on the Overview page ("Taskvane X.Y.Z is available") with **What's new**, **Download** and **Skip this version**, plus one Windows notification per new version. It only tells you: nothing is downloaded or installed. The request carries no personal data, and **Settings > Check for updates** turns it off (then Taskvane makes no network requests at all). winget and Scoop users can keep using `winget upgrade` / `scoop update`.
- Privacy wording on the website, README and SECURITY.md now describes this check instead of saying nothing leaves your PC

## 1.2.1

- **PawnIO is no longer bundled.** CPU temperature and CPU power still use the signed PawnIO driver, but you now install it from its author's site, https://pawnio.eu/. **Enable CPU sensors** opens that page; Taskvane notices when PawnIO is installed and then offers to restart as administrator. Why: Taskvane is GPL-3.0, and shipping it together with a signed, proprietary driver build conflicts with GPL-3 (PawnIO's author pointed this out; other GPL-3 apps such as OpenRGB do the same). If PawnIO is already installed, nothing changes for you.
- The installer no longer has an "Install the PawnIO driver" option, and upgrading removes the old bundled PawnIO setup file
- Website works properly on phones: new menu button, temperature scale labels no longer overlap, comparison tables show both columns, readable screenshots
- Website: "Also in Taskvane" section and a "Send link to my PC" button for phone visitors
- winget and Scoop manifests in `packaging/`; Scoop bucket at github.com/Ahsuu27488/scoop-bucket
- Website About page: AI agent, MCP and RAG work highlighted
- Code signing policy and privacy policy (website `/code-signing/`, README, download page), ahead of applying for free code signing from SignPath Foundation
- Demo video (English and Hinglish, vertical) attached to the v1.2.0 release and linked from the README

## 1.2.0 (first public release)

The first open-source release of Taskvane, a better Task Manager for Windows 11.

- Overview, Performance, Processes, Sensors, Power, Startup apps and Settings pages
- CPU core and package temperatures and power, GPU core and hot-spot temperatures, SSD temperatures, through LibreHardwareMonitorLib
- Whole-system power draw on battery; battery health, wear, voltage and time remaining
- One-click **Enable CPU sensors**: restarts as administrator and installs the signed PawnIO driver (one UAC prompt)
- **Always start as administrator** with no UAC prompt, using an elevated scheduled task
- Processes grouped by app with friendly names; end task or process tree, priority, open file location, details panel
- Startup apps manager; temperature, memory, battery and CPU-load alerts; always-on-top mini widget
- History up to 1 hour with hover readouts; CSV export
- Installer (Inno Setup) and portable zip; `--quit`, `--minimized`, `--no-elevate` command-line options
- About 0.4% total CPU use
