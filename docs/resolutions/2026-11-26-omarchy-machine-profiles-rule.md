# Add Antigravity rule for Surface vs Desktop machine profiles

- **Date:** 2026-11-26
- **Branch:** `feature/omarchy-machine-profiles-rule`
- **Type:** `feature`

---

## 1. Issue / Requirement
Need to persist Antigravity rules inside `omarchy-setup` so that reinstalling Omarchy on another Surface or setting up a Desktop PC later preserves Surface-specific rules while preventing cross-machine overwrites.

## 2. Root Cause
Antigravity rules stored only in local machine config are not versioned in Git, and `omarchy-setup` currently holds Surface-specific configurations (`monitors.lua`, `input.lua`, touchpad scripts, kernel/camera/boot fixes) mixed with shared dotfiles.

## 3. Applied Solution
- Created `.agents/rules/omarchy-profiles.md` inside `omarchy-setup` (automatically discovered by Antigravity whenever the repo is opened on any machine).
- Documented that `config/` currently represents the Surface backup and defined the future separation between shared configs, Surface-exclusive configs, and Desktop-exclusive configs.
- Added mandatory agent checks to verify the target machine/profile before editing hardware/display/input configs or running `backup.sh` / `restore.sh`.

## 4. Modified Files
- `/home/dagudelo/Code/omarchy-setup/.agents/rules/omarchy-profiles.md`
- `/home/dagudelo/Code/omarchy-setup/docs/resolutions/2026-11-26-omarchy-machine-profiles-rule.md`

## 5. Validation
Verified `.agents/rules/omarchy-profiles.md` exists in the repository and published the branch and `RESOLUTIONS.md` entry via `publish-solution.sh`.
