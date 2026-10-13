# Fix Limine root cmdline and Qt 6.12 Omarchy shell invisibility

- **Date:** 2026-10-10
- **Branch:** `fix/limine-root-cmdline-and-qt612-shell`
- **Type:** `fix`

---

## 1. Issue / Requirement
1. After rebooting, Limine halted boot requiring manual entry of `root=/dev/nvme0n1p5 rw` via `Ctrl+X`.
2. The top bar (`omarchy-bar`) was invisible, and pressing `Super + Space` produced a blank screen without showing the application menu.
3. Syntax error in `~/.config/hypr/autostart.lua` reporting `attempt to call a nil value (field 'spawn')`.

## 2. Root Cause
1. `/efi/limine.conf` lacked the `root=...` parameter for `linux-surface`, as `/etc/limine-entry-tool.d/omarchy-defaults.conf` only used `+=` with secondary flags.
2. The update to `qt6-declarative 6.12.0` introduced a native internal singleton in QtQuick named `Color` (`QQuickColor`), conflicting with Omarchy's `Color.qml` singleton and causing style properties (`Color.bar.*`, `Color.menu.*`) to return `undefined`.
3. In Hyprland with Lua configuration backend, the autostart dispatch function is `hl.exec_cmd(...)` rather than `o.spawn(...)`.

## 3. Applied Solution
1. **Limine:** Configured `/etc/limine-entry-tool.d/00-root.conf` with `KERNEL_CMDLINE[default]="root=PARTUUID=087e8082-4f40-49be-bfc8-195af01c64f7 rw rootfstype=ext4"` and rebuilt with `limine-update`.
2. **Omarchy Shell / Qt 6.12:** Created an override tree in `~/.config/omarchy/shell_override/` renaming the singleton to `OmaColor`, adjusted shell components, and wrapped shell launchers in `~/.local/bin/`.
3. **Hyprland:** Fixed `~/.config/hypr/autostart.lua` and prepended `~/.local/bin` to `PATH` in `~/.config/hypr/hyprland.lua`.

## 4. Modified Files
- `/etc/limine-entry-tool.d/00-root.conf`
- `/efi/limine.conf`
- `~/.config/hypr/autostart.lua`
- `~/.config/hypr/hyprland.lua`
- `~/.config/omarchy/shell_override/`
- `~/.local/bin/omarchy-launch-shell`
- `~/.local/bin/omarchy-restart-shell`
- `~/.local/bin/omarchy-shell`

## 5. Validation
- Checked with `hyprctl configerrors` (clean, 0 errors).
- Top bar verified visible and functional with system tray, clock, and workspace indicators.
- Menu opens smoothly via `Super + Space` (`omarchy-menu toggle`).
- Persistent kernel commandline generated successfully by `limine-update`.
