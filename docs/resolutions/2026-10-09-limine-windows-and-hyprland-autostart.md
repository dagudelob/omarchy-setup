# Dual boot Windows en Limine e inicio automatico de Hyprland con start-hyprland

- **Fecha:** 2026-10-09
- **Rama:** `fix/limine-windows-and-hyprland-autostart`
- **Tipo:** `fix`

---

## 1. Inconveniente / Requerimiento
Al encender la Surface, el bootloader Limine cargaba únicamente Arch Linux sin listar la opción de arranque de Windows. Además, Hyprland no iniciaba automáticamente al loguearse en TTY y mostraba una advertencia indicando que se ejecutaba sin `start-hyprland`.

## 2. Causa Raíz
1. La configuración `/boot/EFI/Boot/limine.conf` carecía de una entrada de chainload hacia el gestor EFI de Windows (`bootmgfw.efi`).
2. En `~/.bash_profile` no había autoinicio configurado para TTY1 y, al probar con `hyprland` directo, el binario requería ser invocado mediante el wrapper oficial `start-hyprland` en las versiones modernas de Hyprland.

## 3. Solución Aplicada
1. Se agregó la entrada `Windows Boot Manager` a `/boot/EFI/Boot/limine.conf` utilizando el protocolo `efi_chainload` hacia `boot():/EFI/Microsoft/Boot/bootmgfw.efi`.
2. Se configuró `~/.bash_profile` para detectar el inicio de sesión en TTY1 y ejecutar `start-hyprland`.

## 4. Archivos Modificados
- `/boot/EFI/Boot/limine.conf`
- `/home/dagudelo/.bash_profile`

## 5. Validación
- Se verificó que `/boot/EFI/Boot/limine.conf` cuenta con la sintaxis correcta de Limine para Windows y Arch.
- Se comprobó la existencia y permisos de `/usr/bin/start-hyprland`.
- Se confirmó que `~/.bash_profile` arranca limpiamente en TTY1 usando `exec start-hyprland` sin advertencias.
