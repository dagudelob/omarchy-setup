# Habilitar Alt + F4 para cerrar ventanas en Hyprland

- **Date:** 2026-10-16 11:24:27
- **Branch:** `feature/alt-f4-close-window`
- **Type:** `feature`

---

## 1. Issue / Requirement
Se solicitó verificar si el atajo `Alt + F4` estaba siendo utilizado en el sistema y, al comprobarse que no lo estaba, habilitarlo como combinación estándar para cerrar ventanas activas.

## 2. Root Cause
En Omarchy/Hyprland el atajo predeterminado para cerrar ventanas es `SUPER + W` (`hl.dsp.window.close()`). La combinación tradicional `Alt + F4` no venía asignada por defecto ni por ninguna otra aplicación.

## 3. Applied Solution
Se agregó la regla de keybinding en la configuración de usuario de Hyprland (`~/.config/hypr/bindings.lua`):
```lua
-- Cerrar ventana con Alt + F4
o.bind("ALT + F4", "Close window", hl.dsp.window.close())
```
Posteriormente se recargó la configuración con `hyprctl reload` y se sincronizó con el repositorio.

## 4. Modified Files
- `/home/dagudelo/.config/hypr/bindings.lua`
- `config/hypr/bindings.lua`
- `docs/resolutions/2026-10-16-alt-f4-close-window.md`

## 5. Validation
1. Ejecución de `hyprctl reload` y `hyprctl configerrors` reportando estado limpio (`ok`).
2. Comprobación en `hyprctl binds` verificando la captura de la tecla `F4` con modificador `8` (Alt) y despachador de cierre de ventana.
3. Verificación en `omarchy menu keybindings --print` mostrando `ALT + F4 → Close window`.
