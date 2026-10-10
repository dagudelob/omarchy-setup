# Surface Touchscreen and Camera Hardware Enablement via Linux Surface Kernel

- **Date:** 2026-10-10
- **Branch:** `fix/surface-touchscreen-linux-kernel`
- **Type:** `fix`

---

## 1. Issue / Requirement
On Microsoft Surface Pro 5 (model 1796) running Arch Linux, the touchscreen input and hardware sensors (Intel IPU3 cameras, IPTS touch digitizer) were non-functional under the default upstream Linux kernel. Additionally, previous attempts to install the dedicated `linux-surface` kernel failed due to an out-of-disk-space error (`No space left on device`) caused by a cramped 96 MB factory EFI system partition (`/boot`).

## 2. Root Cause
1. **Hardware Digitizer & Sensors:** Surface devices utilize proprietary Intel Precise Touch & Stylus (IPTS) firmware and MIPI CSI-2 IPU3 camera interfaces that require custom kernel patches, drivers, and user-space modules not included in vanilla Arch kernels.
2. **ESP Disk Exhaustion:** The factory EFI system partition (`/dev/nvme0n1p1`) was mounted directly at `/boot` with only 96 MB total capacity. Coexisting with Windows Boot Manager files, fonts, and the default Arch kernel, attempting to generate a second kernel (`linux-surface` and its `initramfs`) exceeded available storage.

## 3. Applied Solution
1. **Architectural Boot Reorganization (ESP Migration):**
   - Created `/efi` and unmounted `/dev/nvme0n1p1` from `/boot`.
   - Remounted `/dev/nvme0n1p1` to `/efi` solely for UEFI bootloader binaries (`.efi`), freeing over 60 MB on the ESP.
   - Migrated the actual Linux `/boot` directory directly into the primary 70 GB `ext4` root partition (`/dev/nvme0n1p5`), eliminating kernel disk space constraints permanently.
   - Updated `/etc/fstab` to reflect the new mount points.
   - Configured Limine bootloader (`/efi/EFI/Boot/limine.conf`) with native filesystem drivers to read kernels directly from `uuid(3901acfc-c114-46db-910a-03eda9687849):/boot/`.
2. **Repository & Kernel Deployment:**
   - Imported and signed the official `linux-surface` repository GPG key (`56C464BAAC421453`).
   - Configured `[linux-surface]` in `/etc/pacman.conf` (`https://pkg.surfacelinux.com/arch/`).
   - Installed `linux-surface`, `linux-surface-headers`, `surface-ipts-firmware`, `libcamera`, and `pipewire-libcamera`.
   - Regenerated initramfs images (`initramfs-linux-surface.img`) via `mkinitcpio`.

## 4. Modified Files
- `/etc/pacman.conf`: Added the official `linux-surface` repository.
- `/etc/fstab`: Updated ESP partition mount from `/boot` to `/efi`.
- `/efi/EFI/Boot/limine.conf`: Added dual boot entries reading kernels directly from root ext4 filesystem.
- `/boot/vmlinuz-linux-surface`: Installed Surface-optimized kernel binary.
- `/boot/initramfs-linux-surface.img`: Built dedicated initial ramdisk.

## 5. Verification
- Touchscreen input functionality confirmed working flawlessly upon reboot into `linux-surface`.
- PipeWire and libcamera recognize integrated sensors (`ov5693` front camera, `ov8865` rear camera).
- Storage check confirms 61 MB available on `/efi` and ample headroom on `/boot`.
