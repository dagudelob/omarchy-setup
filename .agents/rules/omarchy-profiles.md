# Omarchy Setup — Machine Profiles & Surface Rules

## Current State
- This repository (`omarchy-setup`) currently stores the full backup and fixes for the **Microsoft Surface** (`config/`, `shell/`, `pkglist.txt`, `pkglist-aur.txt`, `RESOLUTIONS.md`).
- Until the desktop PC profile is separated (`profiles/surface/` and `profiles/desktop/`), treat `config/` as **Surface-specific** whenever hardware, display, input, or boot settings are involved.

## Machine Separation Guidelines (Surface vs. Desktop)

### 1. Shared Across Machines (Common)
- Terminal emulators (`kitty`, `foot`, `ghostty`, `alacritty`)
- Shell & prompt (`.bashrc`, `.bash_profile`, `.zshrc`, `starship.toml`)
- Desktop utilities & aesthetics (`waybar`, `btop`, `fastfetch`, `tmux`, `lazygit`, `git`, `imv`, Omarchy themes, `config/hypr/looknfeel.lua`, `config/hypr/bindings.lua`)
- General-purpose packages in `pkglist.txt` / `pkglist-aur.txt`

### 2. Surface-Exclusive (Do NOT apply blindly to Desktop)
- `config/hypr/monitors.lua` (Surface HiDPI resolution & scaling)
- `config/hypr/input.lua` (Surface touchpad & keyboard rules)
- `config/omarchy/scripts/surface-touchpad-gestures.py`
- `config/omarchy/scripts/touchpad-typing-delay.py`
- Surface-specific kernel, camera, touchscreen, and boot fixes (`linux-surface`, Intel IPU3 / WirePlumber camera fixes, Limine / BitLocker entries, Surface keyboard/caps/us-intl quirks)

### 3. Desktop-Exclusive (Future `profiles/desktop/`)
- Desktop `monitors.lua` (external monitor resolution, refresh rate, scaling)
- Desktop `input.lua` (without Surface touchpad gestures or typing-delay scripts)
- Desktop-specific GPU/hardware packages

## Mandatory Agent Behavior
1. **Verify target machine before acting:** Before running `backup.sh`, `restore.sh`, or editing `config/hypr/monitors.lua`, `config/hypr/input.lua`, `config/omarchy/scripts/`, or boot/hardware configs, check which machine is running (e.g., `/sys/class/dmi/id/product_name` or `hostnamectl`) or ask the user whether the change is for **Surface** or **Desktop**.
2. **Prevent cross-machine overwrites:** Never run `backup.sh` from a Desktop PC into the Surface config tree without first separating `profiles/surface/` and `profiles/desktop/`.
3. **Preserve Surface workarounds:** When working on the Surface, respect existing fixes documented in `RESOLUTIONS.md` and keep using `.agents/skills/omarchy-backup/SKILL.md` and `.agents/skills/omarchy-branch-logger/SKILL.md`.
