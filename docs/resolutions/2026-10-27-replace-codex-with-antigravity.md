# Replace Codex with Antigravity as Default Agent for Crash Diagnoses and Omarchy

- **Date:** 2026-10-27
- **Branch:** `feature/replace-codex-with-antigravity`
- **Type:** `feature`

---

## 1. Issue / Requirement
When applications or desktop components crashed on Omarchy, clicking the system notification ("Process crashed: ... Click to diagnose with AI") launched OpenAI Codex CLI instead of Google Antigravity (`agy`). The user requested replacing Codex with Antigravity across Omarchy and making Antigravity the default crash diagnosis agent.

## 2. Root Cause
1. In Omarchy, `omarchy-crash-watch` invokes `omarchy-agent-crash`, which runs `omarchy-agent --prompt "$prompt"`.
2. `omarchy-agent` checks `omarchy-default-agent`, which reads `~/.config/omarchy/defaults/agent`. This configuration file was previously pointing to `codex`.
3. Upstream Omarchy did not include native wrappers or menu options for Antigravity (`agy`), falling back to Codex.

## 3. Applied Solution
1. Updated `~/.config/omarchy/defaults/agent` to `agy`.
2. Updated wrapper script `~/.local/bin/omarchy-default-agent` to:
   - Default to `agy` if empty or previously set to `codex` / `gemini`.
   - Intercept calls to `codex`, `agy`, and `antigravity`, consistently configuring and running Antigravity.
3. Updated wrapper script `~/.local/bin/omarchy-agent` to:
   - Detect `agy`, `antigravity`, or legacy `codex` requests.
   - Forward initial crash prompts to `agy --prompt-interactive "$prompt"`.
   - Spawn the session in Omarchy's themed floating terminal (`org.omarchy.agent`).
4. Overrode `setup.default.agent.codex` in `~/.config/omarchy/extensions/omarchy-menu.jsonc` to display `Antigravity (AGY)` and execute `omarchy-default-agent agy`, while hiding the obsolete Gemini entry.
5. Updated `backup.sh` and `restore.sh` to track, backup, and restore user bin scripts in `bin/`.
6. Reloaded Omarchy shell and verified `omarchy-default-agent` and crash handling invocation.

## 4. Modified Files
- `/home/dagudelo/.config/omarchy/defaults/agent`
- `/home/dagudelo/.config/omarchy/extensions/omarchy-menu.jsonc`
- `/home/dagudelo/.local/bin/omarchy-default-agent`
- `/home/dagudelo/.local/bin/omarchy-agent`
- `bin/omarchy-default-agent`
- `bin/omarchy-agent`
- `config/omarchy/defaults/agent`
- `config/omarchy/extensions/omarchy-menu.jsonc`
- `backup.sh`
- `restore.sh`
- `docs/resolutions/2026-10-27-replace-codex-with-antigravity.md`

## 5. Validation
- Verified `omarchy-default-agent` returns `agy`.
- Tested `omarchy-default-agent codex` and confirmed it automatically updates to `agy` and redirects execution to `agy`.
- Verified `omarchy-launch-tui` and `xdg-terminal-exec` argument construction for `foot` terminal.
- Executed `backup.sh` successfully with secret scanning passed.
