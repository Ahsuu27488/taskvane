---
title: How to log CPU temperature and usage over time (and prove a problem)
seoTitle: How to log CPU temperature over time (and prove a problem)
description: Task Manager saves no history. Learn how to log CPU temperature and usage to CSV over time using Taskvane or HWiNFO to prove thermal throttling or heat issues.
targetQuery: how to log CPU temperature over time
published: 2026-11-02
updated: 2026-11-02
promise: Task Manager saves nothing. How to record CPU temp and usage to CSV, spot throttling, and prove a defect.
related:
  - laptop-overheating-causes
  - normal-cpu-temperature
  - task-manager-alternatives-windows-11
compare: hwinfo
faq:
  - q: Can I log CPU temperature for a full day with Taskvane?
    a: Taskvane stores a rolling history of the last hour (3,600 samples) in memory. To log across an entire day without manual hourly exports, use HWiNFO, which writes sensor readings directly to a file on your disk for as long as you leave it open.
  - q: What format does Taskvane use for the history export?
    a: Taskvane exports standard comma-separated values (CSV) with one row per second. The file includes local timestamps and columns for CPU, memory, and GPU usage, CPU and GPU temperatures in °C, power draw in watts, disk activity, and network transfer rates.
  - q: Why is the cpu_temp column empty in my exported CSV file?
    a: Reading the CPU's temperature sensor needs a driver. Taskvane uses the free PawnIO driver, and Windows only lets apps running as administrator use it. Without administrator mode and PawnIO, Taskvane still records usage, GPU temperature and the other columns, but cpu_temp stays blank.
  - q: Does logging CPU temperature and usage slow down the computer?
    a: Not noticeably. Taskvane uses about 0.4% CPU, and it keeps the samples in memory without writing to disk until you click Export CSV.
---

Windows Task Manager graphs only the last 60 seconds of hardware activity and saves nothing. When you close the window or reboot, that data disappears. If your PC stutters in games, shuts down under load, or suffers from suspected thermal throttling, a 60-second graph cannot help you prove what happened.

To log CPU temperature and usage over time, you need a tool that records history. [Taskvane](/download/) records hardware metrics every second in memory for the last hour and exports the full record to a CSV spreadsheet. For multi-hour stress testing or all-day diagnostic sessions, HWiNFO logs continuous sensor data straight to disk.

Here is how to record CPU temperature and usage, how to read the exported CSV file, and how to use your data to prove thermal throttling.

## How do you log CPU temperature and usage with Taskvane?

Taskvane is a free, open-source (GPL-3.0) Task Manager alternative for Windows 11 and 10. From the moment it launches, Taskvane records a sample every second in memory, keeping a rolling buffer of the last hour (3,600 samples).

Nothing is written to disk until you export. Quitting Taskvane clears this history. However, closing the window minimizes Taskvane to the notification area by default, so recording continues in the background while you play a game or run an application. Taskvane uses about 0.4% CPU, so leaving it running doesn't skew the test.

Taskvane includes history graphs with 1m, 5m, 15m, and 1h ranges with hover readouts across its Overview, Performance, and Power pages.

There is no CPU temperature graph in Taskvane. While GPU temperature has a graph on the GPU performance view, the CPU performance view displays only the current CPU temperature reading. CPU temperature is recorded every second in the background, and those readings are fully preserved in the CSV export.

<img class="shot" src="/img/performance-1600.webp" srcset="/img/performance-800.webp 800w, /img/performance-1600.webp 1600w" sizes="(max-width: 900px) 100vw, 760px" width="1600" height="936" alt="Taskvane Performance page with the CPU usage graph, range buttons for 1m, 5m, 15m and 1h, and the current CPU temperature and package power below it" loading="lazy" decoding="async" />

Without administrator mode, Taskvane records usage, GPU temperature and battery power draw. Recording CPU temperature and CPU power requires administrator mode and the free PawnIO driver from `https://pawnio.eu/`:

1. On first launch, the Overview page displays an **Enable CPU sensors** button. Click it to open the PawnIO download page.
2. Download and run the PawnIO installer.
3. Taskvane detects the driver and changes the button to **Restart as administrator**. Click it and approve the Windows prompt.
4. Optional: in **Settings > General**, turn on **Always start as administrator** so future launches start elevated without a prompt.

To record and export your data:

1. Open Taskvane as administrator before starting your test.
2. Close or minimize the window so Taskvane runs in the notification area.
3. Run your game or workload to reproduce the heating or slowdown.
4. Open Taskvane, click **Settings > Data & access**, and click **Export CSV...** under "Export the last hour of history".
5. A save dialog suggests a filename based on the current date and time, such as `taskvane-20261102-1430.csv`. Choose a folder and click **Save**. A message confirms where the file was saved.

## What data does Taskvane include in the CSV export?

Taskvane exports standard comma-separated values (CSV) with up to 3,600 rows, representing one reading per second for the last hour. If Taskvane ran for less than an hour, it includes rows from the second it started up to the export moment.

Temperatures are always written in degrees Celsius (°C) in the file, regardless of your display setting in the app.

A cell remains empty when no sensor reading was available. The `cpu_temp` column is empty if Taskvane ran without administrator rights and PawnIO. The `power` column reports whole-system draw on battery, or CPU package power (plus GPU package power where available) on AC power; it is blank if neither sensor exists on your system.

The columns appear in this order:

