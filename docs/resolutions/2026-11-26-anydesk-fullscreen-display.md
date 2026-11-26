# AnyDesk Remote Display Scaling and Fullscreen

- **Date:** 2026-11-26
- **Branch:** `fix/anydesk-fullscreen-display`
- **Type:** `fix`

---

## 1. Issue / Requirement
La pantalla remota dentro de la sesión de AnyDesk se visualizaba excesivamente pequeña (sin escalar a la pantalla completa de alta resolución en Hyprland / Omarchy).

## 2. Root Cause
AnyDesk utiliza por defecto una escala de visualización 1:1 (Original). Al conectarse a resoluciones diferentes en pantallas de alta densidad (HiDPI), la imagen remota no se estira automáticamente ni se adapta al contenedor, y la ventana de Hyprland permanece en modo tiling por defecto.

## 3. Applied Solution
1. **Ajuste de escalado en AnyDesk:**
   - En la barra superior de herramientas de la sesión remota, acceder al menú **Display / Configuración de Pantalla** (ícono de monitor).
   - En **View Mode**, cambiar a **Adapt / Auto-adapt (Escalar/Estirar)**.
   - Alternar a pantalla completa dentro de la sesión (`F11` o botón de pantalla completa en la barra).
2. **Pantalla completa nativa en Hyprland:**
   - Utilizar el atajo de Hyprland (`Super + F`) para que la ventana de AnyDesk ocupe el monitor completo eliminando bordes y Waybar.
3. **Resolución remota:**
   - En caso de desfase severo, forzar desde el menú de AnyDesk la adaptación de resolución del equipo remoto a la del monitor local (2736x1824).

## 4. Modified Files
- Ninguno (configuración en tiempo de ejecución de AnyDesk y atajos de Hyprland).

## 5. Validation
El usuario confirmó la resolución satisfactoria con "tema solucionado", logrando visualización completa y ajustada de la pantalla remota.
