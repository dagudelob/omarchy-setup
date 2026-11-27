# Install lazygit and lazydocker with Omarchy Auto-Update

- **Date:** 2026-11-27
- **Branch:** `feature/install-lazygit-lazydocker-omarchy-update`
- **Type:** `feature`

---

## 1. Issue / Requirement
Install `lazygit` and `lazydocker` on Omarchy Linux ensuring both tools are automatically kept up to date whenever `omarchy update` runs.

## 2. Root Cause
`lazydocker` was not installed on the system, while `lazygit` (`0.66.2-1`) was already installed. Both packages needed to be managed through an official `omarchy update`-supported mechanism.

## 3. Applied Solution
Verified both `lazygit` and `lazydocker` are available in the official Arch Linux `extra` repository (priority #1 for `omarchy update`) and installed them via `pacman`:

```bash
pkexec pacman -S --noconfirm --needed lazygit lazydocker
```

Because both packages come from the official Arch `extra` repository, `omarchy update` automatically updates them during `omarchy-update-system-pkgs` with no extra hooks required.

## 4. Modified Files
- None (system packages installed via `pacman` from official Arch `extra` repository).

## 5. Validation
Verified package installation and CLI execution:

```bash
pacman -Q lazygit lazydocker
# lazygit 0.66.2-1
# lazydocker 0.25.2-1

lazygit --version
lazydocker --version
```
