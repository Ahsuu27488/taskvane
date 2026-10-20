---
title: How to check CPU temperature on Windows 11
seoTitle: How to check CPU temperature on Windows 11 (3 ways)
description: Windows 11 does not show CPU temperature in Task Manager. Here are three ways to check your CPU temp, why Windows makes it hard, and what your readings mean.
targetQuery: how to check CPU temperature Windows 11
published: 2026-10-21
updated: 2026-10-21
promise: Task Manager won't show it. Three ways that do, and what your reading means.
related:
  - normal-cpu-temperature
compare: librehardwaremonitor
faq:
  - q: Does Windows 11 show CPU temperature anywhere built in?
    a: No. Windows 11 Task Manager only displays GPU temperatures for some dedicated graphics cards. There is no built-in app, widget, or settings page in Windows 11 that shows your current CPU temperature.
  - q: Why does Taskvane need admin rights for CPU temperature but not GPU temperature?
    a: Windows exposes GPU metrics through standard graphics driver APIs without administrative privileges. CPU sensors require reading processor model-specific registers through a kernel-level hardware driver, which Windows restricts to elevated administrator processes for security.
  - q: Is 90 °C dangerous while gaming?
    a: A temperature of 90 °C is not immediately dangerous for modern processors during heavy gaming, but it is hot. Modern CPUs have built-in safeguards to prevent damage, but sustained temperatures above 85 °C indicate your cooling system is working near its limit.
  - q: Why do the cores show different temperatures?
    a: Processor cores handle different tasks and boost their clock speeds independently. A core running a demanding thread will heat up faster than idle cores, so temperature variations across cores are completely normal.
---

Windows 11 does not show CPU temperature in Task Manager. While Task Manager displays CPU utilization, clock speeds, and even GPU temperatures for some dedicated graphics cards, it never shows the processor's temperature. Nothing else built into Windows does either.

To check your CPU temperature on Windows 11, you have three practical paths:

1. Restart your computer into its UEFI or BIOS setup screen to see the motherboard hardware monitor without installing any software.
2. Use Taskvane, a free, open-source Task Manager alternative that shows per-core temperatures next to your running apps.
3. Use established diagnostic tools such as HWiNFO or LibreHardwareMonitor.

Here is how each approach works, along with the trade-offs and what your numbers mean.

## Can you check CPU temperature in BIOS or UEFI without software?

If you need a quick reading and do not want to install any third-party tools, your motherboard firmware is the only built-in source for hardware temperatures. Modern motherboards monitor hardware sensors directly at the firmware level.

To reach the UEFI setup screen from Windows 11 without pressing keys during boot:

1. Open Windows **Settings** (press `Windows + I`).
2. Navigate to **System > Recovery**.
3. Under **Recovery options**, find **Advanced startup** and click **Restart now**.
4. When your computer reboots into the blue recovery environment, select **Troubleshoot > Advanced options > UEFI Firmware Settings**.
5. Click **Restart**. Your PC will boot directly into the motherboard BIOS interface.

Once inside the UEFI interface, look for a tab named **Hardware Monitor**, **H/W Monitor**, **PC Health**, or **Status**. You will see live readouts for your CPU temperature, system fan speeds, and voltage rails.

This needs no software, but it has two big limits. You have to restart your PC to get there, and the reading only reflects the processor at idle in a basic operating state. It cannot show you how hot the CPU runs under heavy load, such as while playing a modern game, compiling code, or rendering video. To monitor temperatures during actual use, you need a desktop tool running inside Windows.

## How do you check CPU temperature with Taskvane?

Taskvane is a free, open-source (GPL-3.0) Task Manager alternative for Windows 11 and 10. It shows the usual graphs and process list, and adds hardware readings that Windows leaves out: CPU core temperatures, package temperature, GPU hot spots, power draw in watts, and battery health.

Because Windows restricts access to processor sensors, Taskvane reads temperatures through LibreHardwareMonitorLib using the signed PawnIO hardware driver. Taskvane doesn't bundle or install PawnIO itself; you get it from its author. The setup takes a couple of minutes:

1. Download and open Taskvane.
2. On first launch, the Overview page displays a banner stating **CPU temperature and CPU power are off** with an **Enable CPU sensors** button.
3. Click **Enable CPU sensors**. This opens `pawnio.eu`, the official website of the PawnIO driver author.
4. Download and run the PawnIO installer from that site.
5. Taskvane automatically detects when PawnIO is installed, and the button changes to **Restart as administrator**.
6. Click **Restart as administrator** and approve the standard Windows User Account Control (UAC) prompt.

