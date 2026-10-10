# Migración al Paquete Oficial de Omarchy y Corrección de Espacio EFI

- **Date:** 2026-10-10
- **Branch:** `fix/omarchy-update-official-package`
- **Type:** `fix`

---

## 1. Issue / Requirement
Al ejecutar la actualización de Omarchy (`omarchy update`), el comando fallaba con el error:
`OMARCHY_PATH does not match this Omarchy command. Failed (exit code 1)!`.
Adicionalmente, se requería migrar al paquete oficial de Omarchy distribuido por el repositorio de paquetes (`pacman`), asegurando que las configuraciones locales de usuario no se perdieran, y abordar la falta de espacio en la partición EFI de 100 MB de Microsoft Surface al generar imágenes UKI.

## 2. Root Cause
1. `/usr/share/omarchy` era un enlace simbólico que apuntaba a un checkout git local (`/home/dagudelo/omarchy`). La función de seguridad `omarchy_security_require_source_root` valida que `OMARCHY_PATH` sea canónico y coincida con la ruta física de los binarios, provocando el fallo al detectar la discrepancia del symlink sin haber corrido `omarchy dev link`.
2. El paquete `omarchy` no estaba instalado formalmente vía pacman en el sistema.
3. Al instalar el paquete oficial, el hook `limine-mkinitcpio` intentó generar imágenes UKI completas (`ENABLE_UKI=yes`), las cuales superaban los 12.8 MB disponibles en la partición `/efi` de 96 MB compartida con Windows BitLocker.

## 3. Applied Solution
1. **Verificación de dotfiles y respaldo:** Se confirmó que las configuraciones de usuario en `~/.config/` estaban respaldadas y sincronizadas con GitHub en `omarchy-setup`.
2. **Eliminación del enlace simbólico e instalación oficial:**
   - Se removió el symlink `/usr/share/omarchy`.
   - Se instalaron los paquetes oficiales: `sudo pacman -S --needed --overwrite='*' omarchy omarchy-settings`.
3. **Optimización de arranque para partición EFI pequeña:**
   - Se documentó la causa de BitLocker en `/dev/nvme0n1p3` y el riesgo de redimensionar la partición física de 100 MB.
   - Se determinó el uso del arranque tradicional con Limine (`ENABLE_UKI=no`), manteniendo los kernels e initramfs en `/boot` (sistema de archivos raíz con 68 GB libres) y limpiando imágenes antiguas huérfanas en `/efi`.

## 4. Modified Files
- `/usr/share/omarchy` (restaurado de symlink a directorio del paquete oficial)
- `/etc/limine-entry-tool.d/omarchy-uki.conf`
- Base de datos de paquetes de pacman (`omarchy`, `omarchy-settings`)

## 5. Validation
- Comprobación de instalación del paquete oficial mediante `pacman -Q omarchy omarchy-settings`.
- Verificación del binario oficial `/usr/share/omarchy/bin/omarchy-update` vinculado al sistema.
- Revisión de particiones con `lsblk`, `df -h` y análisis de BitLocker en la Surface.
