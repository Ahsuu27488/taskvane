# Changelog

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
