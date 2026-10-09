#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$REPO_DIR/config"
SHELL_DIR="$REPO_DIR/shell"

mkdir -p "$CONFIG_DIR" "$SHELL_DIR"

echo "==> 1. Exportando lista de paquetes..."
if command -v pacman >/dev/null 2>&1; then
    pacman -Qqe > "$REPO_DIR/pkglist.txt" || true
    pacman -Qqm > "$REPO_DIR/pkglist-aur.txt" || true
fi

echo "==> 2. Respaldando configuraciones (~/.config)..."
CONFIG_APPS=(
    "hypr"
    "omarchy"
    "kitty"
    "foot"
    "ghostty"
    "alacritty"
    "btop"
    "fastfetch"
    "lazygit"
    "git"
    "waybar"
    "tmux"
    "imv"
)

for app in "${CONFIG_APPS[@]}"; do
    if [ -d "$HOME/.config/$app" ]; then
        echo "   -> Respaldando ~/.config/$app"
        mkdir -p "$CONFIG_DIR/$app"
        # Sincronizar evitando backups temporales creados por editores
        rsync -a --delete \
            --exclude "*.bak.*" \
            --exclude "*~" \
            --exclude "*.log" \
            "$HOME/.config/$app/" "$CONFIG_DIR/$app/"
    fi
done

# Archivos sueltos en ~/.config
[ -f "$HOME/.config/starship.toml" ] && cp "$HOME/.config/starship.toml" "$CONFIG_DIR/"
[ -f "$HOME/.config/chrome-flags.conf" ] && cp "$HOME/.config/chrome-flags.conf" "$CONFIG_DIR/"
[ -f "$HOME/.config/chromium-flags.conf" ] && cp "$HOME/.config/chromium-flags.conf" "$CONFIG_DIR/"

echo "==> 3. Respaldando configuración de la shell..."
[ -f "$HOME/.bashrc" ] && cp "$HOME/.bashrc" "$SHELL_DIR/.bashrc"
[ -f "$HOME/.bash_profile" ] && cp "$HOME/.bash_profile" "$SHELL_DIR/.bash_profile"
[ -f "$HOME/.zshrc" ] && cp "$HOME/.zshrc" "$SHELL_DIR/.zshrc"

echo "==> 4. Guardando en Git..."
cd "$REPO_DIR"

# Configurar valores por defecto si no existen
if ! git config user.name >/dev/null 2>&1; then
    git config user.name "dagudelo"
fi
if ! git config user.email >/dev/null 2>&1; then
    git config user.email "dagudelo@users.noreply.github.com"
fi

git add .
if git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "ℹ No hay cambios nuevos desde el último respaldo."
else
    git commit -m "Backup Omarchy: $(date +'%Y-%m-%d %H:%M:%S')"
    echo "✔ Cambios confirmados en el repositorio local."
fi

echo "✔ Respaldo completado exitosamente en $REPO_DIR"
