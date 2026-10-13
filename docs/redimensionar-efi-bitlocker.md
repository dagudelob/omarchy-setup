# EFI System Partition Resizing and BitLocker Management Guide

This document details the procedure for disabling BitLocker, resizing the system EFI partition (`/dev/nvme0n1p1`) on a Microsoft Surface Pro dual-boot setup (Windows 11 + Omarchy / Arch Linux), and critical precautions to prevent data loss or boot failures.

---

## 1. Context and Disk Layout

The Microsoft Surface Pro features an NVMe drive originally partitioned by Windows:
- **`nvme0n1p1`**: EFI System Partition (ESP), FAT32, **100 MB** (mounted at `/efi` in Linux).
- **`nvme0n1p2`**: Microsoft Reserved Partition (MSR), **16 MB**.
- **`nvme0n1p3`**: Windows partition (C:), NTFS encrypted with **BitLocker**, **~378 GB**.
- **`nvme0n1p4`**: Windows recovery partition, NTFS, **888 MB**.
- **`nvme0n1p5`**: Omarchy / Arch Linux (root `/`), ext4, **~98 GB**.

### Why does the EFI partition run out of space?
The factory 100 MB is ~35 MB occupied by Microsoft bootloaders and the rest by Linux kernels and initramfs images. When updating packages using unified kernel images (UKI) or generating two concurrent kernels (`linux` and `linux-surface`), the partition exhausts its last 13 MB of free space and aborts file copies.

---

## 2. Important Risks and Warnings

> [!CAUTION]
> **Risk of Windows boot lockout (BitLocker TPM)**  
> If disk partitions are moved or modified while BitLocker is active, the TPM chip will detect a change in boot platform configuration (PCRs) and lock the drive, prompting for the **48-digit BitLocker Recovery Key**. Without this key, Windows data becomes irrecoverable.  
> **Golden rule:** Fully decrypt before modifying partitions and ensure the recovery key is safely backed up from [account.microsoft.com/devices/recoverykey](https://account.microsoft.com/devices/recoverykey).

> [!WARNING]
> **Moving the starting sector of a large partition is an intensive operation**  
> For `p1` to expand to the right, `p2` and `p3` must be physically relocated forward on disk. Moving hundreds of gigabytes block by block may take 20 to 60 minutes. **Never interrupt the process or allow the Surface battery to drain** (keep the charger connected).

> [!IMPORTANT]
> **UEFI Boot / Partition UUID**  
> Partition `p1` must retain its FAT32 filesystem and ideally preserve its PARTUUID/UUID. If recreated from scratch, files must be restored from backup and `/etc/fstab` verified in Linux.

---

## 3. Preparation and Prior Backups

### A. Back up the current EFI partition from Linux
With an external USB drive connected (e.g. at `/run/media/dagudelo/8698-0F9E`):
```bash
sudo cp -a /efi /run/media/dagudelo/8698-0F9E/efi-backup-$(date +%F)
```
Verify that the folder contains `EFI/Microsoft`, `EFI/Boot`, `EFI/limine`, etc.

### B. Back up your BitLocker Recovery Key
1. In Windows, go to **Settings** $\rightarrow$ **Accounts** $\rightarrow$ or search for **BitLocker**.
2. Save the 48-digit numeric key to your phone or a physical notepad.

---

## 4. Step-by-Step: Disable BitLocker and Restructure

### Step 1: Disable BitLocker in Windows
1. Log into **Windows**.
2. Open Start Menu, search for **"Manage BitLocker"** (or go to *Settings > Privacy & security > Device encryption*).
3. Click **Turn off BitLocker** (or disable encryption).
4. Wait until the decryption progress reaches **100%**. Verify in File Explorer that drive `C:` no longer displays a lock icon.
5. Reboot Windows once to ensure a clean shutdown (avoiding Fast Startup hybrid state).
   > *Tip:* You can trigger a full shutdown by holding down `Shift` while clicking "Shut down".

---

### Step 2: Resize with Live USB (GParted)
Since mounted partitions cannot be moved, boot into a Live USB:
1. Prepare a USB drive with **GParted Live** (or any graphical Linux ISO containing GParted).
2. Boot the Surface from USB (hold *Volume Down* while powering on).
3. Open **GParted** and select the NVMe drive (`/dev/nvme0n1`) from the top-right corner.
4. Follow this exact sequence:
   1. **Shrink and shift Windows (`nvme0n1p3`)**:
      - Right-click `nvme0n1p3` $\rightarrow$ **Resize/Move**.
      - In **Free space preceding (MiB)**, enter `1024` (1 GB) or drag the left partition edge to the right to leave ~1 GB free space to its left.
   2. **Move the MSR partition (`nvme0n1p2`)**:
      - Right-click `nvme0n1p2` $\rightarrow$ **Resize/Move**.
      - Drag it rightward until adjacent to the start of the Windows partition.
   3. **Expand the EFI partition (`nvme0n1p1`)**:
      - Right-click `nvme0n1p1` $\rightarrow$ **Resize/Move**.
      - Drag its right edge to occupy all newly unallocated space (totaling ~1.1 GB).
5. Click the green checkmark button **Apply All Operations**.
6. Allow the process to complete without disconnecting AC power.

---

### Step 3: First Boot into Windows
1. Remove the Live USB and boot directly into **Windows**.
2. Windows may perform a brief disk scan and repair check (`chkdsk`); this is standard after moving NTFS sectors.
3. Open Windows Disk Management to verify the EFI partition now measures ~1 GB.
4. *(Optional)* If you wish to re-encrypt Windows, re-enable BitLocker from Control Panel.

---

### Step 4: Final Adjustments in Omarchy / Arch Linux
1. Boot into **Omarchy** (Linux).
2. Check the new partition size:
   ```bash
   df -h /efi
   ```
3. Update or rebuild kernels without storage risk:
   ```bash
   sudo mkinitcpio -P
   ```
4. The expanded space will accommodate Surface kernels, standard kernels, and UKIs without storage bottlenecks.
