# Install Telegram Desktop via official Arch repository with omarchy update integration

- **Date:** 2026-11-26 23:21:01
- **Branch:** `feature/install-telegram-omarchy-update`
- **Type:** `feature`

---

## 1. Issue / Requirement
Install Telegram Desktop on Omarchy using an installation method that updates automatically whenever `omarchy update` is executed.

## 2. Root Cause
Omarchy's `omarchy-update` script updates system packages through `omarchy-update-system-pkgs` (`omarchy-update-pacman -Syu`). Installing Telegram via an external binary tarball or Flatpak would not integrate with the native `pacman` upgrade cycle run by `omarchy update`.

## 3. Applied Solution
1. Verified that `telegram-desktop` (`7.3.2-1`) is available in the official Arch Linux `extra` repository.
2. Installed `telegram-desktop` as a native Arch package (via `omarchy pkg add telegram-desktop` / `pkexec pacman -S --noconfirm --needed -- telegram-desktop`), pulling in dependencies `libfido2` (`1.17.0-1`) and `tlottie` (`1.0.6-1`).
3. Because `telegram-desktop` is tracked by `pacman`, `omarchy update` (`omarchy-update-system-pkgs`) automatically upgrades it alongside all other system packages.

## 4. Modified Files
- System package database (`pacman`): installed `telegram-desktop 7.3.2-1`, `libfido2 1.17.0-1`, `tlottie 1.0.6-1` (no user config files modified).
- `/home/dagudelo/Code/omarchy-setup/docs/resolutions/2026-11-26-install-telegram-omarchy-update.md`

## 5. Validation
- Verified package installation via `pacman -Q telegram-desktop libfido2 tlottie` (`telegram-desktop 7.3.2-1`, `libfido2 1.17.0-1`, `tlottie 1.0.6-1`).
- Confirmed `/usr/share/omarchy/bin/omarchy-update` invokes `omarchy-update-system-pkgs`, which runs `omarchy-update-pacman -Syu` to upgrade all official Arch packages automatically.
