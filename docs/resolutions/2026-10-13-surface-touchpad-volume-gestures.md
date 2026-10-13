# Configuración de gestos touchpad para volumen y escritorios en Surface

- **Date:** 2026-10-13
- **Branch:** `feature/surface-touchpad-volume-gestures`
- **Type:** `feature`

---

## 1. Issue / Requirement
Habilitar gestos multitáctiles en el touchpad de la Microsoft Surface Type Cover bajo Hyprland/Omarchy:
- Cambiar de escritorios/workspaces con 4 dedos horizontalmente.
- Subir y bajar volumen con deslizamiento de 4 dedos verticalmente (arriba/abajo) manteniendo el cuadro visual OSD de Omarchy en pantalla.

## 2. Root Cause
Hyprland soporta gestos nativos de touchpad mediante su API `hl.gesture` en Lua, pero por defecto únicamente venía configurado el cambio de workspace con 3 dedos. Los scripts de volumen (`omarchy-audio-output-volume`) gestionan internamente el paso de volumen en PipeWire/PulseAudio y lanzan el OSD visual de Omarchy.

## 3. Applied Solution
1. Se añadieron las reglas nativas en `~/.config/hypr/input.lua`:
   - `hl.gesture({ fingers = 4, direction = "horizontal", action = "workspace" })` para cambio de escritorios.
   - `hl.gesture({ fingers = 4, direction = "up", action = function() hl.exec_cmd("omarchy-audio-output-volume raise") end })` para subir volumen con OSD.
   - `hl.gesture({ fingers = 4, direction = "down", action = function() hl.exec_cmd("omarchy-audio-output-volume lower") end })` para bajar volumen con OSD.
2. Se mantuvo la compatibilidad con el gesto de 3 dedos para workspaces.
3. Se recargó la configuración de Hyprland con `hyprctl reload` sin errores.

## 4. Modified Files
- `/home/dagudelo/.config/hypr/input.lua`

## 5. Validation
- Verificación de sintaxis con `hyprctl configerrors` reportando `ok`.
- Prueba en vivo del touchpad ejecutando `omarchy-audio-output-volume raise` y `lower`, verificando la visualización correcta de la caja flotante OSD (`omarchy-osd`) con porcentaje y barra animada.
