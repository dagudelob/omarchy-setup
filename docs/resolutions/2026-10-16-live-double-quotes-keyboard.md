# Teclas muertas con comillas dobles vivas en teclado US Intl

- **Date:** 2026-10-16
- **Branch:** `feature/live-double-quotes-keyboard`
- **Type:** `feature`

---

## 1. Issue / Requirement
Configurar el teclado en Hyprland para mantener teclas muertas (tildes `á`, diéresis con AltGr, eñes `ñ`), pero permitiendo que las comillas dobles `"` (Shift + `'`) sean teclas "vivas", insertándose de inmediato sin requerir pulsar espacio ni esperar la siguiente tecla.

## 2. Root Cause
En la variante estándar `us(intl)` (US Internacional), la tecla física `<AC11>` tiene asignado `dead_diaeresis` en el nivel Shift (`Shift` + `'`), lo que provoca que las comillas dobles funcionen como tecla muerta esperando una vocal.

## 3. Applied Solution
1. Se creó un archivo de símbolos XKB de usuario en `~/.config/xkb/symbols/us` con la variante `intl-livequote`, heredando de `us(intl)` y reasignando `<AC11>` a `[ dead_acute, quotedbl, apostrophe, dead_diaeresis ]`.
2. Se actualizó la configuración de Hyprland en `~/.config/hypr/input.lua` configurando `kb_variant = "intl-livequote"`.
3. Se aplicó dinámicamente a la sesión activa mediante `hyprctl eval`.

## 4. Modified Files
- `/home/dagudelo/.config/xkb/symbols/us`
- `/home/dagudelo/.config/hypr/input.lua`

## 5. Validation
- Verificado con `xkbcli compile-keymap --layout us --variant intl-livequote`.
- Aplicado en vivo con `hyprctl getoption input:kb_variant` confirmando el uso de `intl-livequote`.
- Confirmado por el usuario con respuesta directa y satisfacción.
