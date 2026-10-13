# Integración de Google Drive mediante Rclone y systemd user service

- **Date:** 2026-10-13
- **Branch:** `feature/google-drive-rclone-integration`
- **Type:** `feature`

---

## 1. Issue / Requirement
Integrar Google Drive en el sistema Omarchy/Arch Linux para acceder a los archivos directamente desde el explorador de archivos Nautilus y el sistema de archivos local de manera transparente y persistente.

## 2. Root Cause
El backend oficial `gvfs-google` (`gvfsd-google`) de GNOME Online Accounts quedó descontinuado en los repositorios de Arch Linux por obsolescencia de `libgdata`. Por tanto, agregar la cuenta de Google en GNOME Online Accounts no montaba la unidad en Nautilus.

## 3. Applied Solution
1. Se configuró un remoto `drive` en Rclone denominado `gdrive` mediante autenticación OAuth2 en el navegador.
2. Se creó el punto de montaje local `~/GoogleDrive`.
3. Se implementó y habilitó el servicio de usuario systemd `~/.config/systemd/user/rclone-gdrive.service` con soporte para VFS cache writes, reconexión y montaje automático al iniciar sesión.
4. Se añadió `Google Drive` a los marcadores GTK (`~/.config/gtk-3.0/bookmarks`) para acceso inmediato desde la barra lateral de Nautilus.

## 4. Modified Files
- `/home/dagudelo/.config/systemd/user/rclone-gdrive.service`
- `/home/dagudelo/.config/gtk-3.0/bookmarks`
- `/home/dagudelo/.config/rclone/rclone.conf` (no versionado por seguridad de credenciales)
- `/home/dagudelo/Code/omarchy-setup/docs/resolutions/2026-10-13-google-drive-rclone-integration.md`

## 5. Validation
- `systemctl --user status rclone-gdrive.service` reporta estado activo (`active (running)`).
- Listado exitoso de directorios en `~/GoogleDrive` mostrando las carpetas de la nube (`AI`, `Obsidian`, `Documents`, etc.).
- Comprobación del marcador directo en la interfaz de Nautilus.
