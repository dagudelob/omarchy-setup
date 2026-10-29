# Sincronización solar del modo nocturno con el amanecer y atardecer de Toronto

- **Date:** 2026-10-28
- **Branch:** `feature/toronto-nightlight-solar-sync`
- **Type:** `feature`

---

## 1. Issue / Requirement
El usuario solicitó que el modo nocturno (filtro de luz azul / Night Light) de Omarchy se active y desactive dinámicamente según la hora exacta de salida y puesta de sol (sunrise/sunset) de Toronto, adaptándose a las estaciones del año.

## 2. Root Cause
Omarchy utiliza `hyprsunset` con perfiles estáticos basados en horas fijas en `~/.config/hypr/hyprsunset.conf` (por defecto a las 20:00). No incluía sincronización astronómica para actualizar estos horarios de acuerdo a la ubicación del usuario.

## 3. Applied Solution
1. **Script de cálculo solar:** Creado `~/.local/bin/update-hyprsunset-toronto` usando las ecuaciones solares estándar de la NOAA (lat 43.6532, lon -79.3832) para calcular local y offline los horarios solares, configurando `temperature = 3800` para el atardecer y `identity = true` para el amanecer.
2. **Arranque en Hyprland:** Se añadió `o.launch_on_start("hyprsunset")` en `~/.config/hypr/autostart.lua`.
3. **Automatización diaria:** Se configuraron el servicio y temporizador de systemd de usuario (`hyprsunset-toronto.service` y `hyprsunset-toronto.timer`) para ejecutarse diariamente a las 03:00 AM.
4. **Verificación inmediata:** Se ejecutó el script y se verificó el estado activo con temperatura cálida a 3800K.

## 4. Modified Files
- `~/.local/bin/update-hyprsunset-toronto`
- `~/.config/hypr/hyprsunset.conf`
- `~/.config/hypr/autostart.lua`
- `~/.config/systemd/user/hyprsunset-toronto.service`
- `~/.config/systemd/user/hyprsunset-toronto.timer`
- `config/hypr/hyprsunset.conf`
- `config/hypr/autostart.lua`
- `config/systemd/user/hyprsunset-toronto.service`
- `config/systemd/user/hyprsunset-toronto.timer`
- `bin/update-hyprsunset-toronto`
- `docs/resolutions/2026-10-28-toronto-nightlight-solar-sync.md`

## 5. Validation
- `systemctl --user list-timers hyprsunset-toronto.timer` activo y programado.
- `omarchy toggle nightlight --status` retornó `{"enabled":true,"temperature":3800}`.
- `hyprctl reload` ejecutado sin errores de configuración.
