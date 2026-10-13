# BitLocker Recovery and Stabilization when Booting Windows from Limine

- **Date:** 2026-10-09
- **Branch:** `fix/bitlocker-limine-boot`
- **Type:** `fix`

---

## 1. Issue / Requirement
When selecting Windows Boot Manager from the Limine bootloader in a dual-boot setup, Windows repeatedly prompted for the 48-digit BitLocker recovery key before allowing the user to sign in.

## 2. Root Cause
Modifying the UEFI boot chain by introducing Limine altered the TPM PCR register measurements. Detecting a variance in the platform boot sequence, BitLocker triggered its protection mechanism and locked the encrypted volume.

## 3. Applied Solution
1. Retrieved the 48-digit BitLocker numerical recovery key via the linked Microsoft account (`https://account.microsoft.com/devices/recoverykey`).
2. Unlocked the system drive by entering the recovery key on the Windows blue screen.
3. Updated the TPM protector measurements in Windows by running PowerShell / CMD as Administrator:
   - Temporarily suspended BitLocker protectors:
     ```cmd
     manage-bde -protectors -disable C:
     ```
   - Rebooted through Limine into Windows and re-enabled protectors to record the new boot measurements:
     ```cmd
     manage-bde -protectors -enable C:
     ```

## 4. Modified Files
- `docs/resolutions/2026-10-09-bitlocker-limine-boot.md`

## 5. Validation
Confirmed stable Windows boot directly from Limine without any further BitLocker recovery prompts.
