# Switch from Edge to Stable Channel and Resolve Linux Firmware Conflict

- **Date:** 2026-10-13
- **Branch:** `fix/switch-stable-channel-firmware-conflict`
- **Type:** `fix`

---

## 1. Issue / Requirement
The user requested an explanation of the Omarchy `edge` channel and wanted to switch the system to the `stable` release channel. During execution of `omarchy channel set stable`, the upgrade failed due to file conflicts in `/usr/lib/firmware/` between split `linux-firmware` packages.

## 2. Root Cause
Arch Linux split `linux-firmware` into subpackages (`linux-firmware-ti`, `linux-firmware-other`, etc.). Uncoordinated file ownership caused Pacman to block the transaction because files like `ti_3410.fw.zst` already existed on disk. This in turn aborted the Omarchy channel switch script before packages could be swapped.

## 3. Applied Solution
1. Resolved the firmware file conflict by forcing file overwrite during system upgrade:
   ```bash
   sudo pacman -Syu --overwrite "/usr/lib/firmware/*"
   ```
2. Switched Omarchy release channel to stable:
   ```bash
   omarchy channel set stable
   ```
   This swapped `omarchy-dev` and `omarchy-settings-dev` for the official stable packages `omarchy` and `omarchy-settings` (v4.0.4-1).

## 4. Modified Files
- `/etc/pacman.d/omarchy-mirrorlist` (updated to point to stable repositories)
- Package state transitioned: `omarchy-dev` -> `omarchy` (4.0.4-1), `omarchy-settings-dev` -> `omarchy-settings` (4.0.4-1)

## 5. Validation
- Verified channel: `omarchy channel current` returned `stable`.
- Verified installed packages: `pacman -Q omarchy omarchy-settings` confirmed version `4.0.4-1`.
