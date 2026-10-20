---
title: Why is my laptop so hot? Find the app that's causing it
seoTitle: Why is my laptop so hot? Find the app that's causing it
description: Is your laptop hot and loud? Learn how to find runaway apps using high CPU, check temperature history, fix airflow issues, and stop overheating on Windows.
targetQuery: why is my laptop overheating
published: 2026-10-27
updated: 2026-10-27
promise: Track down runaway processes, check temperature history, and fix laptop heat and fan noise.
related:
  - normal-cpu-temperature
  - check-cpu-temperature-windows-11
faq:
  - q: Why is my laptop fan always running even when I am not doing anything?
    a: A laptop fan runs continuously when the processor cannot shed heat. This happens when a background app keeps CPU usage high, dust insulates the internal heatsink, or soft bedding blocks the bottom intake grilles.
  - q: Is it normal for a gaming laptop to get hot to the touch?
    a: Yes. Gaming laptops pack demanding hardware into thin cases. Under heavy loads, processors routinely reach 85 °C to 95 °C, and heat conducts through the chassis and keyboard deck by design.
  - q: Can a single browser tab cause laptop overheating?
    a: Yes. Web pages with unoptimized scripts, continuous video playback, animated ads, or complex web applications can hold a CPU core at maximum capacity indefinitely, spinning up cooling fans.
  - q: Does changing the Windows power mode reduce heat?
    a: Yes. Setting the Windows 11 power mode to Best power efficiency restricts processor boost clocks and lowers core voltage, producing less heat and quieter fans during daily tasks.
---

A laptop that runs hot and spins its fans loudly is usually dealing with one of three issues: a single app keeping the processor busy, blocked air vents trapping heat inside the chassis, or Windows running background tasks such as indexing, updates, or antivirus scans. Most laptops do not overheat because of broken hardware. They get hot because a continuous workload generates heat faster than small internal fans can exhaust it. Finding the cause usually takes a few minutes: check whether software or airflow is responsible, look at the temperatures, then stop the runaway process or clear the vents.

Here is a step-by-step method to locate the culprit, verify your temperatures, and restore normal thermal levels.

## How do you find the app causing the heat?

When your laptop heats up while sitting idle, a runaway process is the most frequent cause. A stuck background service or demanding web page can pin a processor core at 100% capacity without opening an obvious window.

In Taskvane, open the **Processes** page. Taskvane groups processes by app with friendly names, collecting helper processes for a browser under one entry. Click the **CPU** column header to sort apps by processor usage.

<img class="shot" src="/img/processes-1600.webp" srcset="/img/processes-800.webp 800w, /img/processes-1600.webp 1600w" sizes="(max-width: 900px) 100vw, 760px" width="1600" height="936" alt="Taskvane Processes page with processes grouped by app, sorted by CPU use" loading="lazy" decoding="async" />

Watch the list for thirty seconds. Processors spike briefly when opening files, which is normal boost behavior. Look for an app that holds CPU usage high for minutes at a time.

Browser tabs with streaming video, animated ads, or heavy web apps are a common cause of sustained CPU use. If your browser stays near the top of the list, expand its row to see its separate processes, and close the tabs you suspect one at a time until usage drops.

To close a runaway application:

1. Right-click the app in the process list.
2. Select **End task** or **End process tree** to stop the app and its background workers.
3. If you do not recognize the process, click its row to open the details panel and select **Open file location**. This shows where the executable resides so you can verify what it is before stopping it.

You can also check CPU use with other tools:

- **Windows Task Manager**: Built into Windows and opens instantly with `Ctrl + Shift + Esc` without installing software, though its graphs only cover the last 60 seconds and it shows no temperatures. See [Taskvane vs Task Manager](/compare/task-manager/).
- **LibreHardwareMonitor**: Free and open source with a full sensor tree, but it lacks process management. See [Taskvane vs LibreHardwareMonitor](/compare/librehardwaremonitor/).
- **HWiNFO**: The standard for deep hardware diagnostic reports, though its interface lists hundreds of sensors without process management. See [Taskvane vs HWiNFO](/compare/hwinfo/).

## How hot is your laptop and how long has it been running hot?

The temperature tells you whether the laptop is just warm under load or near its limit. Taskvane labels every temperature reading with a status band:

| Band | Temperature | What it means on a laptop |
| :--- | :--- | :--- |
| **Normal** | Below 70 °C | Quiet cooling and cool surfaces. Standard for idle, web browsing, and office work. |
| **Warm** | 70 to 84 °C | Moderate load. Fans spin audibly. Expected during photo editing or casual gaming. |
| **Hot** | 85 to 94 °C | Heavy load. Underside feels hot. Safe for short bursts, but cooling is near capacity. |
| **Critical** | 95 °C and up | At the thermal limit. Modern laptop CPUs will throttle clock speeds to protect hardware. |

To see what happened over time, open the **Performance** page. Its graphs go back up to 1 hour with hover readouts: CPU load, and GPU temperature. CPU temperature isn't graphed there, but Taskvane records it, and the **CSV export** of the last hour includes a CPU temperature column you can open in Excel or any spreadsheet.

<img class="shot" src="/img/performance-1600.webp" srcset="/img/performance-800.webp 800w, /img/performance-1600.webp 1600w" sizes="(max-width: 900px) 100vw, 760px" width="1600" height="936" alt="Taskvane Performance page showing hardware usage graphs and 1-hour history" loading="lazy" decoding="async" />

Together they show whether you had a brief spike when a program started or the CPU has been busy and hot for the last forty minutes.

