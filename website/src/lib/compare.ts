// Comparison pages. Keep claims conservative and fair: say where the other tool wins.
type Cell = 'yes' | 'no' | string;
export interface Comparison {
  slug: string;
  other: string;
  title: string;
  description: string;
  intro: string;
  rows: [string, Cell, Cell][];      // [what, other, taskvane]
  otherWins: string[];
  taskvaneWins: string[];
  verdict: string;
}

export const COMPARISONS: Comparison[] = [
  {
    slug: 'task-manager',
    other: 'Task Manager',
    title: 'Taskvane vs Windows Task Manager: temperatures, power draw and more',
    description:
      'How Taskvane compares with the Windows 11 Task Manager: CPU temperature, power draw in watts, battery health, alerts and history graphs, and what Task Manager still does better.',
    intro:
      "Task Manager is built into Windows and great for managing apps and services. It doesn't show CPU temperature, power draw or battery health, and its graphs only cover the last minute. Taskvane keeps the familiar parts and adds the hardware side.",
    rows: [
      ['Price', 'Built into Windows', 'Free, open source (GPL-3.0)'],
      ['CPU, memory, disk, network and GPU usage', 'yes', 'yes'],
      ['Processes grouped by app, end task, set priority', 'yes', 'yes'],
      ['Startup apps on/off', 'yes', 'yes'],
      ['CPU core and package temperature', 'no', 'yes'],
      ['GPU temperature', 'Dedicated GPUs only', 'Yes, plus hot spot'],
      ['Power draw in watts', 'no', 'yes'],
      ['Battery health, wear and time left at current draw', 'no', 'yes'],
      ['History graphs', 'Last 60 seconds', 'Up to 1 hour, CSV export'],
      ['Alerts for heat, memory, battery, CPU load', 'no', 'yes'],
      ['Always-on-top mini widget', 'no', 'yes'],
      ['Services, users, per-app network use, app history', 'yes', 'no'],
      ['Efficiency mode', 'yes', 'no'],
    ],
    otherWins: [
      'Nothing to install, and it opens with Ctrl+Shift+Esc on any Windows PC.',
      'Manages Windows services and signed-in users.',
      'Shows network and GPU use per app, and app history over time.',
      'Efficiency mode for throttling a single app.',
    ],
    taskvaneWins: [
      'CPU core and package temperatures, GPU hot spot and SSD temperatures.',
      'Power draw in watts and battery health.',
      'An hour of history with hover readouts and CSV export.',
      'Alerts before your PC overheats, and an always-on-top mini widget.',
    ],
    verdict:
      'Keep Task Manager for services and quick fixes. Use Taskvane when you want to know how hot your PC runs, how much power it draws, or what happened over the last hour.',
  },
  {
    slug: 'hwinfo',
    other: 'HWiNFO',
    title: 'Taskvane vs HWiNFO: a simpler way to watch temperatures and power',
    description:
      'Taskvane vs HWiNFO for Windows: sensor depth, ease of use, process management, alerts, licensing and open source. Which hardware monitor fits you?',
    intro:
      'HWiNFO is the most detailed hardware information and sensor tool for Windows, trusted by enthusiasts and reviewers for years. It shows far more sensors than most people need. Taskvane focuses on the readings that matter day to day, and pairs them with a Task Manager-style view of your apps.',
    rows: [
      ['Price and license', 'Free for personal use, paid Pro for commercial use; closed source', 'Free for everyone, open source (GPL-3.0)'],
      ['Sensor depth (voltages, clocks, every rail)', 'Exceptional', 'Main readings, with all sensors in a list'],
      ['CPU and GPU temperatures', 'yes', 'yes'],
      ['Power draw', 'yes', 'yes'],
      ['Detailed hardware report (model numbers, chipset, SPD)', 'yes', 'no'],
      ['Process list and end task', 'no', 'yes'],
      ['Startup apps', 'no', 'yes'],
      ['Battery health and time left at current draw', 'Battery details', 'yes'],
      ['Graphs with hover readouts', 'Per-sensor graphs', 'Dashboards up to 1 hour'],
      ['Alerts', 'yes', 'yes'],
      ['On-screen display in games', 'Via RivaTuner', 'Mini widget (not in fullscreen games)'],
      ['Logging', 'Long-term CSV logging', 'Last hour to CSV'],
    ],
    otherWins: [
      'Far more sensors and detail, including voltages, fan headers and memory timings.',
      'Full hardware reports for troubleshooting or selling a PC.',
      'Long-term logging and an in-game overlay through RivaTuner.',
    ],
    taskvaneWins: [
      'A clean, guided view: temperatures labelled Normal to Critical instead of hundreds of raw values.',
      'Processes, startup apps and end task in the same window.',
      'Fully open source and free for any use, including at work.',
    ],
    verdict:
      'Choose HWiNFO for deep diagnostics, overclocking and long logging sessions. Choose Taskvane for a clear everyday view of temperatures, power and apps in one place.',
  },
  {
    slug: 'librehardwaremonitor',
    other: 'LibreHardwareMonitor',
    title: 'Taskvane vs LibreHardwareMonitor: same sensors, plus processes and power',
    description:
      'Taskvane uses LibreHardwareMonitor’s open-source sensor library. Compare the two: interface, process management, battery power, alerts, history and installation.',
    intro:
      'LibreHardwareMonitor is an excellent open-source sensor monitor, and Taskvane is built on its sensor library, so both read the same temperatures and power values. The difference is everything around the sensors.',
    rows: [
      ['License', 'Open source (MPL-2.0)', 'Open source (GPL-3.0)'],
      ['Sensor readings', 'Full sensor tree', 'Same library: all sensors list, plus summary views'],
      ['Temperature status (Normal to Critical)', 'no', 'yes'],
      ['Process list, end task, priority', 'no', 'yes'],
      ['Startup apps', 'no', 'yes'],
      ['Whole-laptop power draw and battery health', 'Battery sensors', 'Yes, with time left at current draw'],
      ['History', 'Plot window', 'Dashboards up to 1 hour, CSV export'],
      ['Alerts', 'no', 'yes'],
      ['Remote web server', 'yes', 'no'],
      ['Installer and one-click driver setup', 'Portable app', 'Installer or portable; guided PawnIO setup'],
    ],
    otherWins: [
      'A built-in web server for viewing sensors from another device.',
      'A complete sensor tree for every component, in a tiny portable app.',
      'The upstream project: new hardware support lands there first.',
    ],
    taskvaneWins: [
      'Temperatures explained with status labels, plus process and startup management.',
      'Whole-laptop power draw, battery health and alerts.',
      'Guided setup for administrator mode and the PawnIO driver.',
    ],
    verdict:
      'If you want a raw sensor tree or remote viewing, LibreHardwareMonitor is perfect. If you want those sensors inside an everyday Task Manager replacement, use Taskvane.',
  },
];
