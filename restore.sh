#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$REPO_DIR/config"
SHELL_DIR="$REPO_DIR/shell"

echo "=========================================="
echo "  Restaurador de Configuración de Omarchy "
echo "=========================================="

# 1. Restaurar ~/.config
if [ -d "$CONFIG_DIR" ]; then
    echo "==> 1. Restaurando configuraciones en ~/.config..."
    mkdir -p "$HOME/.config"
    for item in "$CONFIG_DIR"/*; do
        target_name="$(basename "$item")"
        if [ -d "$item" ]; then
            mkdir -p "$HOME/.config/$target_name"
            rsync -a "$item/" "$HOME/.config/$target_name/"
            echo "   -> Restaurado ~/.config/$target_name"
        elif [ -f "$item" ]; then
            cp "$item" "$HOME/.config/$target_name"
            echo "   -> Restaurado ~/.config/$target_name"
        fi
    done
fi

# 2. Restaurar shell
if [ -d "$SHELL_DIR" ]; then
    echo "==> 2. Restaurando archivos de shell..."
    [ -f "$SHELL_DIR/.bashrc" ] && cp "$SHELL_DIR/.bashrc" "$HOME/.bashrc" && echo "   -> ~/.bashrc"
    [ -f "$SHELL_DIR/.bash_profile" ] && cp "$SHELL_DIR/.bash_profile" "$HOME/.bash_profile" && echo "   -> ~/.bash_profile"
    [ -f "$SHELL_DIR/.zshrc" ] && cp "$SHELL_DIR/.zshrc" "$HOME/.zshrc" && echo "   -> ~/.zshrc"
fi

# 3. Recargar entorno
echo "==> 3. Recargando servicios y entorno..."
if command -v omarchy >/dev/null 2>&1; then
    omarchy restart shell 2>/dev/null || true
fi
if command -v hyprctl >/dev/null 2>&1; then
    hyprctl reload 2>/dev/null || true
fi

echo "✔ ¡Restauración completada con éxito!"
echo "Nota: Si necesitas reinstalar los paquetes de Arch/AUR, consulta pkglist.txt y pkglist-aur.txt."
