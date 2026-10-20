---
title: How to check how many watts your laptop is using
seoTitle: How to check how many watts your laptop is using
description: Windows does not show laptop power draw in watts. Learn how to check live power consumption on battery or AC, and what typical wattages look like.
targetQuery: how to check laptop power consumption
published: 2026-10-27
updated: 2026-10-27
promise: Task Manager won't show watts. How to see whole-laptop draw, and what normal numbers look like.
related:
  - check-battery-health-windows-11
  - laptop-overheating-causes
compare: task-manager
faq:
  - q: Can Task Manager show how many watts my laptop is using?
    a: No. Windows Task Manager only displays a relative "Power usage" rating such as Very low, Low, or Very high. It does not display actual power consumption in watts for individual applications or for the overall system.
  - q: Why can software only measure whole-laptop watts on battery?
    a: When running on battery, Windows queries the laptop smart battery fuel gauge, which reports exact discharge current and voltage. When plugged in, the laptop runs mostly from the charger and the battery reports its charging, not what the laptop uses, and Windows has no standard reading for the charger's output. So on AC you need a plug-in meter for the whole laptop.
  - q: How many watts should a laptop use while idle?
    a: A modern thin laptop typically uses between 3 W and 8 W while idle with the display at moderate brightness. Gaming laptops or workstations with larger screens and background processes usually idle higher, between 12 W and 25 W.
  - q: How do watts relate to battery life?
    a: You can estimate battery runtime by dividing your battery capacity in watt-hours (Wh) by your current power draw in watts (W). For example, a 50 Wh battery running at a steady 10 W draw will last approximately 5 hours.
---

To check how many watts your laptop is using, unplug the power cable and read the battery discharge rate in a system monitor. Windows can only measure whole-laptop power draw when running on battery, because the battery's internal fuel gauge reports the rate of energy leaving the cells. Plugged in, the laptop runs from the charger and Windows has no standard reading for that, so software can only show parts of it, such as CPU package power.

If you want a live reading of your laptop's total power consumption, the simplest method is to unplug the charger and check your discharge rate using [Taskvane](/download/).

## Why can software only measure whole-system watts on battery?

Windows can only report power consumption when hardware sensors expose it.

Inside every laptop battery is a smart battery management system with a fuel gauge chip. When running on battery power, all electrical current powering the display, processor, storage, fans, and wireless radio must leave the battery pack. The fuel gauge measures this outgoing current and voltage to calculate the discharge rate in watts. Windows reads this rate through ACPI, giving software a clean reading of whole-system draw.

Connecting the AC adapter changes that path. Electricity enters a motherboard circuit that splits current between recharging battery cells and powering hardware directly. Windows has no standard sensor reading for the power coming in from the charger, so apps can't see the total.

While plugged in, processors and graphics cards can report internal chip power such as CPU package power. But these readings leave out the display, motherboard conversion losses, and fans. To measure the entire laptop as a complete system, you must run it on battery.

## How do you check laptop watts with Taskvane?

[Taskvane](/download/) is a free, open-source (GPL-3.0) Task Manager alternative for Windows 11 and 10 that adds what Task Manager leaves out, including live power draw in watts.

To check your laptop's power draw:

1. Download and open Taskvane.
2. Unplug the charger to switch to battery power.
3. Look at the **Overview** page. The **Power draw** tile displays your live power consumption in W, with the label **Whole system**.
4. Click **Power** in the sidebar to open the dedicated power and battery view.

The Power page displays **Whole-system draw measured at the battery**, showing your live **Discharge rate** in W, the calculated **Time left at this rate**, and your battery health. The power graph tracks your consumption over time, storing up to 1 hour of history with hover readouts that you can export as a CSV file.

<img class="shot" src="/img/power-1600.webp" srcset="/img/power-800.webp 800w, /img/power-1600.webp 1600w" sizes="(max-width: 900px) 100vw, 760px" width="1600" height="936" alt="Taskvane Power page showing whole-system draw measured at the battery, discharge rate, and battery health" loading="lazy" decoding="async" />

When you plug the charger back in, the Power page switches to show your **Charge rate** in W. On the Overview page, the Power draw tile adjusts based on permissions. In administrator mode, it shows CPU package power and GPU power where reported. Without administrator mode, it shows **Unplug to measure the whole system**.

Battery watts need no administrator mode. CPU package power does: it needs administrator mode and the free PawnIO driver, which the **Enable CPU sensors** button helps you install (see [how to check CPU temperature on Windows 11](/guides/check-cpu-temperature-windows-11/)).

If you want to track wattage while working in other apps, click the mini widget button. It opens an always-on-top floating panel showing CPU and GPU load, temperatures, and watts.

