# Fix Bluetooth AirPods Disconnect After Pairing

- **Date:** 2026-11-04
- **Branch:** `fix/bluetooth-airpods-disconnect`
- **Type:** `fix`

---

## 1. Issue / Requirement
Los audífonos (AirPods Pro) se conectaban al sistema pero se desconectaban inmediatamente tras 2 segundos. El usuario tenía que olvidar el dispositivo y reintentar repetidamente sin lograr una conexión estable.

## 2. Root Cause
BlueZ operaba en modo dual por defecto (`ControllerMode = dual`). Al emparejar con beacons BLE de Apple, los perfiles de audio (A2DP/HFP) fallaban con `Permission denied (13)` y `Connection refused (111)` porque el enlace no se consolidaba (`Paired: no`, `Bonded: no`), provocando la desconexión inmediata por falta de claves de cifrado válidas.

## 3. Applied Solution
1. Se ajustó `/etc/bluetooth/main.conf` bajo `[General]` con las directivas:
   - `ControllerMode = bredr` (fuerza transporte clásico BR/EDR para perfiles de audio estables).
   - `FastConnectable = true`
   - `JustWorksRepairing = always`
2. Se reinició el servicio `bluetooth.service`.
3. Se limpió el dispositivo residual con `bluetoothctl remove CC:22:FE:2B:6A:6F`.
4. Se puso el estuche en modo de emparejamiento físico (luz blanca) y se ejecutó un handshake completo (`pair`, `trust`, `connect`).

## 4. Modified Files
- `/etc/bluetooth/main.conf`

## 5. Validation
- Verificación con `bluetoothctl info CC:22:FE:2B:6A:6F`:
  - `Paired: yes`
  - `Bonded: yes`
  - `Trusted: yes`
  - `Connected: yes`
- Verificación con `wpctl status`: sink asignado activamente a `* AirPods Pro` sin cortes de conexión.
