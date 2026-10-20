---
title: How to disable startup apps on Windows 11 (and speed up sign-in)
seoTitle: How to disable startup apps on Windows 11 (and speed up sign-in)
description: Learn how to disable startup apps on Windows 11 using Settings, Task Manager, or Taskvane. Find out which programs are safe to turn off and speed up sign-in.
targetQuery: how to disable startup apps Windows 11
published: 2026-10-30
updated: 2026-10-30
promise: Three ways to stop startup programs, what is safe to turn off, and how to verify the results.
related:
  - laptop-overheating-causes
  - task-manager-alternatives-windows-11
compare: task-manager
faq:
  - q: Does disabling a startup app uninstall it from your PC?
    a: No. Disabling a startup app only stops Windows from launching it automatically at sign-in. The software remains installed on your drive, and you can open and use it manually whenever you want.
  - q: Why is there an entry named Program with no publisher in Task Manager?
    a: An entry named Program usually points to a file that was uninstalled or removed while leaving an orphaned startup entry behind, or to an app whose file properties lack a product name. It is harmless to disable.
  - q: Will turning off startup apps improve in-game frame rates?
    a: Disabling startup apps rarely improves in-game FPS directly unless one of those applications was actively using CPU or GPU time in the background. The primary benefits are faster sign-in, lower idle RAM use, and fewer background processes.
  - q: Why does Taskvane need administrator rights to disable some startup apps?
    a: Startup items stored in machine-wide registry locations like HKLM or the all-users Startup folder apply to every account on the computer. Windows requires administrator permissions to modify settings that affect all users.
---

To disable startup apps on Windows 11, open **Settings > Apps > Startup** and switch off any apps you do not need. You can also press `Ctrl + Shift + Esc` to open Task Manager, select **Startup apps**, right-click an app, and select **Disable**. A third option is Taskvane, a free, open-source monitor whose **Startup apps** page displays the full command line and registry origin for each entry.

Disabling startup items prevents them from launching at sign-in. It does not uninstall software; you can still open any app manually. Turning off unneeded updaters, chat apps, and game launchers shortens the time to a responsive desktop while freeing memory and CPU cycles.

Here is how each method works, what is safe to turn off, and how to verify the results.

## How do you disable startup apps in Windows 11 Settings?

Windows Settings provides the simplest way to review and turn off startup programs:

1. Open **Settings** (`Windows + I`).
2. Go to **Apps > Startup**.
3. Review the list of apps registered to run at sign-in.
4. Toggle the switch next to any program to **Off**.

Use the **Sort by** dropdown to organize entries by **Name**, **Status**, or **Startup impact**.

Windows rates impact as **High impact**, **Medium impact**, **Low impact**, or **Not measured**, based on how much processor and disk time the app used during past sign-ins. A High impact app slows sign-in more than a Low impact one. Not measured usually means Windows hasn't timed that app yet.

Settings is quick, but it does not show the executable path or command line.

## How do you turn off startup apps in Task Manager?

Windows Task Manager provides more detail than Settings and is accessible on any Windows PC:

1. Press `Ctrl + Shift + Esc` to open Task Manager.
2. Select **Startup apps** from the left sidebar (called the **Startup** tab in older Windows versions).
3. Review the columns: **Name**, **Publisher**, **Status**, and **Startup impact**.
4. Select an app and click **Disable** in the command bar, or right-click the row and choose **Disable**.

The status updates immediately from **Enabled** to **Disabled**.

An entry named simply **Program** with no publisher usually points to a file that no longer exists after an uninstallation, or an executable lacking metadata in its file details. It is harmless to disable.

Task Manager needs no installation and also lists Microsoft Store apps that register their own startup entries. It hides the command each entry runs by default; right-click a column header and turn on **Command line** to see it. See our comparison in [Taskvane vs Task Manager](/compare/task-manager/).

## How do you manage startup apps in Taskvane?

[Taskvane](/download/) is a free, open-source (GPL-3.0) Task Manager alternative for 64-bit Windows 11 and Windows 10 (version 1809 or newer). It has no ads, needs no account, collects no telemetry, and uses about 0.4% CPU.

To manage startup programs in Taskvane:

1. Open Taskvane and select **Startup apps** from the sidebar.
2. The header shows how many items are active (such as "5 of 9 enabled") and has a **Refresh** button.
3. Each row displays the app's file description (or entry name), full command line, and an on/off switch.
4. Each entry includes a label for **This user** or **All users**, plus its source: **HKCU registry**, **HKLM registry**, or **Startup folder**.
5. Click any switch to toggle the entry on or off.

Taskvane lists apps that start from registry Run keys (user and machine-wide, including 32-bit entries) and Startup folders (user and all-users). It does not list services, scheduled tasks, or Microsoft Store apps' startup entries, so Task Manager's list can contain items Taskvane does not show.

Turning an app off in Taskvane works like Task Manager: the entry stays in place and Windows skips it at sign-in. Changes show in Task Manager and Settings, and either tool can undo them.

