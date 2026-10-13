# Dual Boot Windows in Limine and Hyprland Autostart via start-hyprland

- **Date:** 2026-10-09
- **Branch:** `fix/limine-windows-and-hyprland-autostart`
- **Type:** `fix`

---

## 1. Issue / Requirement
Upon booting the Surface, the Limine bootloader only displayed Arch Linux, omitting the Windows boot option. Additionally, Hyprland did not launch automatically on TTY login, and manual execution showed warnings about running without `start-hyprland`.

## 2. Root Cause
1. `/boot/EFI/Boot/limine.conf` lacked a chainload entry pointing to the Windows EFI bootloader (`bootmgfw.efi`).
2. `~/.bash_profile` had no autostart rule configured for TTY1, and newer Hyprland releases require launching via the official wrapper script `start-hyprland`.

## 3. Applied Solution
1. Added the `Windows Boot Manager` entry to `/boot/EFI/Boot/limine.conf` using the `efi_chainload` protocol pointing to `boot():/EFI/Microsoft/Boot/bootmgfw.efi`.
2. Configured `~/.bash_profile` to detect TTY1 login and execute `start-hyprland`.

## 4. Modified Files
- `/boot/EFI/Boot/limine.conf`
- `/home/dagudelo/.bash_profile`

## 5. Validation
- Verified syntax in `/boot/EFI/Boot/limine.conf` for both Windows and Arch Linux.
- Confirmed existence and executable permissions of `/usr/bin/start-hyprland`.
- Verified that `~/.bash_profile` automatically launches Hyprland on TTY1 without warnings.
