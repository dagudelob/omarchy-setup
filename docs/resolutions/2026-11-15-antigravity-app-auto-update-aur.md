# Update Antigravity desktop app via AUR for automatic Omarchy updates

- **Date:** 2026-11-15 14:27:30
- **Branch:** `fix/antigravity-app-auto-update-aur`
- **Type:** `fix`

---

## 1. Issue / Requirement
`Super + Space` continued launching the older Antigravity desktop app (`2.22.1`) even after downloading a newer build (`2.32.1`), and running `Update Omarchy` only updated `mise`-managed CLI tools rather than the desktop app.

## 2. Root Cause
The Antigravity desktop app was manually extracted into `~/Downloads/apps/Antigravity/` and `~/.local/share/applications/antigravity.desktop` was hardcoded to that directory, so downloaded updates (`~/Downloads/apps/Antigravity (1)/`) and `yay`/`omarchy update` could not update the launcher or binary.

## 3. Applied Solution
1. Built and installed the `antigravity` package (`2.32.1-1`) from the AUR:
   ```bash
   yay -S antigravity
   ```
2. Removed the manual local `.desktop` override so the system-wide launcher provided by the AUR package is used:
   ```bash
   rm ~/.local/share/applications/antigravity.desktop
   ```

## 4. Modified Files
- `/usr/share/applications/antigravity.desktop` (installed by AUR package `antigravity`)
- `/home/dagudelo/.local/share/applications/antigravity.desktop` (removed)

## 5. Validation
- Confirmed `pacman -Q antigravity` reports `antigravity 2.32.1-1`.
- Confirmed `/usr/share/applications/antigravity.desktop` is present and the local override in `~/.local/share/applications/antigravity.desktop` is removed, enabling automatic updates via `Update Omarchy` / `yay`.
