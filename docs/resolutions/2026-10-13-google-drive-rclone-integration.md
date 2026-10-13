# Google Drive Integration via Rclone and Systemd User Service

- **Date:** 2026-10-13
- **Branch:** `feature/google-drive-rclone-integration`
- **Type:** `feature`

---

## 1. Issue / Requirement
Integrate Google Drive into Omarchy/Arch Linux to access files seamlessly, persistently, and directly through Nautilus and the local filesystem.

## 2. Root Cause
The official `gvfs-google` (`gvfsd-google`) GNOME Online Accounts backend was dropped in Arch Linux due to upstream deprecation of `libgdata`. Adding a Google account in GNOME Settings therefore failed to mount the drive in Nautilus.

## 3. Applied Solution
1. Configured an Rclone `drive` remote named `gdrive` using OAuth2 browser authentication.
2. Created local mount point at `~/GoogleDrive`.
3. Created and enabled systemd user service `~/.config/systemd/user/rclone-gdrive.service` with VFS cache writes, auto-reconnect, and session autostart.
4. Added `Google Drive` to GTK bookmarks (`~/.config/gtk-3.0/bookmarks`) for instant access from the Nautilus sidebar.

## 4. Modified Files
- `/home/dagudelo/.config/systemd/user/rclone-gdrive.service`
- `/home/dagudelo/.config/gtk-3.0/bookmarks`
- `/home/dagudelo/.config/rclone/rclone.conf` (not tracked in git for credential safety)
- `docs/resolutions/2026-10-13-google-drive-rclone-integration.md`

## 5. Validation
- `systemctl --user status rclone-gdrive.service` reports `active (running)`.
- Successfully listed remote directories in `~/GoogleDrive` showing cloud folders (`AI`, `Obsidian`, `Documents`, etc.).
- Confirmed working bookmark in Nautilus sidebar.
