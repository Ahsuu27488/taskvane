# Security policy

Taskvane can run with administrator rights and uses a kernel driver (PawnIO, which users install from its author's site), so security reports are taken seriously.

## Reporting a vulnerability

Please **don't open a public issue**. Report it privately through [GitHub Security Advisories](https://github.com/Ahsuu27488/taskvane/security/advisories/new). Include the steps to reproduce, the impact, and the version affected. You'll get a reply within a few days.

## What Taskvane does with elevated rights

- It reads hardware sensors through LibreHardwareMonitorLib and the signed PawnIO driver.
- It ends or re-prioritizes processes, and changes startup entries, **only when you click** those actions.
- With "Always start as administrator" on, it creates the scheduled tasks `Taskvane (administrator)` and `Taskvane (administrator, sign-in)`. Turning the setting off, or uninstalling, removes them.

Taskvane makes **one optional network request**: once a day it asks the public GitHub API (`api.github.com/repos/Ahsuu27488/taskvane/releases/latest`) for the latest version number, so it can tell you about updates. The request carries no personal data or identifiers, nothing is downloaded or installed, and **Settings > Check for updates** turns it off, after which Taskvane makes no network connections except opening links you click in your browser. There is no telemetry.

## Verifying downloads

Every release lists SHA-256 checksums in `SHA256SUMS.txt`. Check a file with:

```powershell
Get-FileHash .\Taskvane-1.2.0-Setup.exe -Algorithm SHA256
```
