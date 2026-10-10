#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$REPO_DIR/config"
SHELL_DIR="$REPO_DIR/shell"

echo "=========================================="
echo "    Omarchy Configuration Restorer        "
echo "=========================================="

# 1. Restore ~/.config
if [ -d "$CONFIG_DIR" ]; then
    echo "==> 1. Restoring configurations to ~/.config..."
    mkdir -p "$HOME/.config"
    for item in "$CONFIG_DIR"/*; do
        target_name="$(basename "$item")"
        if [ -d "$item" ]; then
            mkdir -p "$HOME/.config/$target_name"
            rsync -a "$item/" "$HOME/.config/$target_name/"
            echo "   -> Restored ~/.config/$target_name"
        elif [ -f "$item" ]; then
            cp "$item" "$HOME/.config/$target_name"
            echo "   -> Restored ~/.config/$target_name"
        fi
    done
fi

# 2. Restore shell
if [ -d "$SHELL_DIR" ]; then
    echo "==> 2. Restoring shell files..."
    [ -f "$SHELL_DIR/.bashrc" ] && cp "$SHELL_DIR/.bashrc" "$HOME/.bashrc" && echo "   -> ~/.bashrc"
    [ -f "$SHELL_DIR/.bash_profile" ] && cp "$SHELL_DIR/.bash_profile" "$HOME/.bash_profile" && echo "   -> ~/.bash_profile"
    [ -f "$SHELL_DIR/.zshrc" ] && cp "$SHELL_DIR/.zshrc" "$HOME/.zshrc" && echo "   -> ~/.zshrc"
fi

# 3. Reload environment
echo "==> 3. Reloading services and desktop environment..."
if command -v omarchy >/dev/null 2>&1; then
    omarchy restart shell 2>/dev/null || true
fi
if command -v hyprctl >/dev/null 2>&1; then
    hyprctl reload 2>/dev/null || true
fi

echo "✔ Restoration completed successfully!"
echo "Note: If you need to reinstall Arch/AUR packages, refer to pkglist.txt and pkglist-aur.txt."
