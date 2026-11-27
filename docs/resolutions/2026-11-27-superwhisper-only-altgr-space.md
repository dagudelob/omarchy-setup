# Configure Superwhisper Only (Remove Voxtype) and Restrict Shortcut to AltGr + Space

- **Date:** 2026-11-27
- **Branch:** `feature/superwhisper-only-altgr-space`
- **Type:** `feature`

---

## 1. Issue / Requirement
Both **Superwhisper** and **Voxtype** were installed and running simultaneously on Omarchy (Surface Pro with Intel Core i7-7660U). The user wanted to standardize on **Superwhisper** in cloud mode (switching to local Offline Lite once the 10,000 monthly free words are used), completely remove **Voxtype**, and ensure dictation triggers **only** with **Right AltGr + Space** (`MOD5 + SPACE`) and **not** with **Left Alt + Space** (`ALT + SPACE`).

## 2. Root Cause
- Both `voxtype.service` and `superwhisper.service` were active in `systemd --user`.
- Omarchy's default `/usr/share/omarchy/default/hypr/bindings/dictation.lua` binds `ALT + SPACE` (Left Alt + Space) globally, and `~/.config/hypr/bindings.lua` previously only unbound `ALT + Alt_R` while keeping legacy bindings (`SUPER + CTRL + X`, `F9`).
- `~/.config/hypr/surface-pen.lua` still referenced `voxtype record toggle` for single-click dictation.

## 3. Applied Solution
1. **Removed Voxtype completely (freed 985.61 MiB):**
   ```bash
   systemctl --user disable --now voxtype.service
   systemctl --user daemon-reload
   rm -rf ~/.config/voxtype ~/.local/share/voxtype
   pkexec pacman -Rns --noconfirm voxtype-bin
   ```
2. **Restricted Hyprland dictation binding strictly to `AltGr + Space` (`MOD5 + SPACE`):**
   - Added `hl.unbind("ALT + SPACE")` alongside `hl.unbind("ALT + Alt_R")` in `~/.config/hypr/bindings.lua`.
   - Removed legacy `SUPER + CTRL + X` and `F9` bindings from `~/.config/hypr/bindings.lua`.
3. **Cleared Superwhisper's `Ctrl+Alt+Space` toggle shortcut:**
   ```bash
   superwhisper shortcuts set toggle ""
   superwhisper shortcuts apply
   ```
4. **Updated Surface Pen single-click shortcut:**
   - Replaced `voxtype record toggle` with `omarchy-dictation toggle` in `~/.config/hypr/surface-pen.lua`.
5. **Verified Superwhisper cloud mode:**
   - Confirmed `"processing": "cloud"` (0/10,000 words used) and documented switching to `Offline Lite` (Parakeet TDT 0.6B v3, ~822 MB) when credits run out.

## 4. Modified Files
- `/home/dagudelo/.config/hypr/bindings.lua`
- `/home/dagudelo/.config/hypr/surface-pen.lua`
- `/home/dagudelo/.config/superwhisper/preferences.json` (via `superwhisper shortcuts set/apply`)

## 5. Validation
- `which voxtype` returns not found; `omarchy-default-dictation` returns `superwhisper`; `systemctl --user is-active superwhisper.service` returns `active`.
- `hyprctl reload && hyprctl configerrors` succeeded with zero errors.
- `hyprctl binds` confirmed `ALT + SPACE`, `Ctrl + Alt + Space`, `SUPER + CTRL + X`, and `F9` are unbound, leaving only `MOD5 + SPACE` (`AltGr + Space`) for push-to-talk dictation (plus `Escape` to cancel).
