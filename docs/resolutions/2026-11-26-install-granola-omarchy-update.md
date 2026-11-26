# Install Granola via AUR with automatic omarchy update integration

- **Date:** 2026-11-26 12:24:46
- **Branch:** `feature/install-granola-omarchy-update`
- **Type:** `feature`

---

## 1. Issue / Requirement
Install the Granola AI notepad application on Omarchy and ensure it updates automatically whenever `omarchy update` is run.

## 2. Root Cause
`granola` is not part of the default Omarchy package set; it is available in the AUR as `aur/granola` (which repackages the official macOS build with `electron44`). Because `/usr/share/omarchy/bin/omarchy-update` already invokes `/usr/share/omarchy/bin/omarchy-update-aur-pkgs` (`yay -Sua --noconfirm --cleanafter --ignore gcc14,gcc14-libs`) for all explicitly installed AUR packages (`pacman -Qem`), installing `granola` from the AUR automatically includes it in `omarchy update` without needing custom hooks.

## 3. Applied Solution
Installed `aur/granola` (`7.726.2-2`) using `yay` with `pkexec` elevation:
```bash
yay --sudo pkexec --sudoflags "" -S --noconfirm --needed -- granola
```

## 4. Modified Files
- `/usr/bin/granola` (installed by `granola` package)
- `/usr/share/applications/granola.desktop` (installed by `granola` package)
- No Omarchy configuration files or custom hooks needed modification.

## 5. Validation
- Verified package installation: `pacman -Q granola` returned `granola 7.726.2-2`.
- Verified AUR update tracking: `pacman -Qem | grep -E '^granola '` returned `granola 7.726.2-2`, confirming `omarchy-update-aur-pkgs` will upgrade it during `omarchy update`.
- Verified binary and desktop entry: `which granola` returned `/usr/bin/granola` and `/usr/share/applications/granola.desktop` is present.
