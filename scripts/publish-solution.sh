#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

if [ "$CURRENT_BRANCH" = "main" ]; then
    echo "❌ Error: You are on branch 'main'. You must be on the solution/feature branch to publish it."
    exit 1
fi

COMMIT_MSG="${1:-"docs: log solution for ${CURRENT_BRANCH}"}"

echo "==> 1. Anti-secrets security scan..."
P_KEY=$(printf 'B%sN.*PRIVATE KEY' "EGI")
P_TOK=$(printf 'g%s_[A-Za-z0-9]{20,}' "hp")
DETECTED=$(git diff --cached -- . ':!scripts/*' ':!backup.sh' 2>/dev/null | grep -E -i "($P_KEY|$P_TOK)" || true)

if [ -n "$DETECTED" ]; then
    echo "❌ SECURITY ERROR: Possible secrets detected in staged files:"
    echo "$DETECTED"
    echo "Aborting commit and push to protect your security."
    exit 1
fi

echo "==> 2. Committing changes to branch $CURRENT_BRANCH..."
git add .
if git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "ℹ No pending changes to commit."
else
    git commit -m "$COMMIT_MSG"
fi

echo "==> 3. Pushing branch $CURRENT_BRANCH to GitHub..."
git push -u origin "$CURRENT_BRANCH"

echo ""
echo "==> 4. Updating solutions catalog on main branch..."
# Find the documentation file in current branch
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
# Troubleshooting and Resolutions Catalog (Omarchy)

Organized registry of resolved issues and implemented features, with their corresponding dedicated branches on GitHub.

| Date | Type | Title / Issue | Branch on GitHub |
|---|---|---|---|
EOF
fi

DATE_NOW="$(date +'%Y-%m-%d')"
BRANCH_LINK="[${CURRENT_BRANCH}](https://github.com/dagudelob/omarchy-setup/tree/${CURRENT_BRANCH})"

# Avoid duplicating row in catalog if already present
if ! grep -Fq "$CURRENT_BRANCH" "$INDEX_FILE"; then
    echo "| $DATE_NOW | \`${CURRENT_BRANCH%%/*}\` | $DOC_TITLE | $BRANCH_LINK |" >> "$INDEX_FILE"
    git add "$INDEX_FILE"
    git commit -m "docs: register $CURRENT_BRANCH in resolutions catalog"
    git push origin main
fi

echo ""
echo "=========================================================="
echo " ✔ Solution registered and published successfully!"
echo " Branch on GitHub: https://github.com/dagudelob/omarchy-setup/tree/$CURRENT_BRANCH"
echo " Catalog on main: https://github.com/dagudelob/omarchy-setup/blob/main/RESOLUTIONS.md"
echo "=========================================================="
