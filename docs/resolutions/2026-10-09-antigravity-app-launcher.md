# Integrar Antigravity en el menú de aplicaciones de Omarchy

- **Fecha:** 2026-10-09
- **Rama:** `feature/antigravity-app-launcher`
- **Tipo:** `feature`

---

## 1. Inconveniente / Requerimiento
Antigravity y Antigravity IDE no aparecían en el menú de aplicaciones de Omarchy (`Super + Space` / `Super + Alt + Space`), obligando al usuario a abrir el explorador de archivos y buscar manualmente el ejecutable para abrir la aplicación.

## 2. Causa Raíz
Los binarios fueron descargados y descomprimidos manualmente en `~/Downloads/apps/`, sin entradas `.desktop` registradas en el directorio estándar XDG (`~/.local/share/applications/`), por lo que el lanzador de Omarchy no los indexaba.

## 3. Solución Aplicada
1. Se extrajeron y configuraron los iconos oficiales en `~/.local/share/icons/` (`antigravity.png` y `antigravity-ide.png`).
2. Se crearon los archivos de escritorio XDG en `~/.local/share/applications/`:
   - `antigravity.desktop` vinculando el ejecutable `~/Downloads/apps/Antigravity/Antigravity-x64/antigravity`.
   - `antigravity-ide.desktop` vinculando el ejecutable `~/Downloads/apps/Antigravity IDE/antigravity-ide`.
3. Se otorgaron permisos de ejecución a los accesos directos y se actualizaron las bases de datos del sistema mediante `update-desktop-database ~/.local/share/applications` y `omarchy menu refresh`.

## 4. Archivos Modificados
- `/home/dagudelo/.local/share/applications/antigravity.desktop`
- `/home/dagudelo/.local/share/applications/antigravity-ide.desktop`
- `/home/dagudelo/.local/share/icons/antigravity.png`
- `/home/dagudelo/.local/share/icons/antigravity-ide.png`

## 5. Validación
- Se verificó la presencia y formato de los archivos `.desktop` con permisos ejecutables.
- Se ejecutó `update-desktop-database` y `omarchy menu refresh` con retorno exitoso (`ok`).
- Las aplicaciones quedan indexadas y ejecutables directamente mediante `Super + Space`.
