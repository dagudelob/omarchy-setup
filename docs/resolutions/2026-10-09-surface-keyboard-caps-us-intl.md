# Surface Keyboard Fix: Traditional CapsLock and US International (Dead Keys)

- **Date:** 2026-10-09
- **Branch:** `fix/surface-keyboard-caps-us-intl`
- **Type:** `fix`

---

## 1. Issue / Requirement
1. Pressing `Caps Lock` produced accented characters or opened the compose menu instead of acting as standard uppercase toggle.
2. Unable to generate `ñ` with `~` + `n`, or accented vowels via `'` + vowel (matching Windows US-International behavior).

## 2. Root Cause
- Omarchy defaults to `compose:caps` in Hyprland, remapping CapsLock as a Compose key.
- The default layout was basic `us` (without dead keys), and the `altgr-intl` variant placed `~` on AltGr while producing ordinal symbols on direct press.

## 3. Applied Solution
1. In `~/.config/hypr/input.lua`, configured:
   - `kb_layout = "us"`
   - `kb_variant = "intl"` (English US International with dead keys)
   - `kb_options = ""` (removed `compose:caps` to restore standard CapsLock).
2. In `~/.config/hypr/bindings.lua`, added quick layout toggle binding:
   - `Super + Alt + K` to cycle keyboard layouts (`hyprctl switchxkblayout all next`).
3. Reloaded configuration with `hyprctl reload`.

## 4. Modified Files
- `~/.config/hypr/input.lua`
- `~/.config/hypr/bindings.lua`
- `dotfiles/hypr/input.lua`
- `dotfiles/hypr/bindings.lua`

## 5. Validation
- `hyprctl devices` confirmed active rules: `l "us", v "intl"`.
- `CapsLock` toggles uppercase properly.
- `Shift + ~` followed by `n` yields `ñ` / `Ñ`.
- `'` followed by vowels yields accented letters (`á`, `é`, `í`, `ó`, `ú`).