| Column header | Format or unit | What it records |
| :--- | :--- | :--- |
| `time` | `YYYY-MM-DD HH:MM:SS` | Local timestamp, such as `2026-11-02 14:30:05`. |
| `cpu` | % | Overall CPU usage across all cores. |
| `mem` | % | Physical memory usage percentage. |
| `gpu` | % | Usage percentage of the dedicated GPU, or the only GPU. |
| `cpu_temp` | °C | CPU temperature, the same reading Taskvane shows for the CPU (blank without administrator mode and PawnIO). |
| `gpu_temp` | °C | GPU core temperature of the same GPU as the `gpu` column. |
| `power` | W | Power draw in watts (whole system on battery, CPU and GPU package power when plugged in). |
| `disk_r` | Bytes per second | Disk read throughput across all storage drives. |
| `disk_w` | Bytes per second | Disk write throughput across all storage drives. |
| `net_up` | Bytes per second | Network upload throughput across all adapters. |
| `net_down` | Bytes per second | Network download throughput across all adapters. |
| `gpu0`, `gpu1`, ... | % | Usage percentage for each detected graphics processor. |

## How do you analyze the log to spot thermal throttling?

Open the exported CSV file in Microsoft Excel, Google Sheets, or LibreOffice Calc. Highlight `time`, `cpu`, and `cpu_temp` to create a 2D line chart with time on the horizontal axis.

When a processor reaches its thermal limit (TjMax, typically 95 °C to 100 °C), internal safeguards reduce clock speeds and core voltages to prevent heat damage.

The table below is an illustrative example of exported data during a thermal event, not real measurements:

| time | cpu | mem | gpu | cpu_temp | gpu_temp | power | disk_r | disk_w | net_up | net_down | gpu0 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 2026-11-02 14:20:10 | 98 | 62 | 95 | 82 | 74 | 65.2 | 1048576 | 4096 | 12400 | 54200 | 95 |
| 2026-11-02 14:20:11 | 99 | 62 | 96 | 88 | 75 | 68.0 | 524288 | 0 | 11800 | 51200 | 96 |
| 2026-11-02 14:20:12 | 100 | 62 | 95 | 96 | 76 | 71.4 | 0 | 0 | 13200 | 53100 | 95 |
| 2026-11-02 14:20:13 | 100 | 62 | 91 | 99 | 77 | 72.1 | 0 | 8192 | 12900 | 52800 | 91 |
| 2026-11-02 14:20:14 | 99 | 62 | 78 | 100 | 77 | 54.3 | 0 | 0 | 11400 | 50900 | 78 |
| 2026-11-02 14:20:15 | 98 | 62 | 72 | 98 | 76 | 48.7 | 0 | 0 | 12100 | 51600 | 72 |

This sample sequence shows how thermal throttling presents in log data:

- **Temperature pins at the limit**: CPU temperature climbs quickly to 100 °C and stays pinned at the chip's thermal ceiling.
- **Power draw drops under load**: CPU usage stays pegged at 98% to 100%, but power draw drops from 72.1 W to 48.7 W. The chip lowered its clock speeds and voltages to shed heat, doing less work per second.
- **GPU usage falls too**: GPU usage drops from 95% to 72% while the game is still running, a sign that the slowed-down CPU is holding the GPU back.

Keep the limits in mind: the export has no clock-speed column and no throttling flags. Pinned temperatures with falling power draw suggest thermal throttling, but they don't prove it. For clock speeds and throttling flags, log with HWiNFO.

To check standard operating bands across chips, see [what is a normal CPU temperature](/guides/normal-cpu-temperature/).

## What tools should you use for all-day or multi-hour logging?

Taskvane keeps only the last hour. If you need to log hardware over four hours, overnight, or across an entire workday without exporting each hour, dedicated logging monitors are the right choice.

Here is how other tools handle hardware logging:

- **HWiNFO**: Multi-hour or all-day logging is HWiNFO's strength. It logs any of its sensors, including clock speeds and throttling flags, to a CSV file for as long as you leave it running. Its sensor list is far longer than most people need. See [Taskvane vs HWiNFO](/compare/hwinfo/).
- **LibreHardwareMonitor**: A free, open-source monitor that presents a full hardware sensor tree and can log sensors to a file, though it lacks process management. See [Taskvane vs LibreHardwareMonitor](/compare/librehardwaremonitor/).
- **Windows Task Manager**: Built into Windows and opens instantly with `Ctrl + Shift + Esc` without installing software, but its graphs only cover the last 60 seconds and it saves nothing. See [Taskvane vs Task Manager](/compare/task-manager/).
- **Windows Performance Monitor**: Built into Windows as `perfmon` and can record CPU usage for hours, but it has no temperature counter for most PCs.

Use Taskvane when you want a clear everyday monitor with process controls, hardware alerts, and a quick one-hour export. Use HWiNFO when you need continuous logging across many hours or every sensor your PC has.

## How do you document heat issues for a warranty claim or repair?

A single high reading rarely convinces a repair shop or support team, because modern processors boost hard and run hot under load by design. A record over time is more useful.

To build a clear warranty or repair case, collect verifiable documentation:

1. **Record test conditions**: Note the room temperature, the Windows power mode, and what the laptop was resting on (a flat desk, not bedding).
2. **Document the workload**: Note the exact game, export, or benchmark running, and how many minutes elapsed before stutter or shutdowns began.
3. **Save the raw CSV log**: Export the Taskvane CSV file. Rows with the temperature pinned near the limit while power drops show the pattern described above.
4. **Capture the graphs**: Save the line chart you made from the CSV, and a screenshot of Taskvane's Performance page on the 1h range.
5. **Note the symptoms**: Write down what you saw, such as frame rate drops, audio stutter or sudden shutdowns, and when.

A timestamped log shows whether high temperatures were sustained or just brief spikes, which gives a technician something concrete to start from.

To track down runaway background apps or fix airflow issues, read [why is my laptop overheating](/guides/laptop-overheating-causes/), or check the [Taskvane features](/features/) page for an overview of supported hardware readings.
