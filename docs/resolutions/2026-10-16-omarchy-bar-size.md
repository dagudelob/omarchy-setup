# Ajuste de tamaño y escala de Omarchy Bar Shell

- **Date:** 2026-10-16
- **Branch:** `feature/omarchy-bar-size`
- **Type:** `feature`

---

## 1. Issue / Requirement
Identificar el nombre de la barra de estado del sistema (Omarchy Shell en Quickshell) y ajustar su escala/tamaño visual para mejorar la legibilidad y dimensiones a solicitud del usuario.

## 2. Root Cause
La barra forma parte de `omarchy-shell` y obtiene su escala proporcional del valor base configurado en `[font] base-size` dentro de `~/.config/omarchy/shell.toml` (o con tokens `[bar] size-horizontal`). El archivo `shell.toml` no existía por defecto a nivel de usuario.

## 3. Applied Solution
1. Se creó el archivo `~/.config/omarchy/shell.toml` definiendo `[font] base-size = 15`.
2. Se sincronizó el archivo hacia el repositorio en `dotfiles/omarchy/shell.toml`.
3. Se recargó el entorno ejecutando `omarchy restart shell`.

## 4. Modified Files
- `/home/dagudelo/.config/omarchy/shell.toml`
- `/home/dagudelo/Code/omarchy-setup/dotfiles/omarchy/shell.toml`
- `/home/dagudelo/Code/omarchy-setup/docs/resolutions/2026-10-16-omarchy-bar-size.md`

## 5. Validation
Se ejecutó `omarchy restart shell` de manera exitosa sin errores de sintaxis y se comprobó la correcta renderización y reescalado de la barra en pantalla.