Machine-wide ("All users") entries require administrator rights. Without them, Taskvane displays "Machine-wide startup items need administrator rights." and leaves the switch unchanged.

Taskvane shows no startup impact rating, but displaying the full command line helps identify unfamiliar entries.

Taskvane itself only starts with Windows if you turn on **Launch when Windows starts** in its **Settings > General**, or tick that option in the installer (it starts unticked).

## Which startup apps are safe to disable?

Disabling a startup entry does not uninstall the app. It only stops it from launching automatically at sign-in. You can still open it manually whenever you want.

Usually safe to turn off:

- **Game launchers**: Steam, Epic Games Launcher and Battle.net keep running in the background and use memory while idle. Open them when you play.
- **Chat and music apps**: Discord, Spotify and Microsoft Teams add to sign-in time. Open them when you need them.
- **Software updaters**: Updaters for Adobe apps or peripherals sit in the background to check for updates; most apps also check when you open them.
- **Vendor helper apps**: Preinstalled manufacturer utilities you never open add background load.

Usually best to leave enabled:

- **Audio driver software**: Realtek Audio Console and sound utilities manage headphone jack detection and audio routing.
- **Laptop input utilities**: Touchpad gestures (Synaptics, Elan) and hotkey software support hardware controls.
- **Security software**: Keep the Windows Security notification icon and antivirus shields running from sign-in.
- **Cloud synchronization**: Leave OneDrive, Google Drive, or Dropbox on if you rely on continuous sync.

| Startup type | Examples | Recommendation | Reason |
| :--- | :--- | :--- | :--- |
| **Game launchers** | Steam, Epic Games Launcher | Safe to disable | Saves memory; open when gaming. |
| **Chat and music** | Discord, Spotify, Teams | Safe to disable | Reduces sign-in delay; open when needed. |
| **Updaters** | Adobe, peripheral updaters | Safe to disable | Less background work; most apps check for updates when opened. |
| **Vendor helpers** | OEM assistants, support tools | Safe to disable if unused | Removes background load. |
| **Audio utilities** | Realtek Audio, sound panels | Leave enabled | Maintains headphone sensing and audio switching. |
| **Touchpad and hotkeys** | Touchpad gestures, laptop hotkeys | Leave enabled | Powers multi-finger gestures and function keys. |
| **Security tools** | Windows Security, antivirus | Leave enabled | Provides protection from the moment you log in. |
| **Cloud storage** | OneDrive, Google Drive | Keep if needed | Syncs files continuously; disable if syncing manually. |

When unsure, look the entry up first. Check the full command in Taskvane, or right-click the process on Taskvane's **Processes** page and use **Open file location** or **Search online**.

## How do you undo a change and apply your settings?

Undoing a change is simple: return to Settings, Task Manager, or Taskvane and flip the switch back to **On** (or select **Enable** in Task Manager). The app will start automatically at your next sign-in.

Disabling an app does not close it if it is already running. The change only applies the next time Windows starts. To test the difference immediately, close the program manually (or end it from Taskvane's Processes page), then sign out or restart your PC.

## How do you tell if disabling startup apps helped?

Disabling startup apps mostly speeds up sign-in and frees memory and background CPU. It rarely changes in-game FPS unless one of those apps was busy in the background while you were playing.

You can check results with two measurements:

1. **Time from sign-in to a usable desktop**: Note how long it takes after you enter your PIN until you can open a browser without waiting. Compare a few sign-ins before and after.
2. **Memory in use after sign-in**: Wait about a minute after signing in for Windows to settle, then check memory usage. In Taskvane, look at the **Overview** page or go to **Performance > Memory**. Write the number down, make your changes, restart, and check again at the same point.

If your PC still runs hot or fans stay loud while idle, see [what causes laptop overheating](/guides/laptop-overheating-causes/) or check expected temperature ranges in [what is a normal CPU temperature](/guides/normal-cpu-temperature/).

## What startup items are not covered by standard tools?

Settings, Task Manager, and Taskvane manage standard user and machine startup programs. However, services, scheduled tasks, and drivers also start with Windows:

- **Windows Services**: Background system tasks that support networking, printing, and hardware management.
- **Scheduled Tasks**: Automated actions triggered at boot or set times in Windows Task Scheduler.
- **Kernel Drivers**: Low-level hardware drivers that initialize during boot.

Other tools handle these deeper components:

- **Microsoft Autoruns (Sysinternals)**: Shows every startup item, service, scheduled task, and driver on Windows. It is free, but turning those entries off is for experienced users because disabling a needed system driver can prevent Windows from booting.
- **Windows Task Manager**: Its **Services** tab lists Windows services and can start or stop them. Changing whether a service starts with Windows is done in the separate Services app (`services.msc`).

Taskvane doesn't list or change services, scheduled tasks or drivers.

If you want to manage apps, temperatures, and power draw in one place, download [Taskvane](/download/) or explore [Task Manager alternatives for Windows 11](/guides/task-manager-alternatives-windows-11/).
