# Omarchy Setup & Backup (`dagudelo`)

Backup and custom configuration for **Omarchy** (Hyprland, themes, keybindings, shell, and system packages).

## Contents

- `config/`: User configurations stored in `~/.config/`:
  - `hypr/`: Monitors, window rules, keybindings, and Hyprland appearance.
  - `omarchy/`: Status bar/shell settings, extensions, themes, and Omarchy hooks.
  - `kitty/`, `foot/`, `ghostty/`, `alacritty/`: Configured terminal emulators.
  - `fastfetch/`, `btop/`, `lazygit/`, `starship.toml`: CLI tools and utilities.
- `shell/`: Shell configuration files (`.bashrc`, `.bash_profile`, `.zshrc`, etc.).
- `pkglist.txt`: List of explicitly installed official Arch Linux packages.
- `pkglist-aur.txt`: List of installed AUR packages.

## Usage

### 1. Perform an updated backup
```bash
./backup.sh
```
Or backup and push directly to GitHub:
```bash
./backup.sh --push
```

### 2. Restore configuration on a new system or rollback changes
```bash
./restore.sh
```

### 3. Reinstall packages on a new system (optional)
```bash
# Official packages:
sudo pacman -S --needed - < pkglist.txt

# AUR packages (with yay):
yay -S --needed - < pkglist-aur.txt
```
