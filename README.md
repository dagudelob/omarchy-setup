# Omarchy Setup & Backup (`dagudelo`)

Copia de seguridad y configuración personalizada de **Omarchy** (Hyprland, temas, atajos, shell y paquetes del sistema).

## Contenido

- `config/`: Configuraciones de usuario en `~/.config/`:
  - `hypr/`: Monitores, reglas de ventanas, bindings y apariencia de Hyprland.
  - `omarchy/`: Ajustes de barra/shell, extensiones, temas y hooks de Omarchy.
  - `kitty/`, `foot/`, `ghostty/`, `alacritty/`: Terminales configuradas.
  - `fastfetch/`, `btop/`, `lazygit/`, `starship.toml`: Utilidades y CLI.
- `shell/`: Archivos `.bashrc`, `.bash_profile`, etc.
- `pkglist.txt`: Lista de todos los paquetes oficiales de Arch instalados explícitamente.
- `pkglist-aur.txt`: Lista de paquetes de AUR instalados.

## Uso

### 1. Hacer una copia de seguridad actualizada
```bash
./backup.sh
```

### 2. Restaurar tu configuración en un sistema nuevo o restaurar cambios
```bash
./restore.sh
```

### 3. Reinstalar paquetes en un sistema nuevo (opcional)
```bash
# Paquetes oficiales:
sudo pacman -S --needed - < pkglist.txt

# Paquetes AUR (con yay):
yay -S --needed - < pkglist-aur.txt
```
