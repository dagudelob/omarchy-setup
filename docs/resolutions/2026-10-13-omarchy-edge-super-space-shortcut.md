# Fix Super Space App Launcher Shortcut on Omarchy Edge Channel

- **Date:** 2026-10-13
- **Branch:** `fix/omarchy-edge-super-space-shortcut`
- **Type:** `fix`

---

## 1. Issue / Requirement
After switching Omarchy channel to `edge` and upgrading the system, the `Super + Space` shortcut stopped launching the application menu and search popup.

## 2. Root Cause
Omarchy upstream introduced a new architecture for native global shortcuts (`GlobalShortcut` in Quickshell) handled directly by Hyprland. However, an obsolete local compatibility override directory (`~/.config/omarchy/shell_override/` and wrapper scripts in `~/.local/bin/`) created during an earlier Qt 6.12 bug was still intercepting the shell without implementing the new handlers.

## 3. Applied Solution
1. Removed obsolete wrapper binaries from `~/.local/bin/` (`omarchy-launch-shell`, `omarchy-restart-shell`, `omarchy-shell`).
2. Removed legacy directory `~/.config/omarchy/shell_override/`, allowing the system to use official `/usr/share/omarchy/shell/` with upstream Qt 6 fixes.
3. Restarted Quickshell via `omarchy restart shell` and reloaded Hyprland with `hyprctl reload`.

## 4. Modified Files
- `~/.local/bin/omarchy-launch-shell` (deleted)
- `~/.local/bin/omarchy-restart-shell` (deleted)
- `~/.local/bin/omarchy-shell` (deleted)
- `~/.config/omarchy/shell_override/` (deleted override tree)

## 5. Validation
- Confirmed active process running `/usr/share/omarchy/shell/shell.qml`.
- Verified IPC response and menu toggle via `omarchy-menu toggle`.
- Clean reload of `hyprctl reload` without errors.
- Immediate response of application menu upon pressing `Super + Space`.
