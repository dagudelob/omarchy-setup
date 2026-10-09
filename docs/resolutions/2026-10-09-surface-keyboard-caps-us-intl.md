# Solucion Teclado Surface: CapsLock Tradicional y US Internacional (Dead Keys)

- **Fecha:** 2026-10-09
- **Rama:** `fix/surface-keyboard-caps-us-intl`
- **Tipo:** `fix`

---

## 1. Inconveniente / Requerimiento
1. Al presionar `Caps Lock`, salía un punto con tilde (`í`) o menú compose en lugar de activar el bloqueo de mayúsculas estándar.
2. Imposibilidad de generar la letra `ñ` combinando `~` + `n`, y acentos mediante `'` + vocal (comportamiento idéntico a Windows en teclados US-Internacional).

## 2. Causa Raíz
- Omarchy incluye por defecto en Hyprland la opción `compose:caps`, que reasigna la tecla CapsLock como tecla *Compose* para secuencias y emojis.
- La distribución predeterminada era `us` estándar (sin teclas muertas / *dead keys*), y la variante `altgr-intl` enviaba la tilde `~` como tercer nivel a AltGr mientras producía ordinales (`ª`) al presionar la tecla directa.

## 3. Solución Aplicada
1. En `~/.config/hypr/input.lua`, se configuró:
   - `kb_layout = "us"`
   - `kb_variant = "intl"` (English US International with dead keys)
   - `kb_options = ""` (se retiró `compose:caps` para restaurar CapsLock clásico).
2. En `~/.config/hypr/bindings.lua`, se añadió el atajo de cambio rápido:
   - `Super + Alt + K` para cambiar de distribución (`hyprctl switchxkblayout all next`).
3. Se recargó la configuración en caliente con `hyprctl reload`.

## 4. Archivos Modificados
- `~/.config/hypr/input.lua`
- `~/.config/hypr/bindings.lua`
- `dotfiles/hypr/input.lua` (respaldado en repositorio)
- `dotfiles/hypr/bindings.lua` (respaldado en repositorio)

## 5. Validación
- `hyprctl devices` confirmó la regla activa: `l "us", v "intl"`.
- `CapsLock` activa y desactiva mayúsculas correctamente.
- Secuencias `Shift + ~` luego `n` generan `ñ` y `Ñ`.
- Secuencia `'` luego `a`, `e`, `i`, `o`, `u` genera las vocales con tilde (`á`, `é`, `í`, `ó`, `ú`).
