# Configuración de entradas de arranque Limine (Linux Surface, Rescate y Windows 11)

- **Date:** 2026-10-18
- **Branch:** `fix/configure-limine-boot-entries`
- **Type:** `fix`

---

## 1. Issue / Requirement
Al reiniciar la Surface se mostraban opciones redundantes y anidadas (`omarchy`, `system-boot`, `EFI fallback`), teniendo que abrir un segundo bootloader para acceder a Windows 11. Se requería simplificar el menú a exactamente tres opciones directas: Omarchy (linux-surface), Modo Rescate (kernel fallback sin interfaz gráfica para emergencias) y Windows 11, con un temporizador de 5 segundos que inicie por defecto en Omarchy.

## 2. Root Cause
- Limine tenía activado `FIND_BOOTLOADERS=yes`, detectando automáticamente `systemd-boot` y el fallback genérico de EFI.
- La partición EFI de fábrica (`/efi`) contaba únicamente con 96 MB de capacidad (17 MB libres), lo que provocaba errores de espacio al intentar generar la imagen completa de kernel fallback (`initramfs-fallback` de ~207 MB).
- Existía una partición dedicada de 1 GB (`/dev/nvme0n1p4`, etiqueta `LINUXBOOT`) que no estaba montada ni vinculada al flujo de instalación de kernels de Limine.

## 3. Applied Solution
1. **Montaje de partición de kernels (1 GB):** Se montó `/dev/nvme0n1p4` en `/boot` agregándola a `/etc/fstab` con su UUID (`9091-D751`).
2. **Configuración de Limine y mkinitcpio:**
   - Se definió `ESP_PATH="/boot"` en `/etc/default/limine` para que los kernels e initramfs se almacenen en la partición de 1 GB.
   - En `/etc/limine-entry-tool.d/99-custom-boot.conf` se estableció `MKINITCPIO_FALLBACK=yes` y `FIND_BOOTLOADERS=no`.
   - Se configuró `/etc/mkinitcpio.conf.d/compression.conf` con compresión `zstd -19`.
3. **Regeneración de kernels:** Se generaron tanto el `initramfs` estándar como el `initramfs-fallback` en `/boot` sin errores de espacio.
4. **Menú Limine en `/efi/limine.conf`:**
   - Se apuntó a los kernels en la partición de 1 GB mediante su GUID (`3a09013c-70a6-4869-a8cb-8091a3dfeb6d`).
   - Se creó la entrada de rescate configurada para arrancar en consola de texto ligera de recuperación (`systemd.unit=multi-user.target`).
   - Se añadió la entrada directa a Windows 11 (`boot():/EFI/Microsoft/Boot/bootmgfw.efi`).
   - Se fijó `timeout: 5` y `default_entry: Omarchy/linux-surface`.

## 4. Modified Files
- `/etc/fstab`
- `/etc/default/limine`
- `/etc/limine-entry-tool.d/99-custom-boot.conf`
- `/etc/mkinitcpio.conf.d/compression.conf`
- `/efi/limine.conf`

## 5. Validation
- Verificada la existencia, tamaño y sumas criptográficas (BLAKE2) de `initramfs`, `initramfs-fallback` y `vmlinuz` en `/boot`.
- Verificado el acceso directo a Windows 11 en `/efi/EFI/Microsoft/Boot/bootmgfw.efi`.
- Verificada la eliminación de entradas intermedias (`system-boot` y `EFI fallback`) en `/efi/limine.conf`.
