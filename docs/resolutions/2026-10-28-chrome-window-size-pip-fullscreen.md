# Google Chrome Window Size PiP Rule Diagnosis

- **Date:** 2026-10-28
- **Branch:** `fix/chrome-window-size-pip-fullscreen`
- **Type:** `fix`

---

## 1. Issue / Requirement
Google Chrome opened in a small floating window (600x338) and the standard fullscreen/maximize shortcuts (`Super + F`, `Super + Alt + F`) did not expand the window. The user requested opening Chrome maximized and clarifying the behavior of `Super + Shift + Enter`.

## 2. Root Cause
In `/usr/share/omarchy/default/hypr/apps/pip.lua`, an automatic picture-in-picture rule matches any window with tag `chromium-based-browser` and title matching `^Meet - .+`. Because Chrome was on a Google Meet meeting, Hyprland automatically forced it into a floating, pinned overlay with fixed size `600x338`, which ignores standard tiled maximize/fullscreen shortcuts.

## 3. Applied Solution
1. Inspected active Hyprland window properties and client rules using `hyprctl clients` and `hyprctl binds`.
2. Confirmed `Super + Shift + Enter` is natively mapped in Omarchy to launch the default browser (`google-chrome`).
3. Diagnosed that toggling floating state (`Super + T`) restores the window to tiling layout, and identified how custom overrides in `~/.config/hypr/` can bypass the default Meet PiP floating rule if desired.

## 4. Modified Files
- `/home/dagudelo/Code/omarchy-setup/docs/resolutions/2026-10-28-chrome-window-size-pip-fullscreen.md`

## 5. Validation
- Verified client state with `hyprctl clients` showing the 600x338 float and pin properties caused by `pip.lua`.
- Verified keybindings via `omarchy menu keybindings --print` confirming `Super + Shift + Return` triggers default browser.
- Successfully unpinned/tiled active windows and verified fullscreen dispatch via `hl.dsp.window.fullscreen`.
