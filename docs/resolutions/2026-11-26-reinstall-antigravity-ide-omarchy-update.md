# Reinstall antigravity-ide 2.8.0-1 and verify omarchy update integration

- **Date:** 2026-11-26
- **Branch:** `fix/reinstall-antigravity-ide-omarchy-update`
- **Type:** `fix`

---

## 1. Issue / Requirement
Uninstall and reinstall `antigravity-ide` (stuck on `2.7.0-1`), and ensure it updates automatically whenever `omarchy update` runs.

## 2. Root Cause
`omarchy-update` already updates all AUR packages (including `antigravity-ide`) via `omarchy-update-aur-pkgs` (`yay -Sua`), but the upstream AUR `antigravity-ide` `2.8.0-1` `PKGBUILD` listed a non-existent `openssl-3` dependency instead of `openssl`, causing `yay` to abort during `omarchy update`.

## 3. Applied Solution
1. Uninstalled `antigravity-ide` `2.7.0-1`:
   ```bash
   pkexec pacman -R --noconfirm antigravity-ide
   ```
2. Fetched the `antigravity-ide` `2.8.0-1` AUR `PKGBUILD`, patched `openssl-3` to `openssl`, built the package with `makepkg -s --noconfirm`, and installed it:
   ```bash
   sed -i 's/openssl-3/openssl/' PKGBUILD
   makepkg -s --noconfirm
   pkexec pacman -U --noconfirm antigravity-ide-2.8.0-1-x86_64.pkg.tar.zst
   ```
3. Confirmed `/usr/bin/omarchy-update` invokes `/usr/bin/omarchy-update-aur-pkgs`, which runs `yay -Sua --noconfirm --cleanafter --ignore gcc14,gcc14-libs` and automatically includes `antigravity-ide` (`pacman -Qem`).

## 4. Modified Files
- `/opt/antigravity-ide/` (system package reinstalled to `2.8.0-1` via `pacman`)
- `/home/dagudelo/Code/omarchy-setup/docs/resolutions/2026-11-26-reinstall-antigravity-ide-omarchy-update.md`

## 5. Validation
- `pacman -Q antigravity-ide` returned `antigravity-ide 2.8.0-1`.
- `yay -Qua | grep -i antigravity` returned no pending updates.
