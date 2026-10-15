# Fix Volume OSD Window for Surface Touchpad 4-Finger Gestures

- **Date:** 2026-10-15
- **Branch:** `fix/surface-touchpad-volume-osd`
- **Type:** `fix`

---

## 1. Issue / Requirement
The 4-finger vertical swipe gesture on Microsoft Surface Type Cover properly modulated the system volume, but the on-screen display (OSD) overlay window indicating volume percentage stopped appearing. The requirement was to restore the visual OSD window while strictly maintaining the zero-latency, ultra-smooth 1:1 proportional volume behavior.

## 2. Root Cause
The daemon managing gestures (`surface-touchpad-gestures.service`) was running under systemd user manager without `OMARCHY_PATH=/usr/share/omarchy` in its environment. When `surface-touchpad-gestures.py` invoked `omarchy-osd`, it delegated to `omarchy-shell -q osd show`. Because `OMARCHY_PATH` was missing, `omarchy-shell` silently exited with code 0 due to quiet mode (`-q`), aborting Quickshell IPC communication. Furthermore, calling Quickshell OSD synchronously in the same loop would add ~50ms latency per step, which would throttle direct audio responsiveness.

## 3. Applied Solution
1. **Asynchronous Decoupled OSD Worker:**
   - Implemented `OsdWorker` in `~/.config/omarchy/scripts/surface-touchpad-gestures.py` as an independent background thread.
   - Kept audio sink modulation (`pactl set-sink-volume`) in `VolumeWorker` running at ~1ms execution speed (60+ FPS real-time tracking), passing updates asynchronously to `OsdWorker`.
   - `OsdWorker` throttles Quickshell IPC updates cleanly to prevent compositor saturation while ensuring the exact final volume is shown upon gesture completion (`on_end`).
2. **Environment & Wayland Display Resilience:**
   - Added `ensure_environment()` and `resolve_wayland_display()` in `surface-touchpad-gestures.py` to auto-detect active `wayland-*` sockets in `XDG_RUNTIME_DIR` and set fallback paths.
   - Added `Environment=OMARCHY_PATH=/usr/share/omarchy` and expanded `PATH` in `~/.config/systemd/user/surface-touchpad-gestures.service`.
3. **Daemon Reload:**
   - Executed `systemctl --user daemon-reload` and restarted `surface-touchpad-gestures.service`.

## 4. Modified Files
- `/home/dagudelo/.config/omarchy/scripts/surface-touchpad-gestures.py`
- `/home/dagudelo/.config/systemd/user/surface-touchpad-gestures.service`
- `/home/dagudelo/Code/omarchy-setup/config/omarchy/scripts/surface-touchpad-gestures.py`
- `/home/dagudelo/Code/omarchy-setup/config/systemd/user/surface-touchpad-gestures.service`
- `/home/dagudelo/Code/omarchy-setup/docs/resolutions/2026-10-15-surface-touchpad-volume-osd.md`

## 5. Validation
- Verified service running cleanly with `systemctl --user status surface-touchpad-gestures.service` (`active (running)`).
- Inspected PID environment via `/proc/<PID>/environ` confirming `OMARCHY_PATH=/usr/share/omarchy` and `WAYLAND_DISPLAY=wayland-1`.
- Verified Quickshell OSD IPC call returns `ok`.
- Confirmed with user that 4-finger vertical swipe smoothly updates volume and visual overlay renders as expected.