<img class="shot" src="/img/overview-1600.webp" srcset="/img/overview-800.webp 800w, /img/overview-1600.webp 1600w" sizes="(max-width: 900px) 100vw, 760px" width="1600" height="936" alt="Taskvane Overview page showing the Power draw tile, temperatures, and hardware load" loading="lazy" decoding="async" />

## What other tools can measure laptop power?

Other tools can also inspect power, though each has clear limits:

- **Task Manager**: The Processes tab includes a "Power usage" column, but it only shows relative ratings from Very low to Very high rather than numbers in watts. Task Manager has no watts reading for the whole PC. It is built into Windows and requires no setup, making it convenient for comparing relative app consumption at a glance. See our comparison in [Taskvane vs Task Manager](/compare/task-manager/).
- **Plug-in wall power meter**: A wall meter or smart plug measures true AC draw from the wall outlet including charging current and adapter losses. However, it cannot measure power while mobile or break down consumption by internal component.
- **Windows battery report**: Running `powercfg /batteryreport` in Command Prompt generates an HTML file showing past discharge cycles and battery capacity. It provides a helpful historical log of battery health and sleep drain over days, but it records past events rather than live wattage.
- **HWiNFO**: A diagnostic monitor that reads internal motherboard and rail telemetry. It offers granular sensor logging for advanced troubleshooting, but its crowded interface can feel complex when you only need a quick reading of total laptop wattage. See our comparison in [Taskvane vs HWiNFO](/compare/hwinfo/).

## What is a normal power draw in watts for a laptop?

Normal power consumption depends on your laptop's hardware specifications, display brightness, and current workload.

Here is what typical whole-system power draw looks like on battery:

| Workload | Typical draw (thin laptop) | Typical draw (gaming laptop) | What is happening |
| :--- | :--- | :--- | :--- |
| **Idle at desktop** | 3 W to 8 W | 12 W to 25 W | Minimal background activity, display at moderate brightness, processor in deep C-states. |
| **Web browsing and office apps** | 6 W to 15 W | 18 W to 35 W | Active web scripts, typing, intermittent CPU clock boosts. |
| **Video playback** | 6 W to 12 W | 15 W to 30 W | Hardware video decoder handles playback, keeping general processor cores quiet. |
| **Heavy load or gaming on battery** | 20 W to 35 W | 30 W or more | High CPU and GPU demand. Many gaming laptops limit performance on battery to protect cells. |

Display brightness often represents the single largest power drain at idle. On a thin laptop, raising the screen from minimum to maximum brightness can add 2 W to 5 W of continuous draw. At light loads the screen is often one of the biggest single power users.

## How do you find which app is causing high power draw?

If your laptop's power draw jumps while sitting idle, a background app is usually keeping the CPU busy. Finding it takes a minute:

1. Open Taskvane and click **Processes** in the sidebar. Processes are grouped by app with friendly names, so all helper processes for a browser appear under one entry.
2. Click the **CPU** column header to sort by processor usage. The app causing the power spike will typically sit near the top.
3. Right-click the app to select **End task** or **End process tree**.
4. Check the details panel and click **Open file location** if you need to identify an unfamiliar process.

In **Settings**, Taskvane can send Windows notifications when the CPU stays busy, memory fills up, the battery gets low, or temperatures run hot. When high power draw leads to warm chassis temperatures and fan noise, read our guide on [laptop overheating causes](/guides/laptop-overheating-causes/) to inspect cooling and airflow.

## How do you calculate battery life from watts?

Knowing your live power draw in watts lets you calculate expected battery runtime using simple division:

`Battery capacity in watt-hours (Wh) / Power draw in watts (W) = Runtime in hours`

Laptop batteries are rated in watt-hours (Wh), usually between 40 Wh and 99 Wh. For example:

- A laptop with a **50 Wh** battery drawing **10 W** lasts about **5 hours** (50 divided by 10).
- Reducing draw to **6 W** by dimming the screen and closing background apps extends runtime to about **8.3 hours**, or 8 hours and 20 minutes (50 divided by 6).
- Running a demanding game or export that pulls **25 W** drains that same battery in **2 hours** (50 divided by 25).

Small changes in wattage create substantial changes in battery life. Saving just 3 W on a 50 Wh battery can give you an extra hour or two of working time away from an outlet.

This calculation assumes your battery holds its full design capacity. Over time, battery wear reduces usable watt-hours. For example, a battery rated 50 Wh that now holds 40 Wh gives you a fifth less runtime at the same wattage. To check your battery's wear level and current capacity, see our guide on [how to check battery health on Windows 11](/guides/check-battery-health-windows-11/).
