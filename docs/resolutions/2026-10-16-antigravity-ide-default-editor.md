# Set Antigravity IDE as default system text editor

- **Date:** 2026-10-16
- **Branch:** `feature/antigravity-ide-default-editor`
- **Type:** `feature`

---

## 1. Issue / Requirement
The user requested to configure Antigravity IDE as the primary default text and code editor across Omarchy and the desktop environment, replacing VS Code and Neovim fallbacks for file manager actions, system keybindings, and Omarchy config editing.

## 2. Root Cause
The `antigravity-ide.desktop` file contained quotes and spaces in its `Exec` path (`Exec="/home/.../Antigravity IDE/antigravity-ide"`), triggering a known parser flaw in `xdg-mime` that discarded the desktop entry. Additionally, no MIME type associations were declared, the executable was not directly on PATH as `antigravity-ide`, and Omarchy's internal editor state was set to `code`.

## 3. Applied Solution
1. Created symlink `~/.local/bin/antigravity-ide` pointing to `/home/dagudelo/Downloads/apps/Antigravity IDE/bin/antigravity-ide`.
2. Updated `~/.local/share/applications/antigravity-ide.desktop` with clean `Exec=antigravity-ide %F`, `StartupWMClass=antigravity-ide`, and comprehensive text/code `MimeType` associations.
3. Updated desktop database with `update-desktop-database ~/.local/share/applications/`.
4. Configured XDG default applications in `~/.config/mimeapps.list` via `xdg-mime default antigravity-ide.desktop` for `text/plain`, `text/markdown`, `application/json`, and programming source formats.
5. Set Omarchy default editor state via `~/.local/state/omarchy/defaults/editor` to `antigravity-ide`.

## 4. Modified Files
- `/home/dagudelo/.local/bin/antigravity-ide` (created symlink)
- `/home/dagudelo/.local/share/applications/antigravity-ide.desktop` (updated Exec and MimeType)
- `/home/dagudelo/.config/mimeapps.list` (updated Default Applications)
- `/home/dagudelo/.local/state/omarchy/defaults/editor` (set to `antigravity-ide`)

## 5. Validation
- `which antigravity-ide` confirmed available in PATH.
- `xdg-mime query default text/plain` outputs `antigravity-ide.desktop`.
- `omarchy-cmd-present antigravity-ide` succeeds with code 0.
- Hyprland shortcut `SUPER + SHIFT + N` (`omarchy-launch-editor`) correctly targets `antigravity-ide`.
- Desktop notification test sent successfully.
