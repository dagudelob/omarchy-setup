# Fix ttfx Screensaver Error and Final US International Keyboard Configuration

- **Date:** 2026-10-13
- **Branch:** `fix/screensaver-ttfx-and-us-intl-keyboard`
- **Type:** `fix`

---

## 1. Issue / Requirement
1. When entering idle state, a full-screen window opened displaying recurring error `Error reading input file: No such file or directory (os error 2)`.
2. Maintain optimal keyboard mapping on Surface Pro Type Cover (`English US International` with dead keys), keeping physical punctuation keys (`;` and `:`) while allowing easy typing of accents (`á`, `é`) and `ñ` without changing standard QWERTY layout.

## 2. Root Cause
1. The idle service executed `omarchy-screensaver`, which calls `ttfx -i ~/.config/omarchy/branding/screensaver.txt`. This ASCII art file did not exist in user profile, causing `ttfx` to loop with errors.
2. When testing standard Spanish (`es`) layout, `;` / `:` was remapped to `ñ`, breaking correspondence with hardware labels on the Surface keyboard.

## 3. Applied Solution
1. **Restore Screensaver ASCII Asset:**
   - Created `~/.config/omarchy/branding/` and copied official asset from `/usr/share/omarchy/logo.txt` to `~/.config/omarchy/branding/screensaver.txt`.
   - Committed backup copy to `config/omarchy/branding/screensaver.txt` in repository.
2. **US International Keyboard Configuration:**
   - In `~/.config/hypr/input.lua`, set:
     - `kb_layout = "us"`
     - `kb_variant = "intl"`
     - `kb_options = ""` (preserves standard Caps Lock).
   - Synchronized to `config/hypr/input.lua` in repository.
3. Reloaded Hyprland with `hyprctl reload` and restarted shell with `omarchy restart shell`.

## 4. Modified Files
- `~/.config/omarchy/branding/screensaver.txt`
- `~/.config/hypr/input.lua`
- `config/omarchy/branding/screensaver.txt` (repository)
- `config/hypr/input.lua` (repository)
- `docs/resolutions/2026-10-13-screensaver-ttfx-and-us-intl-keyboard.md`

## 5. Validation
- Executed `ttfx -i ~/.config/omarchy/branding/screensaver.txt` confirming smooth animation without errors.
- Verified with `hyprctl -j devices` that keyboard reports `English (US, intl., with dead keys)`.
- Verified key mappings:
  - Key next to `L` produces `;` and `:`.
  - `Shift + ~` followed by `n` produces `ñ`.
  - `'` followed by vowel produces accents (`á`, `é`, `í`, `ó`, `ú`).
