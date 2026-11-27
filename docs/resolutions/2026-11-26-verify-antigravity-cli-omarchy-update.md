# Verify Antigravity CLI (agy) installation and automatic omarchy update via mise

- **Date:** 2026-11-26 23:18:28
- **Branch:** `fix/verify-antigravity-cli-omarchy-update`
- **Type:** `fix`

---

## 1. Issue / Requirement
Ensure `antigravity-cli` (`agy`) is installed in the terminal and updates automatically whenever `omarchy update` is executed.

## 2. Root Cause
No issue was present: Omarchy already provisions and manages `antigravity-cli` (`agy`) natively through `mise` in `/etc/mise/conf.d/omarchy-tools.toml`, which is updated automatically during `omarchy update` via `omarchy-update-mise`. Installing the native `omarchy/antigravity-cli` pacman package was unnecessary because the `mise` shim already takes precedence in `$PATH`.

## 3. Applied Solution
Verified the existing Omarchy + `mise` integration instead of introducing duplicate pacman or hook overrides:
- Confirmed `antigravity-cli` is configured in `/etc/mise/conf.d/omarchy-tools.toml` as:
  `antigravity-cli = { version = "latest", lazy = true, auto_update = "4h", minimum_release_age = "0s" }`
- Confirmed `/usr/share/omarchy/bin/omarchy-update` invokes `omarchy-update-mise`, which executes `MISE_MINIMUM_RELEASE_AGE=0 mise up` to upgrade `agy` to the latest release.

## 4. Modified Files
- `/home/dagudelo/Code/omarchy-setup/docs/resolutions/2026-11-26-verify-antigravity-cli-omarchy-update.md` (no system configuration changes needed).

## 5. Validation
- `which agy` resolves to `/home/dagudelo/.local/share/mise/shims/agy` (`mise which agy` -> `/home/dagudelo/.local/share/mise/installs/antigravity-cli/latest/agy`).
- `agy --version` returned `1.5.18` (matching the latest `omarchy/antigravity-cli` `1.5.18-1` release).
- `mise ls antigravity-cli` showed automatic progression across prior versions (`1.3.2` through `1.5.18`).
