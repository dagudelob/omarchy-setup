# Add AGY as Default Coding Agent in Omarchy

- **Date:** 2026-10-16
- **Branch:** `feature/update-default-agent-to-agy`
- **Type:** `feature`

---

## 1. Issue / Requirement
Omarchy's defaults menu for coding agents (`Setup > Default Agent`) offered an outdated `gemini` option that did not launch the current Google Antigravity CLI (`agy`). The user requested updating the menu so `agy` appears and can be selected as the default agent.

## 2. Root Cause
The upstream package `omarchy` / `omarchy-settings` hardcodes `setup.default.agent.gemini` mapped to the old `omarchy-default-agent gemini` command and legacy binary flags. Upstream has not yet integrated the new `agy` CLI binary into its core agent list.

## 3. Applied Solution
1. Extended the Quickshell Omarchy menu in `~/.config/omarchy/extensions/omarchy-menu.jsonc` by overriding `setup.default.agent.gemini` with label `AGY (Antigravity)`, executing `omarchy-default-agent agy`, and verifying check status with `[[ "$(omarchy-default-agent)" == "agy" ]]`.
2. Created custom user wrappers in `~/.local/bin/` (`omarchy-default-agent` and `omarchy-agent`) that intercept `agy` requests, configure `~/.config/omarchy/defaults/agent`, and spawn `agy` with terminal window classes and prompt forwarding (`--prompt-interactive`), falling back to `/usr/bin/` for any other agent.
3. Updated `backup.sh` and `restore.sh` in `omarchy-setup` to track and restore these user bin wrappers.

## 4. Modified Files
- `~/.config/omarchy/extensions/omarchy-menu.jsonc`
- `~/.local/bin/omarchy-default-agent`
- `~/.local/bin/omarchy-agent`
- `~/.config/omarchy/defaults/agent`
- `backup.sh`
- `restore.sh`
- `bin/omarchy-default-agent`
- `bin/omarchy-agent`
- `docs/resolutions/2026-10-16-update-default-agent-to-agy.md`

## 5. Validation
- Tested `omarchy-default-agent agy` and confirmed `~/.config/omarchy/defaults/agent` is set to `agy`.
- Validated menu checked condition `[[ "$(omarchy-default-agent)" == "agy" ]]` which successfully evaluated to true.
- Verified `omarchy-agent` correctly prepares `agy` command line and executes properly.
- Performed configuration backup and secret scanning.
