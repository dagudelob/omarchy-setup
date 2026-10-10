# Fix No Space Left on Device in EFI Partition and Limine Boot Failure

- **Date:** 2026-10-10 19:18:14
- **Branch:** `fix/efi-disk-space-limine`
- **Type:** `fix`

---

## 1. Issue / Requirement
Al ejecutar `omarchy update` y `limine-update`, la actualización fallaba con el error `Failed to copy: ... -> /efi/...: No space left on device` y arrojaba una excepción `NullPointerException` en `limine-entry-tool`, dejando la entrada de arranque de Omarchy incompleta o rota.

## 2. Root Cause
1. La partición EFI (`nvme0n1p1`) mide solo 100 MB (96 MB formateados en FAT32).
2. Convivían dos kernels simultáneos (`linux` genérico y `linux-surface`), más 35 MB de archivos de Windows y el microcódigo de Intel (~120 MB en total), excediendo físicamente la capacidad del disco.
3. El paquete `omarchy-settings 4.0.4-1` forzó `ENABLE_UKI=yes`, requiriendo espacio adicional para imágenes monobloque `.efi`.

## 3. Applied Solution
1. **Respaldo de seguridad:** Se respaldó la partición `/efi` completa en almacenamiento externo (`/run/media/dagudelo/8698-0F9E/efi-backup-2026-10-10/`).
2. **Desactivación de UKI:** Se configuró `/etc/limine-entry-tool.d/zz-local-no-uki.conf` con `ENABLE_UKI=no`.
3. **Eliminación del kernel redundante:** Se desinstaló el paquete `linux` de Arch (`sudo pacman -Rdd linux`), conservando exclusivamente `linux-surface`.
4. **Limpieza de archivos innecesarios en `/efi`:**
   - Se removieron fuentes asiáticas de arranque de Windows no utilizadas (`chs`, `cht`, `jpn`, `kor`).
   - Se removieron backups duplicados (`bootmgfw.efi.{...}`, `memtest.efi`, `limine.conf.bak`).
   - Se removieron imágenes huérfanas en la raíz de `/efi`.
5. **Regeneración de Limine:** Se ejecutó `sudo limine-update`, generando exitosamente el initramfs y actualizando `/efi/limine.conf` para `linux-surface`.
6. **Documentación:** Se generó la guía [docs/redimensionar-efi-bitlocker.md](file:///home/dagudelo/Code/omarchy-setup/docs/redimensionar-efi-bitlocker.md) con los pasos para agrandar `nvme0n1p1` mediante Live USB desactivando BitLocker a futuro.

## 4. Modified Files
- `/etc/limine-entry-tool.d/zz-local-no-uki.conf`
- `/efi/limine.conf`
- `docs/redimensionar-efi-bitlocker.md`
- `docs/resolutions/2026-10-10-efi-disk-space-limine.md`

## 5. Validation
- `df -h /efi` muestra 20 MB libres (81% de uso).
- `limine-update` finaliza con código de salida 0 sin advertencias de colisión ni fallas de copia.
- `/efi/limine.conf` contiene la entrada funcional de `Omarchy //linux-surface` con sus checksums validados.
