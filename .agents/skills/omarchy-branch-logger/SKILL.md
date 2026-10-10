---
name: omarchy-branch-logger
description: >-
  Create a dedicated Git branch and Markdown record on GitHub for each Omarchy issue, bug fix, or requested feature.
  PRIMARY TRIGGER: Triggers immediately whenever the user says "este tema quedó solucionado", "tema solucionado", "quedó solucionado", "issue resolved", "problem solved", "save solution", "create branch for this issue", or asks to document an issue/fix/feature into a branch.
  Summarizes the problem, root cause, and final solution in a structured, ultra-concise Markdown file, pushes the branch to GitHub (@dagudelob/omarchy-setup), and maintains a clean catalog in the main branch.
---

# Omarchy Branch Logger Skill

Organizes, documents, and pushes every troubleshooting fix or feature into its own isolated Git branch on GitHub (`@dagudelob/omarchy-setup`), keeping solutions clean, searchable, and structured with concise Markdown records.

## Primary Triggers
**ALWAYS activate this skill when the user indicates an issue is solved or asks to document it:**
- `"este tema quedó solucionado"` / `"tema solucionado"` / `"quedó solucionado"`
- `"issue resolved"` / `"problem solved"` / `"this is solved"`
- `"document this fix"` / `"guardar solucion"`
- `"create branch for this solution"` / `"crear rama para esta solución"`

---

## Repository
- **Local directory:** `/home/dagudelo/Code/omarchy-setup`
- **GitHub:** `https://github.com/dagudelob/omarchy-setup`

---

## Automated Agent Procedure

The moment the user indicates a topic is solved:

### Step 1: Identify the Topic from Conversation
- Identify the problem or feature that was just resolved in recent conversation turns.
- Determine the type:
  - `fix/` for errors, bugs, incompatibilities, or system repairs.
  - `feature/` for new configurations, tools, or customizations.
- Generate a concise, kebab-case slug (e.g. `fix/omarchy-update-path`, `feature/auto-backup-skill`).

### Step 2: Create and Checkout Branch
Execute the helper script to initialize the branch:

```bash
/home/dagudelo/Code/omarchy-setup/scripts/log-solution.sh <fix|feature> <slug> "<Descriptive title of the resolution>"
```

### Step 3: Write Executive Summary in Markdown
Edit the generated file in `docs/resolutions/YYYY-MM-DD-<slug>.md` ensuring it is **concise, direct, and focused**:

```markdown
# [Title of the Fix / Feature]

- **Date:** YYYY-MM-DD
- **Branch:** `fix/<slug>` or `feature/<slug>`
- **Type:** `fix` | `feature`

---

## 1. Issue / Requirement
Executive summary in 2-3 lines: what the issue was or what needed to be achieved.

## 2. Root Cause
Technical explanation in 1-2 lines detailing why the problem occurred.

## 3. Applied Solution
Exact commands executed, file changes made, and definitive steps applied.

## 4. Modified Files
- List of absolute paths of created or edited files.

## 5. Validation
How the fix was verified to ensure it works correctly.
```

*(If the solution involved configuration files in `~/.config/`, ensure those files are synced in the branch if applicable).*

### Step 4: Security Scan and GitHub Publication
Run:

```bash
/home/dagudelo/Code/omarchy-setup/scripts/publish-solution.sh "docs: log solution for <slug>"
```

The script automatically:
1. Applies the anti-secrets filter (`ghp_`, `gho_` tokens, SSH/RSA private keys).
2. Commits changes to the resolution branch.
3. Pushes the branch to GitHub: `git push -u origin <branch>`.
4. Switches back to `main` and updates the master table in `RESOLUTIONS.md` with direct link to the branch on GitHub.
5. Pushes the updated `main` branch to GitHub.

### Step 5: Respond to User
Display an ultra-compact summary in chat:
- Name of the created branch on GitHub.
- Brief 3-line summary of the registered solution.
- Direct branch link: `https://github.com/dagudelob/omarchy-setup/tree/<branch>`.
- Master catalog link: `https://github.com/dagudelob/omarchy-setup/blob/main/RESOLUTIONS.md`.
