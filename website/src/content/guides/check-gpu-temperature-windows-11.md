---
title: How to check GPU temperature on Windows 11
seoTitle: How to check GPU temperature on Windows 11 (and hot spot)
description: Windows 11 can show GPU temperature in Task Manager for dedicated graphics cards. Here is how to find it, why it goes missing, and how to check your hot spot.
targetQuery: how to check GPU temperature Windows 11
published: 2026-10-22
updated: 2026-10-22
promise: How to find it in Task Manager, why it might be missing, and what core and hot spot readings mean.
related:
  - check-cpu-temperature-windows-11
  - normal-cpu-temperature
compare: hwinfo
faq:
  - q: Does Windows 11 Task Manager show GPU temperature?
    a: Yes, but only for dedicated graphics cards with a compatible WDDM 2.4 or newer driver. Task Manager does not show GPU temperature for most integrated graphics chips, and it never shows GPU hot spot or memory junction temperatures.
  - q: Why is GPU temperature missing in Task Manager?
    a: Task Manager omits the temperature line if your PC uses integrated graphics, if your graphics driver is outdated, or if the driver does not support WDDM 2.4 or higher. On laptops with switchable graphics, the reading can also disappear when the dedicated GPU is asleep.
  - q: What is a normal GPU temperature while gaming?
    a: Under gaming load, normal GPU core temperatures typically range between 65 °C and 85 °C. The hot spot temperature usually reads 10 to 20 °C higher, between 75 °C and 100 °C. Readings above 95 °C on the core or 105 °C on the hot spot mean cooling needs attention.
  - q: What is the difference between GPU core and hot spot temperature?
    a: The GPU core temperature is the card's main temperature reading, the one Task Manager shows. The hot spot is the highest reading among the many sensors spread across the GPU die, so it is usually 10 to 20 °C higher than the core.
---

Windows 11 can show your GPU temperature directly in Task Manager, but only for dedicated graphics cards with a modern driver. Task Manager never shows the GPU hot spot, and it omits temperatures entirely for most integrated graphics chips. To check your hot spot or monitor temperatures while gaming, you need a hardware monitor.

To check your GPU temperature on Windows 11, you have three practical paths:

1. Check the Performance tab in Windows Task Manager if your PC has a supported dedicated graphics card.
2. Use Taskvane to see GPU core and hot-spot temperatures side by side without administrator rights.
3. Use diagnostic tools such as HWiNFO if you need memory junction temperatures on GDDR6X cards.

Here is how each option works, why Task Manager hides the reading on many PCs, and what your numbers mean under load.

## How do you find GPU temperature in Windows Task Manager?

If your computer has a dedicated graphics card from NVIDIA, AMD, or Intel, Windows 11 can display its core temperature without installing third-party software.

To find it in Task Manager:

1. Press `Ctrl + Shift + Esc` to open Task Manager.
2. Select the **Performance** tab on the left sidebar.
3. Click your dedicated graphics card in the left list, usually named **GPU** or **GPU 1**.
4. Look below the graphs on the right side for the **GPU Temperature** line.
5. The readout shows the current reading in degrees Celsius, such as 48 °C.

Task Manager is convenient because it is built into Windows. However, it shows only a single value for the whole chip, updates once per second, and keeps no history beyond 60 seconds. It also leaves out the hot spot and does not alert you when temperatures climb.

## Why is GPU temperature missing in Task Manager?

If the GPU Temperature line is missing from Task Manager, your PC usually falls into one of these categories:

- **Integrated graphics chips**: Laptops and desktops running on integrated graphics (such as Intel UHD or AMD Radeon graphics built into the CPU) do not report temperature to Task Manager. In practice the line appears for dedicated cards and is missing on most integrated graphics.
- **Older graphics drivers**: Windows 11 and Windows 10 (version 2004 or later) require a driver supporting Windows Display Driver Model (WDDM) 2.4 or newer. If you are using a generic display driver or an outdated release, Task Manager cannot query the sensor.
- **Dedicated laptop GPUs in sleep mode**: On laptops with switchable graphics, the dedicated GPU powers down when idle to save battery. In this sleep state, Task Manager may show 0 °C or omit the temperature line until a 3D app wakes the card.

## What is the difference between GPU core and hot spot temperature?

When monitoring a graphics card, two distinct measurements matter:

The **GPU core temperature** is the reading shown in Task Manager and basic tools. It reflects an average value across sensors on the die, or a sensor near the edge of the chip. It gives a good general picture of the graphics processor under load.

The **GPU hot spot temperature** (also called junction temperature) is the highest reading among an array of thermal diodes across the GPU die. Workloads hit certain execution units harder than others, so heat concentrates unevenly. The hot spot reports the single hottest point on the silicon die at that moment.

Under gaming load, the hot spot usually reads 10 to 20 °C above the core. For example, a core temperature of 72 °C with an 85 °C hot spot is normal. However, a gap well beyond 25 to 30 °C points to poor cooler contact, uneven mounting pressure, or dried thermal paste.

AMD has stated that hot-spot (junction) temperatures up to 110 °C are within spec for its Radeon cards. When GPUs reach their thermal limit, they lower their clock speeds to protect themselves.

On cards with GDDR6X memory, a **memory junction temperature** also exists. Taskvane does not show it, so tools like [HWiNFO](/compare/hwinfo/) are needed if you want to track video memory heat.

