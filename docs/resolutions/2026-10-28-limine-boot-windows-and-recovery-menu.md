# Limine Boot Menu: Restore Windows 11 Dual Boot and System Recovery Tools Dropdown

- **Date:** 2026-10-28
- **Branch:** `fix/limine-boot-windows-and-recovery-menu`
- **Type:** `fix`

---

## 1. Issue / Requirement
After system updates, the Limine bootloader on the Surface Pro did not list the Windows 11 entry, preventing the user from booting into Windows. Furthermore, the user requested an intuitive, clean boot menu entirely in English featuring direct entries for the two primary operating systems (Omarchy and Windows 11), while grouping and hiding restoration/maintenance options (fallback kernel, rescue shell, initramfs prompt) inside a collapsible dropdown menu.

## 2. Root Cause
1. UEFI was booting `Boot0006` from `/dev/nvme0n1p4` (`/boot`, 1 GB LINUXBOOT partition), loading `/boot/limine.conf`.
2. A recent package/kernel update triggered `limine-entry-tool`, regenerating `/boot/limine.conf` with only the Linux Surface kernel entries, omitting Windows 11 (which had previously been placed in `/efi/limine.conf`).
3. Limine's default configuration expanded all entries under `+Omarchy`, exposing technical kernel labels (`linux-surface`, `linux-surface-fallback`) flatly in the root boot menu instead of user-friendly names.

## 3. Applied Solution
1. **Windows 11 Integration:** Added an EFI chainload entry directly targeting Windows Boot Manager on partition 1 via its filesystem/partition UUID (`uuid(6e48e620-9525-467a-a0b3-c58365067fd3):/EFI/Microsoft/Boot/bootmgfw.efi`).
2. **Main OS Presentation:** Configured top-level direct entries for `Omarchy` (as `default_entry: 1` with a 5-second timeout) and `Windows 11`.
3. **Dedicated Recovery Submenu:** Created a collapsed directory `/System Recovery Tools` (without `+`), hidden from normal boot view and expandable using the Right Arrow (`→`), containing:
   - `Omarchy (Fallback Kernel)`: Full driver initramfs fallback.
   - `Linux Rescue Shell (Maintenance Mode)`: Minimal root terminal (`systemd.unit=rescue.target`).
   - `Initramfs Emergency Shell (Early RAM Debug)`: Early BusyBox RAM prompt (`break=premount`).
4. **Automation Script:** Created `/tmp/update_limine.sh` to safely apply the configuration with automatic backups of `/boot/limine.conf` and synchronized `/efi/limine.conf`.

## 4. Modified Files
- `/boot/limine.conf`
- `/efi/limine.conf`
- `/tmp/update_limine.sh`
- `docs/resolutions/2026-10-28-limine-boot-windows-and-recovery-menu.md`

## 5. Validation
- Verified syntax, hashes, and directory nesting in `/boot/limine.conf` according to Limine v12 specifications.
- Verified Windows boot executable existence and partition UUID mapping on `/dev/nvme0n1p1`.
- Verified user confirmation of the solution ("tema solucionado").
