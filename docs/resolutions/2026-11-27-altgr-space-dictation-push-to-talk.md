# Configure AltGr + Space for push-to-talk dictation on US-intl layout

- **Date:** 2026-11-27
- **Branch:** `fix/altgr-space-dictation-push-to-talk`
- **Type:** `fix`

---

## 1. Issue / Requirement
Right Alt did not trigger Omarchy's default push-to-talk dictation shortcut on the custom `us(intl-livequote)` keyboard layout. The user wanted to keep Right Alt functioning as `AltGr` (distinct from Left Alt) while binding `AltGr + Space` for push-to-talk dictation.

## 2. Root Cause
Omarchy's default dictation config (`/usr/share/omarchy/default/hypr/bindings/dictation.lua`) binds `ALT + Alt_R`, whereas `us(intl-livequote)` inherits `us(intl)` (`level3(ralt_switch)`), causing physical Right Alt (`<RALT>`, keycode 108) to emit `ISO_Level3_Shift` (`MOD5` / `AltGr`) instead of `Alt_R`.

## 3. Applied Solution
Added a user-level override in `~/.config/hypr/bindings.lua` (preserving `/usr/share/omarchy/` read-only so updates don't overwrite it):
- Unbound the non-matching default `ALT + Alt_R` via `hl.unbind("ALT + Alt_R")`.
- Bound `MOD5 + SPACE` (`AltGr + Space`) with `o.bind_hold(...)` for `omarchy-dictation start` / `omarchy-dictation stop`.
- Kept `AltGr` intact for third-level characters and `ALT + SPACE` (Left Alt + Space) for toggle dictation.
- Reloaded Hyprland with `hyprctl reload`.

## 4. Modified Files
- `/home/dagudelo/.config/hypr/bindings.lua`
- `/home/dagudelo/Code/omarchy-setup/config/hypr/bindings.lua`
- `/home/dagudelo/Code/omarchy-setup/docs/resolutions/2026-11-27-altgr-space-dictation-push-to-talk.md`

## 5. Validation
- `hyprctl reload` returned `ok` and `hyprctl configerrors` returned no errors.
- `hyprctl binds` confirmed `modmask: 128` (`MOD5`) + `SPACE` bound to `Start/Stop dictation (push-to-talk)` and `ALT + Alt_R` removed.
- User confirmed `AltGr + Space` push-to-talk dictation works as expected while keeping `AltGr` functional.
