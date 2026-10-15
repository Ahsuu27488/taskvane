# Third-party components

Taskvane bundles the following components. Each remains under its own license.

| Component | Version | License | Source |
|---|---|---|---|
| LibreHardwareMonitorLib and its dependencies (`lib/lhm`) | 0.9.6 | MPL-2.0 (dependencies: MIT / Apache-2.0) | https://github.com/LibreHardwareMonitor/LibreHardwareMonitor |
| PawnIO setup (`lib/pawnio/PawnIO_setup.exe`), signed by namazso | 2.2.0 | Freeware (official signed edition); driver source GPL-2.0 | https://pawnio.eu/ · https://github.com/namazso/PawnIO |
| pywebview | 6.x | BSD-3-Clause | https://github.com/r0x0r/pywebview |
| pythonnet | 3.x | MIT | https://github.com/pythonnet/pythonnet |
| psutil | 7.x | BSD-3-Clause | https://github.com/giampaolo/psutil |
| pystray | 0.19 | LGPL-3.0 | https://github.com/moses-palmer/pystray |
| Pillow | 12.x | MIT-CMU (HPND) | https://github.com/python-pillow/Pillow |
| Microsoft Edge WebView2 Runtime | system | Microsoft license (preinstalled on Windows 11) | https://developer.microsoft.com/microsoft-edge/webview2/ |

PawnIO is installed only when the user chooses **Enable CPU sensors**. It's the same signed driver LibreHardwareMonitor installs, run as `PawnIO_setup.exe -install -silent`. Users can remove it from Windows Settings → Apps, or with `PawnIO_setup.exe -uninstall`.
