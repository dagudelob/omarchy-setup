#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

if [ "$CURRENT_BRANCH" = "main" ]; then
    echo "❌ Error: Te encuentras en la rama 'main'. Debes estar en la rama de la solución/feature para publicarla."
    exit 1
fi

COMMIT_MSG="${1:-"docs: registrar solucion en ${CURRENT_BRANCH}"}"

echo "==> 1. Escaneo de seguridad anti-secretos..."
P_KEY=$(printf 'B%sN.*PRIVATE KEY' "EGI")
P_TOK=$(printf 'g%s_[A-Za-z0-9]{20,}' "hp")
DETECTED=$(git diff --cached -- . ':!scripts/*' ':!backup.sh' 2>/dev/null | grep -E -i "($P_KEY|$P_TOK)" || true)

if [ -n "$DETECTED" ]; then
    echo "❌ ERROR DE SEGURIDAD: Se detectaron posibles secretos en los archivos preparados:"
    echo "$DETECTED"
    echo "Abortando commit y push para proteger tu seguridad."
    exit 1
fi

echo "==> 2. Guardando cambios en la rama $CURRENT_BRANCH..."
git add .
if git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "ℹ No hay cambios pendientes por commitear."
else
    git commit -m "$COMMIT_MSG"
fi

echo "==> 3. Subiendo rama $CURRENT_BRANCH a GitHub..."
git push -u origin "$CURRENT_BRANCH"

echo ""
echo "==> 4. Actualizando catálogo de soluciones en la rama main..."
# Buscar el archivo de documentación en la rama actual
SLUG="${CURRENT_BRANCH#*/}"
DOC_PATH=$(git ls-files "docs/resolutions/*${SLUG}*.md" | head -n 1 || true)
if [ -z "$DOC_PATH" ]; then
    DOC_PATH=$(git ls-files "docs/resolutions/*.md" | tail -n 1 || true)
fi
DOC_TITLE="$CURRENT_BRANCH"
if [ -n "$DOC_PATH" ] && [ -f "$DOC_PATH" ]; then
    DOC_TITLE=$(head -n 1 "$DOC_PATH" | sed 's/^# *//' || echo "$CURRENT_BRANCH")
fi

git checkout main
git pull origin main 2>/dev/null || true

INDEX_FILE="$REPO_DIR/RESOLUTIONS.md"
if [ ! -f "$INDEX_FILE" ]; then
    cat <<EOF > "$INDEX_FILE"
# Catálogo de Inconvenientes y Soluciones (Omarchy)

Registro organizado de problemas resueltos y configuraciones realizadas, con sus respectivas ramas dedicadas en GitHub.

| Fecha | Tipo | Título / Inconveniente | Rama en GitHub |
|---|---|---|---|
EOF
fi

DATE_NOW="$(date +'%Y-%m-%d')"
BRANCH_LINK="[${CURRENT_BRANCH}](https://github.com/dagudelob/omarchy-setup/tree/${CURRENT_BRANCH})"

# Evitar duplicar la fila en el catálogo si ya existe
if ! grep -Fq "$CURRENT_BRANCH" "$INDEX_FILE"; then
    echo "| $DATE_NOW | \`${CURRENT_BRANCH%%/*}\` | $DOC_TITLE | $BRANCH_LINK |" >> "$INDEX_FILE"
    git add "$INDEX_FILE"
    git commit -m "docs: registrar $CURRENT_BRANCH en catalogo de soluciones"
    git push origin main
fi

echo ""
echo "=========================================================="
echo " ✔ ¡Solución registrada y publicada con éxito!"
echo " Rama en GitHub: https://github.com/dagudelob/omarchy-setup/tree/$CURRENT_BRANCH"
echo " Catálogo en main: https://github.com/dagudelob/omarchy-setup/blob/main/RESOLUTIONS.md"
echo "=========================================================="
