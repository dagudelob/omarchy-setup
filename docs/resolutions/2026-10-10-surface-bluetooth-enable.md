# Enable and configure Bluetooth service on Surface Pro

- **Date:** 2026-10-10
- **Branch:** `fix/surface-bluetooth-enable`
- **Type:** `fix`

---

## 1. Issue / Requirement
El adaptador Bluetooth en el Surface Pro no estaba disponible o no iniciaba automáticamente con el sistema, impidiendo conectar periféricos y dispositivos inalámbricos.

## 2. Root Cause
El servicio del demonio `bluetooth.service` de `bluez` venía deshabilitado de forma predeterminada tras la instalación del sistema en Arch Linux, dejando el controlador `hci0` inactivo.

## 3. Applied Solution
1. Verificación del controlador Bluetooth con `rfkill` asegurando que no tuviera bloqueo físico o por software (`unblocked`).
2. Activación e inicio del servicio del sistema con arranque automático:
   ```bash
   sudo systemctl enable --now bluetooth.service
   ```
3. Validación del estado del controlador en `bluetoothctl show` confirmando estado `Powered: yes` y registro de endpoints de audio.

## 4. Modified Files
- `/usr/lib/systemd/system/bluetooth.service` (habilitado e iniciado a través de systemd).

## 5. Validation
- Se ejecutó `systemctl status bluetooth` confirmando estado `active (running)`.
- Se verificó con `rfkill list bluetooth` y `bluetoothctl show` comprobando el controlador `hci0` en funcionamiento y disponible para emparejamiento.
