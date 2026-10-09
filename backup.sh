#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$REPO_DIR/config"
SHELL_DIR="$REPO_DIR/shell"
AUTO_PUSH=false

for arg in "$@"; do
    case "$arg" in
        --push|-p)
            AUTO_PUSH=true
            ;;
    esac
done

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
        rsync -a --delete \
            --exclude "*.bak.*" \
            --exclude "*~" \
            --exclude "*.log" \
            --exclude "*.key" \
            --exclude "*.token" \
            --exclude "*.secret" \
            --exclude ".env*" \
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

echo "==> 4. Verificación de seguridad (escaneo de secretos)..."
cd "$REPO_DIR"

# Configurar valores por defecto si no existen
if ! git config user.name >/dev/null 2>&1; then
    git config user.name "dagudelo"
fi
if ! git config user.email >/dev/null 2>&1; then
    git config user.email "dagudelo@users.noreply.github.com"
fi

git add .

# Buscar patrones de secretos en los archivos preparados (excluyendo este mismo script)
P_KEY=$(printf 'B%sN.*PRIVATE KEY' "EGI")
P_TOK=$(printf 'g%s_[A-Za-z0-9]{20,}' "hp")
DETECTED=$(git diff --cached -- . ':!backup.sh' | grep -E -i "($P_KEY|$P_TOK)" || true)
if [ -n "$DETECTED" ]; then
    echo "❌ ERROR DE SEGURIDAD: Se detectaron posibles secretos en los archivos preparados:"
    echo "$DETECTED"
    echo "Abortando commit y push para proteger tu seguridad."
    exit 1
fi

echo "==> 5. Guardando en Git local..."
if git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "ℹ No hay cambios nuevos desde el último respaldo."
else
    git commit -m "Backup Omarchy: $(date +'%Y-%m-%d %H:%M:%S')"
    echo "✔ Cambios confirmados en el repositorio local."
fi

if [ "$AUTO_PUSH" = true ]; then
    echo "==> 6. Subiendo a GitHub..."
    git push origin main
    echo "✔ Cambios subidos exitosamente a https://github.com/dagudelob/omarchy-setup"
fi

echo "✔ Respaldo completado exitosamente en $REPO_DIR"
