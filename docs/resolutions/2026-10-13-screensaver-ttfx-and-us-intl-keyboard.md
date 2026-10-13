# Solución a error de salvapantallas ttfx y configuración definitiva de teclado US Internacional

- **Date:** 2026-10-13
- **Branch:** `fix/screensaver-ttfx-and-us-intl-keyboard`
- **Type:** `fix`

---

## 1. Issue / Requirement
1. Al entrar en estado de inactividad, se lanzaba una ventana en pantalla completa con el error recurrente `Error reading input file: No such file or directory (os error 2)`.
2. Mantener la distribución óptima de teclado en el Type Cover de la Surface Pro (`English US Internacional` con dead keys), conservando las teclas de puntuación originales (`;` y `:`) y permitiendo escribir tildes (`á`, `é`) y la `ñ` sin alterar la disposición física QWERTY.

## 2. Root Cause
1. El demonio de idle ejecutaba `omarchy-screensaver`, el cual invoca `ttfx -i ~/.config/omarchy/branding/screensaver.txt`. Dicho archivo ASCII no existía en el perfil del usuario, provocando que `ttfx` fallara en bucle.
2. Al intentar probar la distribución española estándar (`es`), la tecla `;` / `:` se reasignaba a `ñ`, rompiendo la concordancia con las teclas grabadas en el hardware físico de la Surface Type Cover.

## 3. Applied Solution
1. **Restauración del Screensaver:**
   - Se creó el directorio `~/.config/omarchy/branding/` y se copió el arte oficial desde `/usr/share/omarchy/logo.txt` hacia `~/.config/omarchy/branding/screensaver.txt`.
   - Se respaldó en el repositorio en `config/omarchy/branding/screensaver.txt`.
2. **Distribución de Teclado US Internacional:**
   - En `~/.config/hypr/input.lua`, se estableció la configuración definitiva:
     - `kb_layout = "us"`
     - `kb_variant = "intl"`
     - `kb_options = ""` (mantiene Caps Lock estándar).
   - Se sincronizó en `config/hypr/input.lua` dentro del repositorio.
3. Se recargó Hyprland con `hyprctl reload` y se reinició la barra con `omarchy restart shell`.

## 4. Modified Files
- `~/.config/omarchy/branding/screensaver.txt`
- `~/.config/hypr/input.lua`
- `config/omarchy/branding/screensaver.txt` (repositorio)
- `config/hypr/input.lua` (repositorio)
- `docs/resolutions/2026-10-13-screensaver-ttfx-and-us-intl-keyboard.md`

## 5. Validation
- Se ejecutó `ttfx -i ~/.config/omarchy/branding/screensaver.txt` confirmando que renderiza la animación fluida sin errores.
- Se verificó con `hyprctl -j devices` que el teclado activo reporta `English (US, intl., with dead keys)`.
- Se validó la concordancia de teclas:
  - Tecla física al lado de la `L` produce `;` y `:`.
  - Combinación `Shift + ~` seguida de `n` genera `ñ`.
  - Combinación `'` seguida de vocal genera acentos (`á`, `é`, `í`, `ó`, `ú`).
