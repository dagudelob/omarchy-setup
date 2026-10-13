# Ajuste de espacios y bordes en ventanas Hyprland

- **Date:** 2026-10-13
- **Branch:** `feature/window-gaps-and-borders`
- **Type:** `feature`

---

## 1. Issue / Requirement
El usuario solicitó maximizar el área visible de las ventanas reduciendo los espacios alrededor de ellas (gaps) y adelgazando los bordes para una experiencia más cercana a pantallas completas estilo Windows.

## 2. Root Cause
Por defecto, Omarchy y Hyprland configuran `gaps_out = 10`, `gaps_in = 5` y `border_size = 2`, reservando márgenes considerables alrededor y entre cada ventana activa.

## 3. Applied Solution
Se configuraron las variables en `~/.config/hypr/looknfeel.lua`:
- `gaps_in = 0`: elimina el hueco entre ventanas adyacentes.
- `gaps_out = 1`: reduce el margen exterior con la pantalla/barra a solo 1px.
- `border_size = 1`: borde fino delimitador de 1px.
- Se recargó la configuración con `hyprctl reload`.

## 4. Modified Files
- `~/.config/hypr/looknfeel.lua`
- `config/hypr/looknfeel.lua`
- `docs/resolutions/2026-10-13-window-gaps-and-borders.md`

## 5. Validation
Verificado mediante `hyprctl reload && hyprctl configerrors`, confirmando recarga sin errores y visualización inmediata en el escritorio.
