# Remap code command in terminal to Antigravity IDE

- **Date:** 2026-10-16
- **Branch:** `feature/remap-code-to-antigravity`
- **Type:** `feature`

---

## 1. Issue / Requirement
The user requested re-mapping the terminal `code` command so running `code` opens Antigravity IDE instead of standard VS Code.

## 2. Root Cause
The `code` command resolved to `/usr/bin/code` by default, whereas Antigravity IDE is installed locally at `/home/dagudelo/Downloads/apps/Antigravity IDE/bin/antigravity-ide`.

## 3. Applied Solution
Created a symlink in `~/.local/bin/code` targeting `/home/dagudelo/Downloads/apps/Antigravity IDE/bin/antigravity-ide`. Because `~/.local/bin` is placed before system directories in `$PATH`, invoking `code` now defaults to Antigravity IDE across all interactive shells.

```bash
ln -s "/home/dagudelo/Downloads/apps/Antigravity IDE/bin/antigravity-ide" /home/dagudelo/.local/bin/code
```

## 4. Modified Files
- `/home/dagudelo/.local/bin/code` (symlink to Antigravity IDE CLI launcher)

## 5. Validation
- Verified command resolution in interactive Zsh: `zsh -i -c "which code"` returned `/home/dagudelo/.local/bin/code`.
- Verified command resolution in interactive Bash: `bash -i -c "which code"` returned `/home/dagudelo/.local/bin/code`.
- Verified `--help` execution through the binary wrapper.
