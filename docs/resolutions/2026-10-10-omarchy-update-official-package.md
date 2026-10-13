# Migration to Official Omarchy Package and EFI Space Fix

- **Date:** 2026-10-10
- **Branch:** `fix/omarchy-update-official-package`
- **Type:** `fix`

---

## 1. Issue / Requirement
Running `omarchy update` failed with the error:
`OMARCHY_PATH does not match this Omarchy command. Failed (exit code 1)!`.
Additionally, needed to migrate to the official Omarchy package distributed via `pacman`, preserve local user configurations, and resolve the 100 MB EFI partition exhaustion when generating UKI images on Microsoft Surface.

## 2. Root Cause
1. `/usr/share/omarchy` was a symlink pointing to a local git checkout (`/home/dagudelo/omarchy`). The security check `omarchy_security_require_source_root` requires `OMARCHY_PATH` to be canonical and match binary paths, failing when detecting the mismatched symlink without `omarchy dev link`.
2. The `omarchy` package was not formally installed through pacman.
3. Upon official package installation, the `limine-mkinitcpio` hook attempted to build monolithic UKI images (`ENABLE_UKI=yes`), exceeding the 12.8 MB remaining in the 96 MB EFI partition shared with Windows BitLocker.

## 3. Applied Solution
1. **Dotfiles Backup Verification:** Confirmed user configurations in `~/.config/` were backed up and pushed to `omarchy-setup` on GitHub.
2. **Remove Symlink and Install Official Packages:**
   - Removed `/usr/share/omarchy` symlink.
   - Installed official packages: `sudo pacman -S --needed --overwrite='*' omarchy omarchy-settings`.
3. **Boot Optimization for Small EFI Partition:**
   - Documented BitLocker layout on `/dev/nvme0n1p3` and risks of resizing the partition.
   - Preserved traditional Limine boot (`ENABLE_UKI=no`), storing kernels and initramfs on the root filesystem (68 GB free) and cleaning orphan images from `/efi`.

## 4. Modified Files
- `/usr/share/omarchy` (restored from symlink to official directory)
- `/etc/limine-entry-tool.d/omarchy-uki.conf`
- Pacman package database (`omarchy`, `omarchy-settings`)

## 5. Validation
- Verified installation with `pacman -Q omarchy omarchy-settings`.
- Verified official binary `/usr/share/omarchy/bin/omarchy-update`.
- Confirmed partition layout and stability with `lsblk` and `df -h`.
