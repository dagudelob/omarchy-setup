# Fix AnyDesk UI scaling and fullscreen on Wayland

- **Date:** 2026-10-31
- **Branch:** `fix/anydesk-fullscreen`
- **Type:** `fix`

---

## 1. Issue / Requirement
AnyDesk no permitía redimensionar correctamente la ventana de sesión remota ni poner pantalla completa. El escritorio remoto se mostraba en una caja pequeña y centrada con bordes grises desaprovechando la pantalla.

## 2. Root Cause
Conflicto entre AnyDesk (basado en GTK3 / XWayland) y el entorno Wayland/Hyprland con escalado fraccional HiDPI. AnyDesk calculaba erróneamente el tamaño del framebuffer y el canvas de streaming al no forzar el backend de renderizado X11.

## 3. Applied Solution
1. Se verificó que ejecutar AnyDesk con `GDK_BACKEND=x11 anydesk` resuelve el renderizado, permitiendo que la ventana escale fluidamente y tome pantalla completa.
2. Se copió el archivo de escritorio a `~/.local/share/applications/anydesk.desktop` y se actualizó la directiva `Exec` a `env GDK_BACKEND=x11 /usr/bin/anydesk %u`.
3. Esto garantiza que al abrir AnyDesk desde el lanzador de aplicaciones (`Super + Space`), arranque de forma nativa bajo X11 sin bordes grises.

## 4. Modified Files
- `/home/dagudelo/.local/share/applications/anydesk.desktop`

## 5. Validation
- El usuario confirmó que la ejecución con `GDK_BACKEND=x11` funciona perfectamente permitiendo redimensionar y ver la sesión en pantalla completa.
- Se actualizó la base de datos de escritorios (`update-desktop-database`) para que el lanzador (`Super + Space`) invoque directamente el wrapper con X11.
