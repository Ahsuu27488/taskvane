---
title: How to check battery health on Windows 11
seoTitle: How to check battery health on Windows 11 (and read wear)
description: Windows 11 does not show battery health in Settings. Here is how to generate a battery report, check wear in Taskvane, and preserve your laptop battery.
targetQuery: how to check battery health Windows 11
published: 2026-10-22
updated: 2026-10-22
promise: The two numbers that matter, the exact powercfg steps, and what wear percentages mean.
related:
  - check-laptop-power-draw-watts
faq:
  - q: Does Windows 11 show battery health anywhere in Settings?
    a: No. Windows 11 Settings displays your current charge level and battery usage per app, but omits battery health and capacity degradation. You need to generate an HTML battery report or use an app like Taskvane to see your health percentage.
  - q: Can a worn laptop battery recover its lost capacity?
    a: No. Chemical degradation in lithium-ion cells is permanent. While estimated capacity can shift by two or three percent between charge cycles as the battery management controller recalculates, lost physical capacity cannot return.
  - q: At what wear percentage should you replace a laptop battery?
    a: A wear level above 30 percent (under 70 percent health) typically reduces runtime enough that replacing the battery is worth planning. If your laptop shuts down suddenly or the battery physically swells, replace it right away.
  - q: Why does cycle count show a dash in the battery report?
    a: Some laptop manufacturers and battery fuel gauge chips do not report cycle counts to Windows. When the hardware does not supply the data, the battery report shows a dash instead of a number.
---

To check battery health on Windows 11, compare your battery's full charge capacity to its original design capacity. The ratio gives your health percentage: full charge capacity divided by design capacity. For example, if a battery originally held 50,000 mWh and now holds 40,000 mWh when fully charged, its health is 80%, with 20% wear.

Windows 11 does not display this number in Settings. You can get it in two minutes with the built-in `powercfg /batteryreport` command, or read it on Taskvane's Power page without typing any commands.

Here is how both methods work, how to interpret battery wear, and how to slow down battery aging.

## How do you generate a battery report with powercfg?

The built-in way to check battery health on Windows 11 uses a command-line tool named `powercfg`. You do not need administrator privileges to run it.

Follow these steps to generate your report:

1. Open Windows Terminal or Command Prompt. Press `Windows + R`, type `cmd`, and press Enter.
2. Type `powercfg /batteryreport` and press Enter.
3. Windows inspects the battery controller and creates an HTML file named `battery-report.html` in the folder shown in your prompt, usually `C:\Users\<username>`.
4. To place the file directly on your desktop instead, run:
   ```cmd
   powercfg /batteryreport /output "%USERPROFILE%\Desktop\battery-report.html"
   ```
5. Double-click `battery-report.html` to open it in your web browser.

## How do you read design capacity vs full charge capacity?

Near the top of your report, find the **Installed batteries** section. It lists three key values:

- **DESIGN CAPACITY**: The energy the battery was designed to store when brand new, measured in milliwatt-hours (mWh).
- **FULL CHARGE CAPACITY**: The maximum energy the battery holds now at 100% charge.
- **CYCLE COUNT**: The number of complete discharge cycles completed.

To calculate health and wear:

- Battery health (%) = (Full charge capacity / Design capacity) * 100
- Battery wear (%) = 100% - Battery health (%)

In a real report from an everyday laptop:

- **DESIGN CAPACITY**: 38,000 mWh
- **FULL CHARGE CAPACITY**: 36,404 mWh
- **CYCLE COUNT**: -

Dividing 36,404 mWh by 38,000 mWh gives 0.958, or about 96% health and 4% wear. Its cycle count showed a dash (`-`) because some laptop makers and battery controllers do not report cycle counts to Windows. A dash is normal and does not mean your battery is faulty.

Lower down, the **Battery capacity history** section tracks full charge capacity against design capacity over recent weeks, showing whether capacity faded gradually or dropped suddenly.

## How do you check battery health in Taskvane?

If you prefer not to run terminal commands or calculate percentages, Taskvane displays battery health directly.

Taskvane is a free, open-source (GPL-3.0) Task Manager alternative for Windows 11 and 10.

