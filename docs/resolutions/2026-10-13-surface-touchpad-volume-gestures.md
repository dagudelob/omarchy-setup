# Gestos Fluidos y Proporcionales de Touchpad para Volumen y Escritorios en Surface

- **Date:** 2026-10-13
- **Branch:** `feature/surface-touchpad-volume-gestures`
- **Type:** `feature`

---

## 1. Issue / Requirement
Habilitar una experiencia de gestos multitáctiles en el touchpad de la Microsoft Surface Type Cover bajo Hyprland/Omarchy con dinámica estilo Windows Precision Touchpad / macOS:
- Control de volumen continuo y proporcional 1:1 al desplazamiento real de 4 dedos verticalmente (subir/bajar volumen con inercia y suavidad), en lugar de saltos estáticos discretos.
- Cambio de escritorios/workspaces con 4 dedos horizontalmente de manera nativa e instantánea.

## 2. Root Cause
Hyprland por defecto solo maneja gestos estáticos de umbral por acción (un único trigger discreto al final del recorrido del swipe). Para lograr que el volumen aumente o disminuya en tiempo real de acuerdo a la distancia exacta recorrida por los dedos en la superficie del touchpad, se requiere procesar los eventos continuos `GESTURE_SWIPE_UPDATE` de libinput a nivel de sistema.

## 3. Applied Solution
1. **Permisos y herramientas de entrada:**
   - Adición del usuario al grupo `input` del sistema para acceso a lectura de eventos del touchpad.
   - Instalación de `libinput-tools` mediante `omarchy pkg add`.
2. **Daemon continuo de gestos multitáctiles:**
   - Creación de `~/.config/omarchy/scripts/surface-touchpad-gestures.py` que lee el flujo de `libinput debug-events` en tiempo real.
   - Traduce los deltas continuos de desplazamiento (`dy`) directamente en porcentaje de volumen proporcional con inercia física suave.
3. **Servicio persistente:**
   - Configuración y habilitación del servicio de usuario systemd `~/.config/systemd/user/surface-touchpad-gestures.service`.
4. **Integración con Hyprland:**
   - En `~/.config/hypr/input.lua` se mantiene la navegación horizontal nativa de workspaces para 3 y 4 dedos (`hl.gesture({ fingers = 4, direction = "horizontal", action = "workspace" })`), dejando la dimensión vertical liberada para el controlador de volumen continuo.

## 4. Modified Files
- `/home/dagudelo/.config/hypr/input.lua`
- `/home/dagudelo/.config/omarchy/scripts/surface-touchpad-gestures.py`
- `/home/dagudelo/.config/systemd/user/surface-touchpad-gestures.service`

## 5. Validation
- Verificación del estado del servicio `surface-touchpad-gestures.service` activo y ejecutándose en segundo plano (`active (running)`).
- Validación de sintaxis de Hyprland con `hyprctl reload` reportando `ok`.
- Prueba física confirmada por el usuario: el volumen responde de manera proporcional, fluida y precisa al movimiento vertical de 4 dedos en el teclado de la Surface.
