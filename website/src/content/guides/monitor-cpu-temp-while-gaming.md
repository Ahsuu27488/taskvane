---
title: How to watch CPU temperature while gaming (overlay options compared)
seoTitle: How to watch CPU temp while gaming (overlay options compared)
description: Compare overlay options for watching CPU temperature while gaming on Windows, including MSI Afterburner, driver tools, and Taskvane's always-on-top mini widget.
targetQuery: how to display CPU temp while gaming
published: 2026-11-02
updated: 2026-11-02
promise: In-game overlays versus always-on-top widgets, how to set them up, and what mid-game temperatures mean.
related:
  - normal-cpu-temperature
  - check-gpu-temperature-windows-11
  - laptop-overheating-causes
compare: hwinfo
faq:
  - q: Why doesn't Xbox Game Bar show CPU temperature?
    a: Game Bar's Performance widget shows usage figures that Windows itself tracks, such as CPU, GPU and RAM usage. Windows has no standard way for apps to read the CPU's temperature sensor, so tools that show it, including Taskvane, use their own driver to read it.
  - q: Does an in-game overlay lower frame rates?
    a: Modern overlays like RTSS and GPU driver companion apps use very few system resources and typically have no noticeable effect on frame rates. The impact is negligible on modern hardware and only becomes a minor consideration on heavily CPU-limited systems.
  - q: Why does the Taskvane mini widget disappear in fullscreen games?
    a: The mini widget is an always-on-top desktop window rather than an in-game hook. When a game runs in exclusive fullscreen mode, the game takes over the display and other windows are not drawn on top of it. Switching the game to borderless windowed mode keeps the widget visible.
  - q: Can in-game overlays trigger game bans?
    a: Overlays such as RTSS and the GPU makers' own overlays are widely used, but some multiplayer games with anti-cheat block or flag third-party software that hooks into the game. Check the game's rules if you are unsure. An always-on-top window like Taskvane's mini widget doesn't hook into the game at all.
---

To display your CPU temperature while gaming on Windows, you have two practical paths: an in-game overlay or an always-on-top desktop widget. A true in-game overlay injects into your graphics renderer and draws numbers directly onto game frames, which works even in exclusive fullscreen mode. Popular options include MSI Afterburner with RivaTuner Statistics Server (RTSS), HWiNFO connected to RTSS, and GPU driver overlays from NVIDIA and AMD. The built-in Windows Xbox Game Bar shows frame rates and hardware usage, but cannot show CPU temperature. Alternatively, Taskvane provides an always-on-top mini widget that displays live CPU and GPU temperatures alongside power draw in watts. Because the mini widget is a desktop window rather than an in-game hook, it requires running your game in borderless windowed mode or placing the widget on a second monitor.

## What is the difference between an in-game overlay and an always-on-top window?

The difference comes down to how Windows renders graphics:

- **In-game overlay**: An overlay is drawn by the game's own renderer. It injects into the graphics pipeline (DirectX, Vulkan, or OpenGL) and draws text directly onto game frames. Because the game engine renders the metrics, an overlay stays visible in exclusive fullscreen mode.
- **Always-on-top window**: A separate desktop window that sits above other windows. It does not touch game memory or the renderer. In exclusive fullscreen the game takes over the display, so an always-on-top window is hidden while the game has focus.

To keep an always-on-top window visible while playing, switch the game to borderless (often called "borderless windowed" or "fullscreen windowed") mode. Borderless mode fills the screen but is still a normal window, so the widget can sit on top of it. With two monitors, you can also put the widget on the second one.

## What tools can display your CPU temperature while gaming?

Five common tools can display your hardware stats while playing games on Windows.

### Xbox Game Bar

Pressing `Windows + G` opens the built-in Xbox Game Bar. Its Performance widget shows CPU, GPU, VRAM and RAM usage and FPS, and can be pinned so it stays on screen. It does not show CPU temperature.

- **Where it wins**: Built into Windows 10 and 11 with zero setup; opens with one shortcut.

### MSI Afterburner with RivaTuner Statistics Server

MSI Afterburner is free and works with most graphics cards, not only MSI's. It comes with RivaTuner Statistics Server (RTSS), which draws the on-screen display. It can show GPU temperature, usage, FPS and frame time, and CPU temperature on many systems. Setup means ticking "Show in On-Screen Display" for each reading in Afterburner's monitoring settings.

- **Limits**: The interface takes time to configure, and some anti-cheat systems block third-party hooks. Check the game's rules if the overlay fails to appear.
- **Where it wins**: The standard for deep in-game overlays and frame time graphs in exclusive fullscreen games.

### HWiNFO with RivaTuner Statistics Server

HWiNFO reads far more sensors than most tools, including per-core temperatures, voltages and clock speeds. It can send any of them to RTSS for the same kind of overlay.

- **Limits**: Two programs to install and set up, and a long list of sensors to choose from.
- **Where it wins**: Unmatched sensor depth. Compare features in [Taskvane vs HWiNFO](/compare/hwinfo/).

### GPU driver overlays (NVIDIA and AMD)

NVIDIA (the NVIDIA app) and AMD (AMD Software: Adrenalin Edition) have built-in performance overlays with FPS and GPU readings.

- **Limits**: They focus on GPU readings, and each works only with that maker's graphics cards.
- **Where it wins**: Comes from your graphics card maker, so there is no extra tool to trust, and turning it on takes a shortcut or a toggle.

