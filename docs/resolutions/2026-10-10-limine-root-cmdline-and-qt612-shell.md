# Fix Limine root cmdline and Qt 6.12 Omarchy shell invisibility

- **Date:** 2026-10-10
- **Branch:** `fix/limine-root-cmdline-and-qt612-shell`
- **Type:** `fix`

---

## 1. Issue / Requirement
1. Tras reiniciar el sistema, Limine detenía el arranque obligando a ingresar manualmente `root=/dev/nvme0n1p5 rw` con `Ctrl+X`.
2. La barra superior (`omarchy-bar`) era invisible y al presionar `Super + Space` la pantalla se ponía en blanco sin mostrar el menú de aplicaciones.
3. Se generó un error de sintaxis en `~/.config/hypr/autostart.lua` reportando `attempt to call a nil value (field 'spawn')`.

## 2. Root Cause
1. `/efi/limine.conf` no tenía definido el parámetro `root=...` para el kernel `linux-surface`, ya que `/etc/limine-entry-tool.d/omarchy-defaults.conf` solo usaba `+=` con banderas secundarias.
2. La actualización a `qt6-declarative 6.12.0` introdujo un singleton interno nativo en QtQuick llamado `Color` (`QQuickColor`), el cual colisionaba con el singleton `Color.qml` de Omarchy, causando que todas las llamadas de estilo (`Color.bar.*`, `Color.menu.*`) devolvieran `undefined`.
3. En Hyprland con backend Lua, la función de autostart es `hl.exec_cmd(...)` y no `o.spawn(...)`.

## 3. Applied Solution
1. **Limine:** Configurado `/etc/limine-entry-tool.d/00-root.conf` con `KERNEL_CMDLINE[default]="root=PARTUUID=087e8082-4f40-49be-bfc8-195af01c64f7 rw rootfstype=ext4"` y actualizado con `limine-update`.
2. **Omarchy Shell / Qt 6.12:** Se creó una copia corregida en `~/.config/omarchy/shell_override/` renombrando el singleton a `OmaColor`, se ajustaron los componentes del shell y se envolvieron los ejecutables `omarchy-launch-shell`, `omarchy-restart-shell` y `omarchy-shell` en `~/.local/bin/`.
3. **Hyprland:** Se corrigió `~/.config/hypr/autostart.lua` y se priorizó `~/.local/bin` en el `PATH` dentro de `~/.config/hypr/hyprland.lua`.

## 4. Modified Files
- `/etc/limine-entry-tool.d/00-root.conf`
- `/efi/limine.conf`
- `~/.config/hypr/autostart.lua`
- `~/.config/hypr/hyprland.lua`
- `~/.config/omarchy/shell_override/` (árbol de shell con `OmaColor`)
- `~/.local/bin/omarchy-launch-shell`
- `~/.local/bin/omarchy-restart-shell`
- `~/.local/bin/omarchy-shell`

## 5. Validation
- Verificación con `hyprctl configerrors` (sin errores).
- Capturas de pantalla confirmando barra superior visible y operativa con iconos de reloj, estado, bandeja y workspaces.
- Apertura correcta del menú interactivo con `Super + Space` (`omarchy-menu toggle`).
- Configuración persistente de arranque generada por `limine-update`.
