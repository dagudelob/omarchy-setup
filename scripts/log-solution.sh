#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

TYPE="${1:-fix}"          # fix | feature | chore
SLUG="${2:-}"             # fix-slug (kebab-case)
TITLE="${3:-}"            # Human-readable title

if [ -z "$SLUG" ]; then
    echo "Usage: $0 <fix|feature> <fix-slug> \"[Optional Title]\""
    echo "Example: $0 fix omarchy-update-path \"OMARCHY_PATH path error in omarchy-update\""
    exit 1
fi

BRANCH_NAME="${TYPE}/${SLUG}"
DATE_STR="$(date +'%Y-%m-%d')"
DOC_DIR="$REPO_DIR/docs/resolutions"
DOC_FILE="$DOC_DIR/${DATE_STR}-${SLUG}.md"

mkdir -p "$DOC_DIR"

echo "==> 1. Ensuring main is up to date..."
git checkout main
git pull origin main 2>/dev/null || true

echo "==> 2. Creating/Switching to branch $BRANCH_NAME..."
if git show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; then
    git checkout "$BRANCH_NAME"
else
    git checkout -b "$BRANCH_NAME"
fi

if [ ! -f "$DOC_FILE" ]; then
    echo "==> 3. Creating Markdown template in $DOC_FILE..."
    cat <<EOF > "$DOC_FILE"
# ${TITLE:-$SLUG}

- **Date:** $(date +'%Y-%m-%d %H:%M:%S')
- **Branch:** \`$BRANCH_NAME\`
- **Type:** \`${TYPE}\`

---

## 1. Issue / Requirement
<!-- 2-3 line summary of the issue or requested functionality -->

## 2. Root Cause
<!-- Brief explanation of why the problem occurred -->

## 3. Applied Solution
<!-- Concrete steps, commands executed, and modified configurations -->

## 4. Modified Files
<!-- List of created or edited files -->

## 5. Validation
<!-- How the resolution was verified -->
EOF
    echo "✔ Template created: $DOC_FILE"
fi

echo "✔ Active branch: $BRANCH_NAME"
echo "You can edit the file: $DOC_FILE"