Without administrator mode, Taskvane displays usage numbers, the process list, GPU temperatures, battery power draw, and battery health. CPU temperature, CPU power, and drive temperatures require administrator mode and the free PawnIO driver from `https://pawnio.eu/`. On first launch, click **Enable CPU sensors** on the Overview page, install PawnIO, and click **Restart as administrator**. For sensor setup details, follow [how to check CPU temperature on Windows 11](/guides/check-cpu-temperature-windows-11/). For typical operating ranges, read [what is a normal CPU temperature](/guides/normal-cpu-temperature/).

## What physical problems cause a laptop to overheat?

When CPU usage is low but temperatures remain high, restricted airflow is almost always the cause:

- **Soft surfaces**: Using a laptop on a bed, pillow, blanket, or couch blocks the intake vents on the bottom of the casing. Soft fabric conforms to the chassis and traps heat. Always use a flat desk or a rigid lap tray.
- **Dust in cooling vents**: Cooling fans pull dust and pet hair into the chassis over time. This debris forms a dense layer across heatsink fins, blocking exhaust air. Turn off the laptop, unplug the power adapter, and spray short bursts of compressed air into the intake and exhaust vents to blow out accumulated dust.
- **Dried thermal paste**: On laptops older than three or four years, the thermal paste between the processor and copper cooling pipes hardens and loses thermal conductivity. If an older laptop overheats while idling on a clean desk, fresh thermal paste can lower temperatures noticeably, sometimes by 10 °C or more. Take the laptop to a repair shop if you are not comfortable opening the chassis yourself.

## Is Windows background activity causing the heat?

High processor usage is not always caused by user applications. Windows frequently runs automated maintenance tasks in the background:

- **Windows Update**: When Windows downloads and installs system updates, background processes can keep CPU usage high for a while. Check **Settings > Windows Update** to see if an update is underway. Let the update finish and reboot when prompted.
- **Search indexing**: After a fresh Windows installation or a major feature update, the Windows Search indexer scans your drives to catalog files. This background scan can run for several hours, but it stops automatically once indexing is complete.
- **Antivirus scans**: Windows Defender and third-party antivirus utilities schedule periodic background scans that temporarily raise CPU load and fan speeds.
- **Startup programs**: Many applications add background updaters and helpers that launch when your computer boots. In Taskvane, open the **Startup apps** page to see what launches when Windows starts and switch items on or off, the same way Task Manager does.

## How does the Windows 11 power mode affect temperature?

Windows 11 includes power modes that control how aggressively processor boost clocks operate. You can adjust this setting under **Settings > System > Power & battery > Power mode**:

- **Best power efficiency**: Lowers peak clock speeds and core voltages. This limits maximum heat production and keeps cooling fans quiet during everyday tasks.
- **Balanced**: Adjusts clock speeds dynamically based on workload demands. This is the standard setting for everyday use.
- **Best performance**: Prioritizes higher clock speeds even during light workloads, which increases power draw, generates extra heat, and makes fans run louder.

Selecting Best power efficiency or Balanced keeps the chassis cooler and extends battery run time. To see how much power your laptop consumes under each mode, read [how to check laptop power draw in watts](/guides/check-laptop-power-draw-watts/).

## How do you set up alerts before your laptop overheats?

Catching high heat early helps you close runaway tasks before your laptop starts thermal throttling.

Taskvane's alerts are on by default and send a Windows notification. You can change each limit in **Settings > Alerts**:

| Alert | Default |
| :--- | :--- |
| CPU temperature above | 90 °C (needs administrator mode) |
| GPU temperature above | 85 °C |
| Sustained CPU usage above | 95%, averaged over 1 minute |
| Memory usage above | 90% |
| Battery below (on battery) | 15% |

The sustained CPU alert is the one that catches a runaway background task: a short spike won't trigger it, a busy minute will.

You can also click the **Mini widget** button in the sidebar. This opens a compact, always-on-top floating panel displaying CPU and GPU load, temperatures, and power draw in watts, letting you monitor hardware stats without keeping the full window open.

## What fixes should you avoid when dealing with heat?

When troubleshooting a hot laptop, avoid software utilities that promise easy fixes:

- **Avoid PC cleaners and booster software**: Registry cleaners, driver-updater apps, and PC booster utilities do not fix heat problems. Some of them add their own background services, which only adds load.
- **Do not terminate unknown processes blindly**: Ending unfamiliar system tasks can crash Windows or cause data loss. If you see an unfamiliar process using CPU time, right-click it in Taskvane and use the details panel with **Open file location** to check what it is before stopping it.
- **Do not disable cooling fans**: Avoid third-party tools that force fan speeds to stay low. If fans are spinning loudly, the cooling system is reacting to real heat, and throttling fan speeds can lead to emergency thermal shutdowns.

## When is a hot laptop completely normal?

Some laptop heat is expected and designed into the hardware. High-performance gaming laptops and compact thin notebooks pack demanding components into small enclosures with limited cooling area.

Under demanding workloads like 3D gaming, video exports, or code compilation, mobile processors regularly run between 85 °C and 94 °C. Chip manufacturers engineer these processors to boost aggressively until they reach thermal thresholds. Heat naturally radiates through the keyboard deck and chassis surfaces during heavy use.

If your laptop reaches 90 °C during a game but drops back quickly once you close it, the cooling is doing its job. Heat is only a concern when temperatures stay high while idling, or when thermal throttling causes sudden frame drops and system lag. For full details on operating limits, see [what is a normal CPU temperature](/guides/normal-cpu-temperature/).
