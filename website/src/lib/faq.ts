// FAQ content: rendered on /faq/ and emitted as FAQPage structured data.
// Answers are plain sentences so search engines and AI assistants can quote them directly.
export const FAQ: { q: string; a: string }[] = [
  {
    q: 'What is Taskvane?',
    a: 'Taskvane is a free, open-source Task Manager alternative for Windows 11 and Windows 10. It shows CPU, GPU, memory, disk and network usage like Task Manager, and adds CPU and GPU temperatures, power draw in watts, battery health, alerts and an always-on-top mini widget.',
  },
  {
    q: 'How do I see my CPU temperature on Windows 11?',
    a: "Windows 11 Task Manager doesn't show CPU temperature. Install Taskvane, open it, and click Enable CPU sensors: it opens pawnio.eu, where you install the free PawnIO driver, and then Taskvane restarts as administrator. It then shows the temperature of every CPU core and the CPU package, and labels each reading Normal, Warm, Hot or Critical.",
  },
  {
    q: 'How do I check how many watts my laptop is using?',
    a: "Open Taskvane while your laptop is running on battery. The Power draw tile shows the whole laptop's power draw in watts, read from the battery, along with how long the charge will last at that rate. When plugged in, Windows doesn't report whole-system power, so Taskvane shows CPU and GPU package power instead (administrator mode).",
  },
  {
    q: 'Is Taskvane free?',
    a: 'Yes. Taskvane is free and open source under the GPL-3.0 license. It has no ads, no account and no telemetry, and the only network request it makes on its own is an optional daily update check that asks GitHub for the latest version number (no personal data; turn it off in Settings).',
  },
  {
    q: 'Why does Taskvane need administrator rights?',
    a: "Only for CPU temperature, CPU power and drive temperatures. Windows only lets programs running as administrator read those sensors. Everything else, including GPU temperatures, usage and battery power draw, works without admin rights. You can turn on Always start as administrator to avoid a UAC prompt on every launch.",
  },
  {
    q: 'What is PawnIO and is it safe?',
    a: "PawnIO is a small, digitally signed hardware driver used by LibreHardwareMonitor and other monitoring tools to read CPU sensors. Taskvane doesn't bundle it: you install it yourself from its author's site, pawnio.eu (the Enable CPU sensors button opens it), and you can remove it any time from Settings > Apps.",
  },
  {
    q: 'Will Taskvane slow down my PC?',
    a: 'No. Taskvane uses about 0.4% of the CPU with its window open. It reads every process in a single Windows system call, the same source Task Manager uses, and runs hardware sensors in a separate helper process.',
  },
  {
    q: 'Does Taskvane work on Windows 10?',
    a: 'Yes. Taskvane works on Windows 10 version 1809 or later and on Windows 11, 64-bit. It needs the Microsoft Edge WebView2 Runtime, which is built into Windows 11 and most Windows 10 PCs.',
  },
  {
    q: 'Windows says "Windows protected your PC". Is the download safe?',
    a: "SmartScreen shows that warning for new apps that aren't code-signed yet. Click More info, then Run anyway. You can check the file against the SHA-256 checksums published with every release, or build Taskvane yourself from the source on GitHub.",
  },
  {
    q: 'Is there a portable version?',
    a: 'Yes. Download the Portable zip from the download page, unzip it anywhere and run Taskvane.exe. It keeps its settings in a data folder next to the app and installs nothing.',
  },
  {
    q: 'How do I uninstall Taskvane?',
    a: "Open Settings > Apps > Installed apps in Windows, find Taskvane and choose Uninstall. This removes the app, its shortcuts and its scheduled tasks. It doesn't touch the PawnIO driver, which you installed separately; uninstall it from the same list if you want.",
  },
];
