#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

TYPE="${1:-fix}"          # fix | feature | chore
SLUG="${2:-}"             # nombre-del-arreglo (kebab-case)
TITLE="${3:-}"            # Título legible

if [ -z "$SLUG" ]; then
    echo "Uso: $0 <fix|feature> <slug-del-arreglo> \"[Título Opcional]\""
    echo "Ejemplo: $0 fix omarchy-update-path \"Error de ruta OMARCHY_PATH en omarchy-update\""
    exit 1
fi

BRANCH_NAME="${TYPE}/${SLUG}"
DATE_STR="$(date +'%Y-%m-%d')"
DOC_DIR="$REPO_DIR/docs/resolutions"
DOC_FILE="$DOC_DIR/${DATE_STR}-${SLUG}.md"

mkdir -p "$DOC_DIR"

echo "==> 1. Asegurando que main esté al día..."
git checkout main
git pull origin main 2>/dev/null || true

echo "==> 2. Creando/Cambiando a la rama $BRANCH_NAME..."
if git show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; then
    git checkout "$BRANCH_NAME"
else
    git checkout -b "$BRANCH_NAME"
fi

if [ ! -f "$DOC_FILE" ]; then
    echo "==> 3. Creando plantilla Markdown en $DOC_FILE..."
    cat <<EOF > "$DOC_FILE"
# ${TITLE:-$SLUG}

- **Fecha:** $(date +'%Y-%m-%d %H:%M:%S')
- **Rama:** \`$BRANCH_NAME\`
- **Tipo:** \`${TYPE}\`

---

## 1. Inconveniente / Requerimiento
<!-- Resumen de 2-3 líneas del error o funcionalidad solicitada -->

## 2. Causa Raíz
<!-- Explicación breve de por qué ocurría el problema -->

## 3. Solución Aplicada
<!-- Pasos concretos, comandos ejecutados y configuraciones modificadas -->

## 4. Archivos Modificados
<!-- Lista de archivos creados o editados -->

## 5. Validación
<!-- Cómo se comprobó que quedó solucionado -->
EOF
    echo "✔ Plantilla creada: $DOC_FILE"
fi

echo "✔ Rama activa: $BRANCH_NAME"
echo "Puedes editar el archivo: $DOC_FILE"
