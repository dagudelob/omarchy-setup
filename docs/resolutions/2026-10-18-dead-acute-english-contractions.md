# Fix dead acute producing accented consonants instead of English contractions

- **Date:** 2026-10-18
- **Branch:** `fix/dead-acute-english-contractions`
- **Type:** `fix`

---

## 1. Issue / Requirement
When typing in English on a keyboard layout configured with dead acute (`'`), pressing `'` followed by letters such as `l` or `v` generated accented characters (`ĺ`, `ǘ`) instead of common English contractions like `i'll` or `i've`.

## 2. Root Cause
The default X11 Compose table maps `<dead_acute> <l>` to `ĺ` (Latin Small Letter L With Acute) and `<dead_acute> <v>` to `ǘ` (Latin Small Letter U With Diaeresis And Acute).

## 3. Applied Solution
Added custom Compose override definitions to `~/.XCompose` mapping `<dead_acute>` followed by common contraction consonants (`l`, `v`, `d`, `m`, `s`, `r`, `t` and their uppercase variants) directly to `'` + the respective character. Restarted Fcitx5 with `omarchy-restart-xcompose`.

## 4. Modified Files
- `/home/dagudelo/.XCompose`

## 5. Validation
Reloaded Fcitx5 via `omarchy-restart-xcompose` and verified in active desktop applications that typing `'` + `l` produces `'l` and `'` + `v` produces `'v` while Spanish vowels (`á`, `é`, `í`, `ó`, `ú`) continue working normally.
