# Recuperación y estabilización de BitLocker al arrancar Windows desde Limine

- **Fecha:** 2026-10-09
- **Rama:** `fix/bitlocker-limine-boot`
- **Tipo:** `fix`

---

## 1. Inconveniente / Requerimiento
Al seleccionar Windows Boot Manager desde el gestor de arranque Limine (Luminer) en un entorno de dual boot, Windows solicitaba la clave de recuperación de BitLocker de 48 dígitos antes de permitir el inicio de sesión.

## 2. Causa Raíz
La modificación de la cadena de arranque UEFI al introducir Limine alteró las mediciones de los registros PCR del chip TPM. Al detectar una discrepancia en la secuencia de arranque segura, BitLocker bloqueó el acceso al volumen cifrado por medidas de seguridad.

## 3. Solución Aplicada
1. Obtención de la clave de recuperación numérica de 48 dígitos a través de la cuenta de Microsoft vinculada (`https://account.microsoft.com/devices/recoverykey`).
2. Desbloqueo inicial del volumen introduciendo la clave en la pantalla de recuperación de Windows.
3. Actualización de las mediciones de los protectores TPM en Windows ejecutando PowerShell / CMD como Administrador:
   - Suspensión temporal de los protectores:
     ```cmd
     manage-bde -protectors -disable C:
     ```
   - Reinicio a través de Limine y reactivación de los protectores para registrar el nuevo estado de arranque:
     ```cmd
     manage-bde -protectors -enable C:
     ```

## 4. Archivos Modificados
- `docs/resolutions/2026-10-09-bitlocker-limine-boot.md`

## 5. Validación
El usuario confirmó inicio correcto de Windows sin bloqueo y funcionamiento estable desde Limine ("tema solucionado").