To check your battery:

1. Open Taskvane and click **Power** in the sidebar.
2. The page shows **Battery health (%)**, **Wear (%)**, and **Capacity vs design** in Wh (full charge / design).
3. You also see current **Charge**, live **Discharge rate** or **Charge rate (W)**, and **Time left at this rate**.

<img class="shot" src="/img/power-1600.webp" srcset="/img/power-800.webp 800w, /img/power-1600.webp 1600w" sizes="(max-width: 900px) 100vw, 760px" width="1600" height="936" alt="Taskvane Power page showing battery health percentage, capacity versus design, and power draw" loading="lazy" decoding="async" />

Battery readings don't need administrator mode or any driver.

When the battery holds under 80% of its design capacity, the **Overview** page also shows a note saying so, so you notice without going looking. A low-battery alert (on by default at 15%) is in **Settings > Alerts**.

## What is a normal battery wear level?

Battery wear is the portion of factory capacity permanently lost through chemical aging. Wear is best read using rules of thumb:

| Wear level | Battery health | What to expect |
| :--- | :--- | :--- |
| **0% to 10%** | 90% to 100% | Great condition. Battery runtime feels like new. Normal for laptops in their first year. |
| **10% to 20%** | 80% to 90% | Normal aging. Expected after one to two years of regular mobile use. |
| **20% to 30%** | 70% to 80% | Noticeably shorter runtime. You will need a charger sooner during work sessions. |
| **30% and higher** | Below 70% | Substantial wear. Plan a replacement if you regularly work away from outlets. |

Treat these bands as rules of thumb. If your laptop stays plugged in at a desk, 30% wear may never get in your way.

On a new battery, health can read slightly above 100% because cell manufacturing tolerances allow some packs to exceed rated design capacity slightly. Readings can also shift by two or three percent between checks because health is an estimate from the battery's controller based on voltage and temperature. The battery does not truly recover lost capacity; chemical degradation in lithium-ion cells is permanent.

## Which habits slow down battery wear?

Modern laptops run on lithium-ion cells. You can slow down wear by avoiding conditions that stress cell chemistry:

1. **Avoid heat**: Heat is the biggest enemy of battery lifespan. High temperatures accelerate the chemical reactions that break down battery cells. Never leave your laptop in a hot car, and avoid using it on beds or blankets that choke intake vents. If your laptop runs hot, check [what causes laptop overheating](/guides/laptop-overheating-causes/).
2. **Limit time spent at 100% charge**: Long periods at 100% charge add wear, especially while the chassis is warm. Many laptops have a charge-limit option (often around 80%) in the maker's app. For example, Lenovo Vantage has Conservation Mode, MyASUS has Battery Health Charging, Dell's power app offers a custom charge limit, and many HP laptops have Battery Health Manager in their BIOS settings. Options differ by model, but if your laptop stays plugged in most of the day, an 80% limit is worth turning on.
3. **Avoid regular full discharges**: Lithium-ion batteries do not have a memory effect and do not need full discharges. Deep drains to 0% put more strain on cells than shallow cycles that recharge at 20% or 30%.
4. **Watch your discharge rate**: If your battery drains quickly, check your power draw in watts with our guide on [how to check laptop power draw in watts](/guides/check-laptop-power-draw-watts/).

## Why does Windows 11 Settings omit battery health?

Windows 11 Settings > System > Power & battery shows charge level and battery usage per app, but not battery health.

Microsoft hasn't said why. Windows does track design and full charge capacity, though: the numbers are exposed to the `powercfg` battery report and to the system interfaces that monitoring apps such as Taskvane read. Some laptop makers' own apps also show a health figure.

## What other tools can check laptop battery health?

Several established tools also read battery health on Windows 11:

- **BatteryInfoView**: A lightweight utility from NirSoft that displays detailed battery firmware events and logs charge rate changes without installation.
- **HWiNFO**: A deep hardware diagnostics tool that reports battery wear alongside motherboard sensor rails, voltages, and thermal probes.

Both go deeper than Taskvane on battery diagnostics. Taskvane's angle is showing health, wear and live watts next to the rest of your system, in one window.
