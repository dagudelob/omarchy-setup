# Configuración de Zsh y Oh My Posh con tema Night Owl y Nerd Fonts

- **Fecha:** 2026-10-09
- **Rama:** `feature/zsh-oh-my-posh-night-owl`
- **Tipo:** `feature`

---

## 1. Inconveniente / Requerimiento
Instalación y configuración completa de Zsh como shell predeterminada en Omarchy (Hyprland con atajo `Super + Enter`), integrando Oh My Posh con el tema `night-owl.omp.json` y solucionando problemas de visualización de glifos/íconos (caracteres mostrados como cuadrados).

## 2. Causa Raíz
- Zsh no estaba instalado a nivel de sistema y el usuario tenía asignado Bash.
- La terminal integrada del IDE y las aplicaciones Electron carecían de fallback estricto a Nerd Fonts y Symbols en la configuración de `fontconfig`, impidiendo renderizar glifos Powerline (`\ue0b0`, `\uf489`, etc.).

## 3. Solución Aplicada
1. Instalación de Oh My Posh en `~/.local/bin/oh-my-posh` y descarga del repositorio oficial de temas en `~/.cache/oh-my-posh/themes/`.
2. Instalación de Zsh (`sudo pacman -S zsh`) y asignación como shell por defecto del usuario (`chsh -s $(which zsh)`).
3. Creación y configuración de `~/.zshrc` con inicialización de Oh My Posh cargando `night-owl.omp.json`.
4. Descarga e instalación completa de las familias `JetBrainsMono Nerd Font` y `Symbols Nerd Font` en `~/.local/share/fonts/NerdFonts/`.
5. Configuración de `~/.config/fontconfig/fonts.conf` con enlace fuerte (`binding="strong"`) para la familia `monospace` y actualización de caché con `fc-cache -r`.
6. Configuración de la terminal integrada del IDE en `settings.json` con soporte explícito de Nerd Fonts.

## 4. Archivos Modificados
- `/home/dagudelo/.zshrc`
- `/home/dagudelo/.config/fontconfig/fonts.conf`
- `/home/dagudelo/.config/Antigravity IDE/User/settings.json`
- `/home/dagudelo/Code/omarchy-setup/.vscode/settings.json`
- `/home/dagudelo/.local/share/fonts/NerdFonts/*`

## 5. Validación
- Shell de usuario verificada en `/etc/passwd` apuntando a `/usr/bin/zsh`.
- Ejecución interactiva exitosa de Zsh con `oh-my-posh` v31.6.0.
- `fc-match monospace` resolviendo inmediatamente a `JetBrainsMonoNerdFont-Regular.ttf`.
- Apertura de terminal predeterminada (`foot`) con `Super + Enter` ejecutando Zsh.