### Taskvane mini widget

Taskvane's mini widget sits on your desktop instead of hooking into game code. It shows CPU usage and temperature, RAM usage, GPU usage and temperature, power draw in watts, and battery charge percentage.

- **Limits**: It is not an overlay: it does not show FPS or frame times, and exclusive fullscreen games hide it.
- **Where it wins**: One click to open, shows power draw in watts and battery charge, and never hooks into the game.

Overlays cost very little performance, usually not noticeable. Frame rates are a bigger concern only on very weak PCs. Some games with anti-cheat may block or flag third-party overlays, so check the game's rules before using hooking tools.

## How do you set up the Taskvane mini widget?

Taskvane is a free, open-source (GPL-3.0) Task Manager alternative for Windows 11 and 10. Its mini widget is a small always-on-top window that opens in the bottom-right corner of the screen. You can drag it by its top bar, and it remembers where you left it. The top bar also has a button that opens the main Taskvane window and a close (✕) button. Opening the widget doesn't take focus away from the window you're in.

Rows update every second, each with a small bar:

- **CPU**: usage percentage and temperature.
- **RAM**: memory usage percentage.
- **GPU**: usage percentage and temperature of the dedicated GPU (or the only GPU).
- **PWR**: power draw in watts (whole-system draw on battery; CPU and GPU power when plugged in).
- **BAT**: battery charge percentage, with a charging symbol when plugged in.

Rows without data are left out (no BAT row on a desktop, no PWR row when there is no power reading), and the widget resizes to fit. Temperatures follow your °C or °F setting. CPU power when plugged in needs administrator mode.

To set up the widget and turn on CPU temperature:

1. Open Taskvane.
2. Turn on CPU sensors if needed. CPU temperature requires administrator mode plus the free PawnIO driver, which users install from `https://pawnio.eu/` (the **Enable CPU sensors** button opens it, then Taskvane offers **Restart as administrator**). For details, follow [how to check CPU temperature on Windows 11](/guides/check-cpu-temperature-windows-11/).
3. Click **Mini widget** at the bottom of the sidebar or right-click the tray icon and select **Mini widget**.
4. Drag the widget to a screen corner or to a second monitor.
5. In your game's video settings, set display mode to Borderless Windowed (or Fullscreen Windowed).

Without administrator mode Taskvane still shows all usage numbers, the process list, GPU temperatures, battery power draw and battery health. Only CPU temperature, CPU power and drive temperatures need administrator mode.

## What CPU temperatures should you expect mid-game?

When checking CPU temperature while gaming, a short spike is fine, but sustained readings matter. Modern processors boost clock speeds aggressively for short bursts like loading a map, causing brief temperature jumps that drop once the burst finishes. Sustained heat during active gameplay is what tests your cooler.

Taskvane labels temperatures using four bands:

| Band | Temperature | What it means while gaming |
| :--- | :--- | :--- |
| **Normal** | Below 70 °C | Good cooling headroom. Typical for lightweight games or roomy desktop cases. |
| **Warm** | 70 to 84 °C | Standard operating range under gaming load. Cooling fans ramp up audibly. |
| **Hot** | 85 to 94 °C | Heavy thermal load. Common in compact laptops; indicates cooling is near capacity on desktops. |
| **Critical** | 95 °C and up | At the thermal limit. The processor will throttle clock speeds to protect hardware. |

For where these limits come from, read [what is a normal CPU temperature](/guides/normal-cpu-temperature/). For graphics card operating ranges, see [how to check GPU temperature on Windows 11](/guides/check-gpu-temperature-windows-11/).

You do not have to watch the widget continuously while playing. Taskvane alerts (Settings > Alerts, one switch for all, on by default) send a Windows notification if limits are crossed:

- CPU temperature above 90 °C (needs administrator mode)
- GPU temperature above 85 °C
- Sustained CPU usage above 95% averaged over 1 minute (names the top process)
- Memory usage above 90%
- Battery below 15% (on battery)

Each threshold can be changed. The same alert repeats at most once every 10 minutes. Closing the window keeps Taskvane running in the notification area by default, so alerts keep working.

To look back at a session afterwards, Taskvane keeps the last hour. The **Performance** page graphs CPU and GPU usage and GPU temperature, and **Settings > Data & access > Export CSV…** saves the last hour, including CPU temperature, to a file. See [how to log CPU temperature over time](/guides/log-cpu-temperature-over-time/).

<img class="shot" src="/img/performance-1600.webp" srcset="/img/performance-800.webp 800w, /img/performance-1600.webp 1600w" sizes="(max-width: 900px) 100vw, 760px" width="1600" height="936" alt="Taskvane Performance page with the CPU usage graph, CPU temperature and package power, and a device list for memory, two GPUs, disk, network and power" loading="lazy" decoding="async" />

## Can you show CPU temperature in the notification area instead?

If you prefer no floating windows or overlays on your screen, Taskvane offers another low-effort option: putting temperature on the Windows tray icon.

In **Settings**, find **Notification-area icon shows**. You can set the tray icon to show:

- CPU usage
- CPU temperature
- GPU temperature
- Power draw
- Memory usage

Set to CPU temperature, the icon shows the current number, and its color changes as the temperature rises. Games usually cover the taskbar, so this suits a quick check between matches or a game running in a window.
