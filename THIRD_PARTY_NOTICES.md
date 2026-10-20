# Third-party components

Taskvane bundles the following components. Each remains under its own license.

| Component | Version | License | Source |
|---|---|---|---|
| LibreHardwareMonitorLib and its dependencies (`lib/lhm`) | 0.9.6 | MPL-2.0 (dependencies: MIT / Apache-2.0) | https://github.com/LibreHardwareMonitor/LibreHardwareMonitor |
| pywebview | 6.x | BSD-3-Clause | https://github.com/r0x0r/pywebview |
| pythonnet | 3.x | MIT | https://github.com/pythonnet/pythonnet |
| psutil | 7.x | BSD-3-Clause | https://github.com/giampaolo/psutil |
| pystray | 0.19 | LGPL-3.0 | https://github.com/moses-palmer/pystray |
| Pillow | 12.x | MIT-CMU (HPND) | https://github.com/python-pillow/Pillow |
| Microsoft Edge WebView2 Runtime | system | Microsoft license (preinstalled on Windows 11) | https://developer.microsoft.com/microsoft-edge/webview2/ |

Not bundled: the **PawnIO** driver (https://pawnio.eu/, by namazso), which LibreHardwareMonitorLib uses for CPU sensors. Since 1.2.1 Taskvane doesn't ship it, because combining a GPL-3.0 app with a signed, proprietary driver build conflicts with GPL-3's Installation Information terms. Users install it from its author's site; Taskvane only detects it.
