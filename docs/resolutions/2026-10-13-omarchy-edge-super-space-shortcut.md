# Fix Super Space App Launcher Shortcut on Omarchy Edge Channel

- **Date:** 2026-10-13
- **Branch:** `fix/omarchy-edge-super-space-shortcut`
- **Type:** `fix`

---

## 1. Issue / Requirement
Al cambiar el canal de Omarchy a `edge` y actualizar el sistema, el atajo de teclado `Super + Space` dejó de abrir el menú de aplicaciones y el buscador del sistema.

## 2. Root Cause
La actualización de Omarchy introdujo una nueva arquitectura de atajos globales nativos (`GlobalShortcut` en Quickshell) gestionados directamente por Hyprland. Sin embargo, en el sistema seguía activo un directorio obsoleto de compatibilidad temporal (`~/.config/omarchy/shell_override/` y scripts en `~/.local/bin/`) originado por un bug anterior de Qt 6.12, el cual no implementaba estos manejadores de `GlobalShortcut`.

## 3. Applied Solution
1. Se eliminaron los ejecutables wrapper obsoletos de `~/.local/bin/` (`omarchy-launch-shell`, `omarchy-restart-shell`, `omarchy-shell`).
2. Se eliminó la copia heredada `~/.config/omarchy/shell_override/` para que el sistema utilice el shell oficial provisto en `/usr/share/omarchy/shell/`, que ya incluye soporte nativo y solución upstream para Qt 6.
3. Se reinició Quickshell mediante `omarchy restart shell` y se recargó la configuración de Hyprland con `hyprctl reload`.

## 4. Modified Files
- `~/.local/bin/omarchy-launch-shell` (eliminado)
- `~/.local/bin/omarchy-restart-shell` (eliminado)
- `~/.local/bin/omarchy-shell` (eliminado)
- `~/.config/omarchy/shell_override/` (árbol de anulación eliminado)

## 5. Validation
- Verificación del proceso activo ejecutando `/usr/share/omarchy/shell/shell.qml`.
- Comprobación de la respuesta IPC y toggle del menú con `omarchy-menu toggle`.
- Ejecución de `hyprctl reload` sin errores.
- Confirmación de apertura inmediata del menú interactivo con `Super + Space`.
