# Diagnóstico y verificación del protector de pantalla (screensaver) en Omarchy

- **Date:** 2026-10-13 16:10:24
- **Branch:** `fix/screensaver-idle-diagnostics`
- **Type:** `fix`

---

## 1. Issue / Requirement
El usuario reportó que el protector de pantalla (*screensaver*) de Omarchy no parecía activarse automáticamente tras un período de inactividad.

## 2. Root Cause
El servicio de inactividad (`quickshell` / `omarchy-shell idle`) estaba activo y funcionando normalmente, pero requería 120 segundos (2 minutos) de inactividad continua sin pulsaciones de teclas ni movimiento de ratón para dispararse. Además, eventos de actividad previos o inhibidores de reproducción de medios resetean el contador.

## 3. Applied Solution
1. Se inspeccionaron las variables de estado e inhibidores de suspensión:
   - `omarchy-shell idle status` confirmó que el servicio estaba operativo (`enabled: true`, `screensaver: 120s`, `lock: 300s`).
   - Se revisaron los registros con `journalctl --user -b | grep -E "idle-cycle|screensaver"`, evidenciando ciclos previos activados exitosamente a los 120s y cancelados por actividad de entrada.
2. Se validaron los scripts del screensaver (`omarchy-launch-screensaver` y `omarchy-screensaver` con `ttfx` sobre terminal `foot`).
3. Se comprobó la ejecución manual forzada con `omarchy-launch-screensaver force` verificando el renderizado de animación en pantalla y posterior salida limpia.

## 4. Modified Files
- Ningún archivo modificado (diagnóstico y validación de comportamiento de sistema en `~/.config/omarchy/shell.json`).

## 5. Validation
- Se ejecutó `omarchy-launch-screensaver force` confirmando creación de ventana `org.omarchy.screensaver` en Hyprland ejecutando `ttfx`.
- Verificación de salida limpia tras recibir señal o input.
- Confirmación de operatividad por parte del usuario ("tema solucionado").
