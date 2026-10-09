---
name: omarchy-backup
description: >-
  Back up all Omarchy configuration, Hyprland dotfiles, installed packages, and user settings to the omarchy-setup git repository and push to GitHub (@dagudelob/omarchy-setup).
  Use whenever the user asks to save, back up, sync, or push their Omarchy changes, desktop setup, or dotfiles, or triggers phrases like "guardar cambios", "backup omarchy", "guardar configuracion", "subir a github", "sync omarchy".
  Enforces automatic secret and credential scanning to prevent uploading private keys, tokens, or environment files.
---

# Omarchy Backup Skill

Safely backs up all user customizations made to Omarchy, Hyprland, terminals, shells, and package lists, audits staged files for sensitive data, and automatically synchronizes everything with the user's remote GitHub repository.

## Repositorio y Destino

- **Directorio local:** `/home/dagudelo/Code/omarchy-setup`
- **Repositorio remoto:** `https://github.com/dagudelob/omarchy-setup`
- **Rama principal:** `main`

## Workflow de Ejecución

Cuando el usuario pida guardar cambios, realizar un backup o sincronizar con GitHub:

### Paso 1: Ejecutar el script de respaldo automatizado
Ejecuta el script con el flag `--push` desde el directorio de trabajo del repositorio:

```bash
/home/dagudelo/Code/omarchy-setup/backup.sh --push
```

El script se encarga automáticamente de:
1. Exportar la lista actualizada de paquetes oficiales de Arch (`pkglist.txt`) y de AUR (`pkglist-aur.txt`).
2. Sincronizar las carpetas esenciales en `~/.config/`:
   - `hypr/` (atajos, monitores, reglas de ventana, look & feel)
   - `omarchy/` (shell.json, temas, extensiones, hooks)
   - Terminales (`kitty/`, `foot/`, `ghostty/`, `alacritty/`)
   - CLI y utilidades (`fastfetch/`, `btop/`, `lazygit/`, `starship.toml`, `tmux/`, etc.)
3. Sincronizar archivos de shell (`~/.bashrc`, `~/.bash_profile`).
4. Excluir automáticamente archivos temporales, logs, `.env` y llaves privadas.
5. Ejecutar un escaneo estricto de seguridad contra patrones de tokens de GitHub (`ghp_`, `gho_`) y llaves privadas antes de commitear.
6. Crear un commit con fecha/hora y subirlo a la rama `main` en GitHub.

### Paso 2: Verificar el estado de la sincronización
Si el comando anterior finalizó con éxito:
1. Revisa `git status` en `/home/dagudelo/Code/omarchy-setup` para confirmar que el árbol quedó limpio.
2. Informa al usuario:
   - Que los cambios fueron respaldados y verificados contra secretos.
   - La cantidad de archivos modificados o si no había cambios pendientes.
   - El enlace directo al repositorio: [https://github.com/dagudelob/omarchy-setup](https://github.com/dagudelob/omarchy-setup).

### Reglas Críticas de Seguridad
- **NUNCA** agregar archivos `.env`, credenciales de bases de datos, tokens de sesión o llaves de `~/.ssh/`.
- El archivo `.gitignore` del repositorio está activo para rechazar estos patrones.
- Si el script aborta por detección de un patrón sospechoso, muestra el archivo al usuario y pide confirmación antes de cualquier acción.
