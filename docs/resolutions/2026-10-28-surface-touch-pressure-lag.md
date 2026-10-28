# Calibración de presión y eliminación de latencia en touchscreen de Surface Pro

- **Date:** 2026-10-28
- **Branch:** `fix/surface-touch-pressure-lag`
- **Type:** `fix`

---

## 1. Issue / Requirement
En Microsoft Surface Pro (Linux / Hyprland), la pantalla táctil presentaba falta severa de respuesta: requería presionar con excesiva fuerza con los dedos para iniciar el desplazamiento hacia abajo y se trababa / cortaba a los 2 centímetros de recorrido.

## 2. Root Cause
1. **Umbrales de contacto excesivamente altos en `iptsd`:** `ActivationThreshold = 24` requería una presión anormal para que el detector de blobs registrara el dedo, y `DeactivationThreshold = 20` abortaba el contacto apenas la presión disminuía ligeramente durante el deslizamiento.
2. **Autosuspend PCI del bus Intel MEI (`0000:00:16.4`):** El controlador entraba en suspensión profunda tras 500 ms de inactividad (`autosuspend_delay_ms = 500`), introduciendo latencia de reactivación.

## 3. Applied Solution
1. Se desactivó el autosuspend agresivo de MEI en tiempo de ejecución:
   ```bash
   echo "on" | sudo tee /sys/bus/pci/devices/0000:00:16.4/power/control
   ```
2. Se configuró un perfil de contacto sensible y fluido en `/etc/iptsd.d/90-touch-sensitivity.conf`:
   ```ini
   [Contacts]
   ActivationThreshold = 8
   DeactivationThreshold = 5
   PositionThresholdMin = 0.01
   ```
3. Se reinició el servicio `iptsd@dev-hidraw1.service`.

## 4. Modified Files
- `/etc/iptsd.d/90-touch-sensitivity.conf`
- `/sys/bus/pci/devices/0000:00:16.4/power/control`

## 5. Validation
El usuario validó en vivo que la pantalla táctil responde de forma instantánea a toques y roces suaves naturales sin necesidad de ejercer fuerza, y el desplazamiento vertical hacia abajo y hacia arriba se ejecuta de manera continua y fluida sin congelarse ni trabarse.
