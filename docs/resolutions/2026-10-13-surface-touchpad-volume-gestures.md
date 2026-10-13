# Surface Touchpad Gestures for Volume Control and Workspaces

- **Date:** 2026-10-13
- **Branch:** `feature/surface-touchpad-volume-gestures`
- **Type:** `feature`

---

## 1. Issue / Requirement
Enable a smooth, responsive multitouch gesture experience on the Microsoft Surface Type Cover touchpad under Hyprland/Omarchy matching Windows Precision Touchpad / macOS:
- Continuous, 1:1 proportional volume control following 4-finger vertical displacement (smooth volume adjustments with gentle inertia), rather than discrete static steps.
- Native 4-finger horizontal workspace switching.

## 2. Root Cause
Hyprland by default only handles static gesture threshold triggers (a single action triggered upon completing a swipe). To adjust volume smoothly in direct proportion to real-time finger travel distance, continuous `GESTURE_SWIPE_UPDATE` events from libinput must be processed at system level.

## 3. Applied Solution
1. **Permissions and Input Utilities:**
   - Added user to system `input` group for reading touchpad device events.
   - Installed `libinput-tools` via `omarchy pkg add`.
2. **Continuous Multitouch Gesture Daemon:**
   - Implemented `~/.config/omarchy/scripts/surface-touchpad-gestures.py` listening to `libinput debug-events` in real time.
   - Translated continuous delta vertical displacement (`dy`) directly into proportional volume percentage changes with smooth physical damping.
3. **Persistent Service:**
   - Created and enabled systemd user service `~/.config/systemd/user/surface-touchpad-gestures.service`.
4. **Hyprland Integration:**
   - In `~/.config/hypr/input.lua`, retained native horizontal workspace gestures (`hl.gesture({ fingers = 4, direction = "horizontal", action = "workspace" })`), leaving the vertical axis dedicated to continuous volume control.

## 4. Modified Files
- `/home/dagudelo/.config/hypr/input.lua`
- `/home/dagudelo/.config/omarchy/scripts/surface-touchpad-gestures.py`
- `/home/dagudelo/.config/systemd/user/surface-touchpad-gestures.service`

## 5. Validation
- Verified `surface-touchpad-gestures.service` status is active and running (`active (running)`).
- Hyprland syntax validated with `hyprctl reload` returning `ok`.
- Physical gesture tested and confirmed: 4-finger vertical swipe smoothly and accurately modulates volume.