## How do you check GPU core and hot spot with Taskvane?

Taskvane is a free, open-source (GPL-3.0) Task Manager alternative for Windows 11 and 10. Your graphics driver already reports the GPU's temperature to apps, so unlike CPU temperature, Taskvane shows it right away, without administrator mode or an extra driver.

To check your GPU temperatures in Taskvane:

1. Download and open Taskvane.
2. The **Overview** page has a GPU tile with the current load, video memory use and temperature.

<img class="shot" src="/img/overview-1600.webp" srcset="/img/overview-800.webp 800w, /img/overview-1600.webp 1600w" sizes="(max-width: 900px) 100vw, 760px" width="1600" height="936" alt="Taskvane Overview page showing the GPU tile with load and temperature" loading="lazy" decoding="async" />

3. Open the **Sensors** page from the sidebar to view both GPU core and hot-spot temperatures side by side.
4. Each entry shows the current reading, the minimum and maximum since Taskvane started, and a status label. The labels use the same bands as CPU temperatures (Hot from 85 °C, Critical from 95 °C), so a hot spot of 95 to 105 °C on a Radeon card shows as Critical even though AMD rates it as within spec. Read the hot spot against the core, as explained above, rather than by its label alone.

<img class="shot" src="/img/sensors-1600.webp" srcset="/img/sensors-800.webp 800w, /img/sensors-1600.webp 1600w" sizes="(max-width: 900px) 100vw, 760px" width="1600" height="936" alt="Taskvane Sensors page listing GPU core and hot-spot temperatures with status labels" loading="lazy" decoding="async" />

Two more things help while gaming. The **Mini widget** button opens an always-on-top panel with CPU and GPU load, temperatures and watts, which you can keep beside a windowed or borderless game (it is not an in-game overlay). And a GPU temperature alert is on by default at 85 °C; change it in **Settings > Alerts**.

## What other tools can check GPU temperature?

Several other free tools can monitor graphics temperatures on Windows:

- **HWiNFO**: Deep hardware telemetry with memory junction temperatures and logging, though its dense sensor list takes time to learn. See [Taskvane vs HWiNFO](/compare/hwinfo/).
- **GPU-Z**: A compact tool dedicated to graphics cards that displays clock speeds and sensor graphs, but lacks process management.
- **MSI Afterburner**: Popular for in-game overlays during fullscreen play (through the bundled RivaTuner Statistics Server), plus fan and clock tuning.
- **NVIDIA App and AMD Software**: The driver companions can show GPU temperature in their own performance overlays, for their own cards only.

## What is a normal GPU temperature while gaming?

GPU core temperature under gaming load is commonly 65 to 85 °C. How hot your card runs depends on the game, case ventilation, and whether you use a desktop or a laptop.

| Operating state | GPU core | GPU hot spot | What is happening |
| :--- | :--- | :--- | :--- |
| **Idle and desktop use** | 35 °C to 50 °C | 40 °C to 55 °C | Fans on modern cards often stop completely below 50 to 55 °C to stay silent. |
| **Moderate gaming** | 65 °C to 74 °C | 75 °C to 88 °C | Common in esports titles or roomy cases. Fans spin quietly. |
| **Demanding gaming** | 75 °C to 84 °C | 88 °C to 98 °C | Heavy 3D load or gaming laptops. Fans ramp up audibly to shed heat. |
| **Heavy thermal load** | 85 °C to 94 °C | 99 °C to 108 °C | Sustained load near cooling limits. Check for dust or poor case airflow. |
| **Thermal throttling** | 95 °C and up | 110 °C and up | The GPU drops its clock speeds to protect its silicon from heat damage. |

Desktop cards with large coolers often stay below 75 °C while gaming. Laptops pack high-wattage chips into thin chassis, so temperatures between 80 °C and 85 °C under sustained gaming are typical and expected.

## What should you do if your GPU runs too hot?

If your graphics card consistently runs in the Hot or Critical range, these steps help reduce temperatures:

1. **Clear dust from the cooler**: Dust collects between heatsink fins and blocks airflow. Use compressed air to clean your graphics card fans, heatsink fins, and case intake filters.
2. **Elevate laptops off soft surfaces**: Never run games on a laptop placed on a bed or carpet. Soft surfaces block intake vents. Use a flat desk or a stand that elevates the base. For more on cooling paths, read [laptop overheating causes](/guides/laptop-overheating-causes/).
3. **Close what you aren't using**: a second game launcher, a browser playing video or a recording tool running in the background all add GPU load. Task Manager's Processes tab has a GPU column for checking which app it is.
4. **Cap your frame rate**: If your GPU renders 200 frames per second on a 144 Hz screen, it wastes power. Capping the frame rate in the game's settings (or the driver panel) lowers power draw, and with it temperature and fan noise.
5. **Check the hot-spot gap and repaste older cards**: If your core is 70 °C but the hot spot exceeds 100 °C, the 30 °C gap indicates uneven cooler contact. On cards several years old, applying fresh thermal paste can restore cooling performance.

To check how the rest of your system is handling heat, see [how to check CPU temperature on Windows 11](/guides/check-cpu-temperature-windows-11/) and [what is a normal CPU temperature](/guides/normal-cpu-temperature/).
