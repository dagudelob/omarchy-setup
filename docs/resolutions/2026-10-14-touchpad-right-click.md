# Fix Touchpad Right-Click Corner Recognition in Hyprland

- **Date:** 2026-10-14
- **Branch:** `fix/touchpad-right-click`
- **Type:** `fix`

---

## 1. Issue / Requirement
The touchpad was not recognizing right-clicks when pressing down on the right side / lower-right corner of the touchpad under Hyprland in Omarchy.

## 2. Root Cause
`clickfinger_behavior` was set to `true` in Hyprland's input touchpad configuration (`~/.config/hypr/input.lua`). When enabled, libinput disables physical software button areas (bottom-right / bottom-left) and only triggers a right-click via a two-finger click/tap.

## 3. Applied Solution
1. Backed up `~/.config/hypr/input.lua`.
2. Changed `clickfinger_behavior = true` to `clickfinger_behavior = false` under `input.touchpad` in `~/.config/hypr/input.lua` to enable standard software button areas (bottom-right corner click).
3. Reloaded Hyprland configuration via `hyprctl reload` and verified configuration syntax using `hyprctl configerrors`.
4. Synced configuration file to the repository (`config/hypr/input.lua`).

## 4. Modified Files
- `/home/dagudelo/.config/hypr/input.lua`
- `/home/dagudelo/Code/omarchy-setup/config/hypr/input.lua`

## 5. Validation
- `hyprctl reload` executed with return code 0.
- `hyprctl configerrors` returned `ok` with zero syntax or runtime configuration errors.
- Verified physical lower-right corner press now registers as right-click.
