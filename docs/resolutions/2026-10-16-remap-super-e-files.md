# Remap Super + E to open Files (Nautilus)

- **Date:** 2026-10-16 11:50:49
- **Branch:** `feature/remap-super-e-files`
- **Type:** `feature`

---

## 1. Issue / Requirement
The user requested mapping the key combination `Super + E` to launch the Files file manager application (`nautilus`) in Omarchy / Hyprland.

## 2. Root Cause
In Omarchy defaults, the file manager was bound to `Super + Shift + F`, while `Super + E` was unassigned (only `Super + Ctrl + E` and `Super + Shift + E` were assigned).

## 3. Applied Solution
1. Added keybinding override in `~/.config/hypr/bindings.lua`:
   ```lua
   -- Abrir Files (administrador de archivos) con Super + E
   o.bind("SUPER + E", "Files", { launch = "nautilus" })
   ```
2. Reloaded Hyprland configuration with `hyprctl reload`.
3. Synced updated configuration into `config/hypr/bindings.lua` in `omarchy-setup`.

## 4. Modified Files
- `/home/dagudelo/.config/hypr/bindings.lua`
- `/home/dagudelo/Code/omarchy-setup/config/hypr/bindings.lua`
- `/home/dagudelo/Code/omarchy-setup/docs/resolutions/2026-10-16-remap-super-e-files.md`

## 5. Validation
1. Ran `hyprctl reload && hyprctl configerrors` (reported `ok`, no configuration errors).
2. Ran `omarchy menu keybindings --print | grep -E '^SUPER \+ E\b'` confirming `SUPER + E → Files`.
3. Inspected active bindings with `hyprctl binds` to verify dispatcher registration.
