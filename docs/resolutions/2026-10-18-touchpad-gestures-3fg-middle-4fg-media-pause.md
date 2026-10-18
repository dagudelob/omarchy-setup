# Touchpad gestures: 3-finger middle click and 4-finger media play/pause

- **Date:** 2026-10-18
- **Branch:** `feature/touchpad-gestures-3fg-middle-4fg-media-pause`
- **Type:** `feature`

---

## 1. Issue / Requirement
Configure touchpad tap gestures on Surface Pro Type Cover under Omarchy Linux (Hyprland):
- 3-finger tap: Native middle mouse button click (`BTN_MIDDLE`) with zero latency.
- 4-finger tap: Instant media play/pause toggle matching physical headphone click response.

## 2. Root Cause
- 3-finger tap was intercepted by `drag_3fg = 1` in Hyprland's input settings, preventing libinput from emitting native middle clicks.
- 4-finger tap had latency and detection issues in the custom daemon because multi-touch finger spread (`ABS_MT_POSITION_X/Y`) was mistakenly measured instead of device centroid motion, causing tap distance checks to fail.

## 3. Applied Solution
1. **Hyprland Input (`input.lua`):**
   - Configured `drag_3fg = 0` to release 3-finger tap to libinput.
   - Set `tap_button_map = "lrm"` (1-finger Left, 2-finger Right, 3-finger Middle) and `tap_to_click = true`.
2. **Gesture Daemon (`surface-touchpad-gestures.py`):**
   - Stripped out 3-finger interception so libinput handles native 3-finger middle click directly.
   - Refined `QuadtapWatcher` to track only centroid movement (`ABS_X`/`ABS_Y`) for `BTN_TOOL_QUADTAP` (code 335).
   - Trigger media `PlayPause` via direct DBus MPRIS invocation (`busctl --user call ... Player PlayPause`), falling back to `omarchy-shell media playPause`.
3. **Service Management:**
   - Reloaded Hyprland config (`hyprctl reload`) and restarted `surface-touchpad-gestures.service`.

## 4. Modified Files
- `/home/dagudelo/.config/hypr/input.lua`
- `/home/dagudelo/.config/omarchy/scripts/surface-touchpad-gestures.py`
- `config/hypr/input.lua`
- `config/omarchy/scripts/surface-touchpad-gestures.py`
- `docs/resolutions/2026-10-18-touchpad-gestures-3fg-middle-4fg-media-pause.md`

## 5. Validation
- Verified with `hyprctl reload` and `hyprctl configerrors` (clean output).
- Verified `surface-touchpad-gestures.service` status (active running).
- Verified 3-finger tap opens links in new tabs / closes tabs (middle click).
- Verified 4-finger tap toggles playback on active media player instantly.
