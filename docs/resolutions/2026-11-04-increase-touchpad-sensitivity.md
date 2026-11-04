# Aumentar sensibilidad del touchpad en Hyprland

- **Date:** 2026-11-04
- **Branch:** `feature/increase-touchpad-sensitivity`
- **Type:** `feature`

---

## 1. Issue / Requirement
El touchpad tenía la sensibilidad por defecto en Hyprland (`0.0`), lo cual resultaba lento y poco reactivo para la navegación en la Surface Pro.

## 2. Root Cause
En la configuración de entrada de Hyprland (`~/.config/hypr/input.lua`), el parámetro `sensitivity` se encontraba en el valor predeterminado del sistema (`0.0` dentro del rango de `-1.0` a `1.0`).

## 3. Applied Solution
1. Se editó `~/.config/hypr/input.lua` para añadir la propiedad `sensitivity = 0.5` dentro del bloque `hl.config({ input = { ... } })`.
2. Se aplicó y recargó la configuración inmediatamente con `hyprctl reload`.
3. Se sincronizó el archivo actualizado en el repositorio `config/hypr/input.lua`.

## 4. Modified Files
- `/home/dagudelo/.config/hypr/input.lua`
- `/home/dagudelo/Code/omarchy-setup/config/hypr/input.lua`
- `/home/dagudelo/Code/omarchy-setup/docs/resolutions/2026-11-04-increase-touchpad-sensitivity.md`

## 5. Validation
- Verificación con `hyprctl getoption input:sensitivity` retornando `float: 0.500000`.
- Confirmación del usuario indicando que el movimiento del touchpad quedó en el nivel deseado.
