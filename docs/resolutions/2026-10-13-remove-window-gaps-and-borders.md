# Eliminar espacios entre ventanas y bordes en Hyprland

- **Date:** 2026-10-13
- **Branch:** `feature/remove-window-gaps-and-borders`
- **Type:** `feature`

---

## 1. Issue / Requirement
El usuario solicitó que las aplicaciones ocuparan el 100% del espacio de la pantalla sin bordes ni espacios entre ventanas, conservando la barra superior visible (sin utilizar pantalla completa completa / fullscreen exclusivo que oculta la barra).

## 2. Root Cause
Omarchy/Hyprland define por defecto un margen exterior (`gaps_out = 10`), margen entre ventanas (`gaps_in = 5`) y grosor de bordes (`border_size = 2`), dejando separación visible entre las aplicaciones.

## 3. Applied Solution
Se configuraron a 0 las variables de gaps y bordes en el archivo de apariencia de Hyprland:
- `gaps_in = 0`
- `gaps_out = 0`
- `border_size = 0`

Se recargó la configuración inmediatamente con `hyprctl reload`.

## 4. Modified Files
- `/home/dagudelo/.config/hypr/looknfeel.lua`
- `/home/dagudelo/Code/omarchy-setup/config/hypr/looknfeel.lua`
- `/home/dagudelo/Code/omarchy-setup/docs/resolutions/2026-10-13-remove-window-gaps-and-borders.md`

## 5. Validation
Se validó con:
- `hyprctl reload && hyprctl configerrors` (sin errores reportados).
- `hyprctl getoption general:gaps_in` (`0 0 0 0`).
- `hyprctl getoption general:gaps_out` (`0 0 0 0`).
- `hyprctl getoption general:border_size` (`0`).
