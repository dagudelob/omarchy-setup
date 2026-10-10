# Zsh and Oh My Posh Configuration with Night Owl Theme and Nerd Fonts

- **Date:** 2026-10-09
- **Branch:** `feature/zsh-oh-my-posh-night-owl`
- **Type:** `feature`

---

## 1. Issue / Requirement
Complete installation and setup of Zsh as the default shell on Omarchy (Hyprland using the `Super + Enter` shortcut), integrating Oh My Posh with the `night-owl.omp.json` theme, and resolving glyph/icon rendering issues (characters showing up as tofu/boxes).

## 2. Root Cause
- Zsh was not installed system-wide and the user was assigned Bash.
- The IDE's integrated terminal and Electron applications lacked strict fallback rules to Nerd Fonts and Symbols in `fontconfig`, preventing Powerline glyphs (`\ue0b0`, `\uf489`, etc.) from rendering correctly.

## 3. Applied Solution
1. Installed Oh My Posh into `~/.local/bin/oh-my-posh` and downloaded the official theme repository into `~/.cache/oh-my-posh/themes/`.
2. Installed Zsh (`sudo pacman -S zsh`) and configured it as the default user shell (`chsh -s $(which zsh)`).
3. Created and configured `~/.zshrc` with Oh My Posh initialization loading `night-owl.omp.json`.
4. Downloaded and installed full `JetBrainsMono Nerd Font` and `Symbols Nerd Font` font families into `~/.local/share/fonts/NerdFonts/`.
5. Configured `~/.config/fontconfig/fonts.conf` with strong binding (`binding="strong"`) for the `monospace` family and updated the font cache with `fc-cache -r`.
6. Configured the IDE integrated terminal in `settings.json` with explicit Nerd Fonts fallback support.

## 4. Modified Files
- `/home/dagudelo/.zshrc`
- `/home/dagudelo/.config/fontconfig/fonts.conf`
- `/home/dagudelo/.config/Antigravity IDE/User/settings.json`
- `/home/dagudelo/Code/omarchy-setup/.vscode/settings.json`
- `/home/dagudelo/.local/share/fonts/NerdFonts/*`

## 5. Validation
- User shell verified in `/etc/passwd` pointing to `/usr/bin/zsh`.
- Interactive execution of Zsh verified with `oh-my-posh` v31.6.0.
- `fc-match monospace` resolving immediately to `JetBrainsMonoNerdFont-Regular.ttf`.
- Default terminal emulator (`foot`) successfully launched via `Super + Enter` executing Zsh.
