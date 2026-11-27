# Keep linux-surface Kernel and Explain Limine Fallback Entry

- **Date:** 2026-11-27 00:04:12
- **Branch:** `fix/linux-surface-kernel-limine-fallback`
- **Type:** `fix`

---

## 1. Issue / Requirement
After attempting a kernel change, an unexpected `//linux-surface-fallback` entry appeared in the Limine boot menu. Needed to clarify the origin of the fallback entry, understand the differences between the standard Arch `linux` kernel and `linux-surface` on Microsoft Surface Pro (`Surface_Pro_1796`), and decide which kernel to keep.

## 2. Root Cause
- The `//linux-surface-fallback` entry in `/boot/limine.conf` is not a separate `linux` kernel; it is an auto-generated `initramfs-fallback` entry created by `limine-entry-tool` because `/etc/limine-entry-tool.d/99-custom-boot.conf` defines `MKINITCPIO_FALLBACK=yes` (alongside `ENABLE_LIMINE_FALLBACK=yes` in `omarchy-defaults.conf`).
- Only `linux-surface` (`6.19.8.arch1-3`) is currently installed; the standard `linux` package is not installed, while `iptsd` (`3.1.0-1`) and `surface-ipts-firmware` (`20200929-1`) rely on `linux-surface` patches for Surface Pro (`Surface_Pro_1796`) touchscreen, stylus, and IPU3 camera support.

## 3. Applied Solution
No system configuration files were modified by user decision:
- Confirmed `linux-surface` (`6.19.8-arch1-3-surface`) remains the active and sole installed kernel to preserve full Surface Pro hardware support (IPTS touch/pen and Intel IPU3 cameras).
- Documented when to use `linux-surface` (Surface hardware features) vs. standard `linux` (native `[core]` updates, fallback stability, or non-Surface hardware) and how `//linux-surface-fallback` is controlled via `MKINITCPIO_FALLBACK=yes` in `/etc/limine-entry-tool.d/99-custom-boot.conf`.

## 4. Modified Files
- `/home/dagudelo/Code/omarchy-setup/docs/resolutions/2026-11-27-linux-surface-kernel-limine-fallback.md`

## 5. Validation
Verified current system state via `uname -r` (`6.19.8-arch1-3-surface`), `pacman -Q` (`linux-surface 6.19.8.arch1-3`, `iptsd 3.1.0-1`, `surface-ipts-firmware 20200929-1`), and inspection of `/boot/limine.conf` and `/etc/limine-entry-tool.d/99-custom-boot.conf`.
