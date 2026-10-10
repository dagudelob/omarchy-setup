# Guía de Redimensionamiento de Partición EFI y Gestión de BitLocker

Este documento detalla el procedimiento para desactivar BitLocker, redimensionar la partición EFI de sistema (`/dev/nvme0n1p1`) en una Microsoft Surface Pro con arranque dual (Windows 11 + Omarchy / Arch Linux), y las precauciones críticas para evitar pérdida de datos o bloqueos del arranque.

---

## 1. Contexto y Estado del Disco

La Microsoft Surface Pro cuenta con una unidad NVMe particionada originalmente por Windows:
- **`nvme0n1p1`**: EFI System Partition (ESP), FAT32, **100 MB** (montada en `/efi` en Linux).
- **`nvme0n1p2`**: Microsoft Reserved Partition (MSR), **16 MB**.
- **`nvme0n1p3`**: Partición de Windows (C:), NTFS cifrado con **BitLocker**, **~378 GB**.
- **`nvme0n1p4`**: Partición de recuperación de Windows, NTFS, **888 MB**.
- **`nvme0n1p5`**: Omarchy / Arch Linux (raíz `/`), ext4, **~98 GB**.

### ¿Por qué se satura la partición EFI?
Los 100 MB de fábrica están ocupados en ~35 MB por los cargadores de Microsoft y el resto por los kernels e initramfs de Linux. Al actualizar paquetes que usan imágenes unificadas (UKI) o generar dos kernels simultáneos (`linux` y `linux-surface`), la partición agota los últimos 13 MB libres y aborta la copia de archivos.

---

## 2. Peligros y Advertencias Importantes

> [!CAUTION]
> **Riesgo de bloqueo de arranque de Windows (BitLocker TPM)**  
> Si se mueven o modifican las particiones del disco con BitLocker activado, el chip TPM detectará un cambio en la configuración de la plataforma de arranque (PCRs) y bloqueará la unidad pidiendo la **Clave de Recuperación de BitLocker de 48 dígitos**. Si no tienes esa clave, los datos de Windows quedan irrecuperables.  
> **Regla de oro:** Desencriptar por completo antes de tocar particiones y tener la clave a mano respaldada desde [account.microsoft.com/devices/recoverykey](https://account.microsoft.com/devices/recoverykey).

> [!WARNING]
> **Mover el sector inicial de una partición grande es una operación pesada**  
> Para que `p1` crezca a la derecha, `p2` y `p3` deben moverse físicamente hacia adelante en el disco. Mover cientos de gigabytes bloque por bloque puede tardar entre 20 y 60 minutos. **Nunca interrumpas el proceso ni permitas que la Surface se quede sin batería** (mantén el cargador conectado).

> [!IMPORTANT]
> **Arranque UEFI / UUID de partición**  
> La partición `p1` debe mantener su formato FAT32 y preferiblemente conservar su PARTUUID/UUID. Si se recrea desde cero, habrá que restaurar los archivos del respaldo y verificar `/etc/fstab` en Linux.

---

## 3. Preparación y Respaldos Previos

### A. Respaldar la partición EFI actual desde Linux
Con una memoria USB o disco externo conectado (ej. en `/run/media/dagudelo/8698-0F9E`):
```bash
sudo cp -a /efi /run/media/dagudelo/8698-0F9E/efi-backup-$(date +%F)
```
Verifica que la carpeta contenga `EFI/Microsoft`, `EFI/Boot`, `EFI/limine`, etc.

### B. Respaldar la Clave de Recuperación de BitLocker
1. En Windows, ve a **Configuración** $\rightarrow$ **Cuentas** $\rightarrow$ o busca **BitLocker**.
2. Guarda el código numérico de 48 dígitos en tu teléfono o libreta física.

---

## 4. Paso a Paso: Desactivar BitLocker y Reestructurar

### Paso 1: Desactivar BitLocker en Windows
1. Inicia sesión en **Windows**.
2. Abre el Menú Inicio, busca **"Administrar BitLocker"** (o ve a *Configuración > Privacidad y seguridad > Cifrado de dispositivo*).
3. Haz clic en **Desactivar BitLocker** (o desactivar cifrado).
4. Espera a que el porcentaje de descifrado llegue al **100%**. Confirma que en el Explorador de Archivos la unidad `C:` ya no tenga el icono de candado.
5. Reinicia Windows una vez para asegurarte de que cerró limpiamente (evitar estado de suspensión rápida/Fast Startup).
   > *Tip:* Puedes hacer un apagado completo manteniendo presionada la tecla `Shift` al hacer clic en "Apagar".

---

### Paso 2: Redimensionar con Live USB (GParted)
Dado que las particiones montadas no pueden ser desplazadas, utiliza un Live USB:
1. Prepara una memoria USB con **GParted Live** (o cualquier ISO de Linux con interfaz gráfica y GParted).
2. Arranca la Surface desde la USB (manteniendo presionado *Bajar Volumen* al encender).
3. Abre **GParted** y selecciona en la esquina superior derecha el disco NVMe (`/dev/nvme0n1`).
4. Sigue esta secuencia exacta:
   1. **Achicar y desplazar Windows (`nvme0n1p3`)**:
      - Clic derecho en `nvme0n1p3` $\rightarrow$ **Resize/Move**.
      - En el campo **Free space preceding (MiB)**, introduce `1024` (1 GB) o arrastra el inicio de la partición hacia la derecha para dejar ~1 GB libre a la izquierda.
   2. **Mover la partición MSR (`nvme0n1p2`)**:
      - Clic derecho en `nvme0n1p2` $\rightarrow$ **Resize/Move**.
      - Arrástrala a la derecha hasta quedar pegada al inicio de la partición de Windows.
   3. **Expandir la partición EFI (`nvme0n1p1`)**:
      - Clic derecho en `nvme0n1p1` $\rightarrow$ **Resize/Move**.
      - Arrastra el borde derecho ocupando todo el espacio libre no asignado (quedará de ~1.1 GB en total).
5. Haz clic en el botón verde de **Apply All Operations** (Aplicar todas las operaciones).
6. Deja que el proceso concluya sin desconectar la alimentación.

---

### Paso 3: Primer arranque en Windows
1. Retira la Live USB y reinicia directamente en **Windows**.
2. Windows puede mostrar un mensaje de análisis y reparación rápida de disco (`chkdsk`), es normal tras mover sectores NTFS.
3. Abre el Administrador de Discos en Windows para comprobar que la partición EFI ahora mide ~1 GB.
4. *(Opcional)* Si deseas volver a cifrar Windows, vuelve a activar BitLocker desde el panel de control.

---

### Paso 4: Ajustes finales en Omarchy / Arch Linux
1. Arranca en **Omarchy** (Linux).
2. Comprueba el nuevo tamaño con:
   ```bash
   df -h /efi
   ```
3. Ejecuta la actualización o reconstrucción de los kernels sin riesgo de espacio:
   ```bash
   sudo mkinitcpio -P
   ```
4. Todo el espacio adicional permitirá alojar kernels Surface, kernels estándar y UKIs sin ningún conflicto futuro.
