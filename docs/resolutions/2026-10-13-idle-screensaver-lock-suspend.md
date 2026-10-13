# Configuración de salvapantallas (2min), bloqueo/apagado de pantalla (5min) y suspensión (15min)

- **Date:** 2026-10-13
- **Branch:** `feature/idle-screensaver-lock-suspend`
- **Type:** `feature`

---

## 1. Issue / Requirement
Configurar la gestión de inactividad de Omarchy para que tras 2 minutos se active el screensaver, a los 5 minutos se bloquee la sesión apagando la pantalla, y a los 15 minutos de inactividad total el equipo entre en suspensión de forma automática.

## 2. Root Cause
Omarchy gestiona nativamente los tiempos de screensaver y bloqueo mediante el daemon Quickshell en `shell.json`, pero la hibernación no estaba habilitada en el sistema (swap en zRAM sin swap persistente ni hooks de arranque) y no existía un temporizador predeterminado para suspender tras inactividad prolongada.

## 3. Applied Solution
1. Se ajustaron los parámetros de inactividad en `~/.config/omarchy/shell.json`:
   - `idle.screensaver`: `120` (2 minutos).
   - `idle.lock`: `300` (5 minutos, que además apaga la pantalla vía DPMS).
2. Se implementó el script ejecutable `~/.local/bin/omarchy-idle-suspend` que monitorea el estado de bloqueo respetando el indicador *Stay Awake* y ejecuta `systemctl suspend` tras 10 minutos de pantalla bloqueada (15 minutos totales de inactividad).
3. Se creó y habilitó el servicio systemd de usuario `omarchy-idle-suspend.service` integrado en la sesión gráfica.

## 4. Modified Files
- `~/.config/omarchy/shell.json`
- `~/.local/bin/omarchy-idle-suspend`
- `~/.config/systemd/user/omarchy-idle-suspend.service`

## 5. Validation
- Verificación de recarga en tiempo real de `omarchy-shell idle status` confirmando `screensaver: 120` y `lock: 300`.
- Verificación del estado activo y en ejecución de `omarchy-idle-suspend.service` mediante `systemctl --user status`.
