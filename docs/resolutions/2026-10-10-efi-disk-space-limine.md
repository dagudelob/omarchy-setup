# Fix No Space Left on Device in EFI Partition and Limine Boot Failure

- **Date:** 2026-10-10 19:18:14
- **Branch:** `fix/efi-disk-space-limine`
- **Type:** `fix`

---

## 1. Issue / Requirement
Running `omarchy update` and `limine-update` failed with the error `Failed to copy: ... -> /efi/...: No space left on device` and threw a `NullPointerException` in `limine-entry-tool`, leaving the Omarchy boot entry broken.

## 2. Root Cause
1. The EFI System Partition (`nvme0n1p1`) is only 100 MB (96 MB FAT32 formatted).
2. Two kernels coexisted simultaneously (`linux` and `linux-surface`), alongside 35 MB of Windows bootloader files and Intel microcode (~120 MB total), physically exceeding disk capacity.
3. The `omarchy-settings 4.0.4-1` package forced `ENABLE_UKI=yes`, requiring additional space for monolithic `.efi` images.

## 3. Applied Solution
1. **Safety backup:** Backed up the entire `/efi` partition to external storage (`/run/media/dagudelo/8698-0F9E/efi-backup-2026-10-10/`).
2. **Disable UKI:** Configured `/etc/limine-entry-tool.d/zz-local-no-uki.conf` with `ENABLE_UKI=no`.
3. **Remove redundant kernel:** Uninstalled generic Arch `linux` (`sudo pacman -Rdd linux`), keeping exclusively `linux-surface`.
4. **Cleanup unused files in `/efi`:**
   - Removed unused Asian Windows boot fonts (`chs`, `cht`, `jpn`, `kor`).
   - Removed duplicate backups (`bootmgfw.efi.{...}`, `memtest.efi`, `limine.conf.bak`).
   - Cleaned up orphan images from `/efi` root.
5. **Regenerate Limine:** Executed `sudo limine-update`, generating initramfs and updating `/efi/limine.conf` for `linux-surface`.
6. **Documentation:** Created [docs/redimensionar-efi-bitlocker.md](file:///home/dagudelo/Code/omarchy-setup/docs/redimensionar-efi-bitlocker.md) with guidelines for expanding `nvme0n1p1` using a Live USB after suspending BitLocker.

## 4. Modified Files
- `/etc/limine-entry-tool.d/zz-local-no-uki.conf`
- `/efi/limine.conf`
- `docs/redimensionar-efi-bitlocker.md`
- `docs/resolutions/2026-10-10-efi-disk-space-limine.md`

## 5. Validation
- `df -h /efi` confirms 20 MB free space (81% used).
- `limine-update` completes with exit code 0 without collisions or copy errors.
- `/efi/limine.conf` contains valid entries for `Omarchy //linux-surface` with validated checksums.