Within a few seconds, live temperature readouts appear on the Overview and Sensors pages. Every CPU core temperature is displayed alongside the overall package temperature. The Sensors page also keeps the minimum and maximum since Taskvane started, and every reading gets a label: Normal, Warm, Hot or Critical.

<img class="shot" src="/img/sensors-1600.webp" srcset="/img/sensors-800.webp 800w, /img/sensors-1600.webp 1600w" sizes="(max-width: 900px) 100vw, 760px" width="1600" height="936" alt="Taskvane Sensors page displaying CPU core temperatures, package temperature, and status labels" loading="lazy" decoding="async" />

If you do not want to approve a UAC prompt every time you launch Taskvane, you can turn on **Settings > Always start as administrator**. While running with administrative rights, Taskvane registers an elevated scheduled task. Subsequent launches start elevated immediately without prompting.

Without administrator mode Taskvane still shows all usage numbers, the process list, battery power draw and GPU temperatures. Only CPU temperature, CPU power and drive temperatures need it.

## What other tools can check CPU temperature?

Several well-known free tools also show CPU temperature on Windows 11:

- **LibreHardwareMonitor**: A free, open-source monitor that presents a comprehensive hardware sensor tree covering every motherboard, fan, and chip sensor. Taskvane uses its underlying sensor library. You can read our detailed comparison in [Taskvane vs LibreHardwareMonitor](/compare/librehardwaremonitor/).
- **HWiNFO**: The industry standard for deep hardware diagnostic reports, offering hundreds of sensor parameters, rail voltages, memory timings, and logging. It is free for personal use and closed source. See our comparison in [Taskvane vs HWiNFO](/compare/hwinfo/).
- **Core Temp**: A compact utility focused specifically on per-core processor temperatures, frequency, and power consumption with minimal memory overhead.
- **HWMonitor**: A classic hardware monitor from CPUID that lists temperatures, voltages, and fan speeds in a single hierarchical view.

All of them need administrator rights and a kernel driver for CPU readings, for the reason explained next.

## Why does Windows 11 make checking CPU temperature so difficult?

People often wonder why a basic statistic like processor temperature requires installing third-party drivers or launching software as administrator. The reason comes down to Windows security architecture and hardware design.

Modern x86 processors from Intel and AMD do not expose temperature through a standard Windows user-space API. Instead, digital thermal sensors write temperature data directly into processor-specific hardware registers known as Model-Specific Registers (MSRs). On motherboards, additional temperature probes feed into proprietary Super I/O chips.

Accessing MSRs and Super I/O controllers requires executing low-level processor instructions that can only run in Ring 0 (kernel mode). Because an untrusted application running kernel code could compromise system stability or read protected memory, Windows strictly forbids standard user applications from communicating directly with hardware registers. A signed kernel driver is mandatory.

This also explains why Task Manager shows GPU temperature for dedicated graphics cards, but not CPU temperature. The graphics driver (NVIDIA, AMD or Intel) already runs in the kernel and reports the GPU's temperature to Windows, so any app can read it. There's no equivalent standard path for CPU sensors.

You might see suggestions online to check CPU temperature using PowerShell commands like `Get-CimInstance MSAcpi_ThermalZoneTemperature`. In practice that reading is unreliable. On most modern desktop PCs and laptops, the ACPI thermal zone interface is either completely missing, unimplemented by motherboard vendors, or reports an unchanging stuck value that represents a motherboard sensor rather than CPU core silicon. Don't rely on it for CPU temperature.

## What should your CPU temperature read?

CPU temperature changes quickly with workload, room temperature and cooling, so read it as a range, not a single number.

Taskvane puts every reading into one of four bands:

| Band | Temperature | What it means |
| :--- | :--- | :--- |
| **Normal** | Below 70 °C | Healthy operating temperatures. Below 50 °C indicates idle or light use. 50 to 69 °C is typical for everyday work like web browsing, running office apps, and video conferencing. |
| **Warm** | 70 to 84 °C | Standard operating range under moderate load. Typical while gaming, compiling software, or rendering video. Cooling fans spin up noticeably. |
| **Hot** | 85 to 94 °C | Heavy sustained load. Safe for short bursts, but indicates your cooling system is running near capacity. Check for dust or blocked ventilation if it stays here continuously. |
| **Critical** | 95 °C and up | At the thermal limit. Modern processors will begin thermal throttling around 100 °C to protect themselves. |

A quick temperature spike into the Warm or Hot band when opening an application is normal behavior for modern boost algorithms. However, if your processor sits above 85 °C while idle, or quickly hits 95 °C under light loads, your cooling setup needs attention.

For where these limits come from (TjMax), why some chips run at 95 °C by design, and what to do about heat, read [what is a normal CPU temperature](/guides/normal-cpu-temperature/).
