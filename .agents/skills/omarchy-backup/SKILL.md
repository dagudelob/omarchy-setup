---
name: omarchy-backup
description: >-
  Back up all Omarchy configuration, Hyprland dotfiles, installed packages, and user settings to the omarchy-setup git repository and push to GitHub (@dagudelob/omarchy-setup).
  Use whenever the user asks to save, back up, sync, or push their Omarchy changes, desktop setup, or dotfiles, or triggers phrases like "save changes", "backup omarchy", "save configuration", "push to github", "sync omarchy".
  Enforces automatic secret and credential scanning to prevent uploading private keys, tokens, or environment files.
---

# Omarchy Backup Skill

Safely backs up all user customizations made to Omarchy, Hyprland, terminals, shells, and package lists, audits staged files for sensitive data, and automatically synchronizes everything with the user's remote GitHub repository.

## Repository and Destination

- **Local directory:** `/home/dagudelo/Code/omarchy-setup`
- **Remote repository:** `https://github.com/dagudelob/omarchy-setup`
- **Main branch:** `main`

## Execution Workflow

Whenever the user asks to save changes, perform a backup, or sync with GitHub:

### Step 1: Run the automated backup script
Run the script with the `--push` flag from the repository directory:

```bash
/home/dagudelo/Code/omarchy-setup/backup.sh --push
```

The script automatically takes care of:
1. Exporting the updated list of official Arch Linux packages (`pkglist.txt`) and AUR packages (`pkglist-aur.txt`).
2. Syncing essential directories in `~/.config/`:
   - `hypr/` (keybindings, monitors, window rules, look & feel)
   - `omarchy/` (shell.json, themes, extensions, hooks)
   - Terminals (`kitty/`, `foot/`, `ghostty/`, `alacritty/`)
   - CLI tools and utilities (`fastfetch/`, `btop/`, `lazygit/`, `starship.toml`, `tmux/`, etc.)
3. Syncing shell configuration files (`~/.bashrc`, `~/.bash_profile`, `~/.zshrc`).
4. Automatically excluding temporary files, logs, `.env` files, and private keys.
5. Performing a strict security scan against GitHub token patterns (`ghp_`, `gho_`) and private keys before committing.
6. Creating a timestamped commit and pushing it to the `main` branch on GitHub.

### Step 2: Verify synchronization status
When the backup script finishes:
1. Inspect `git status` in `/home/dagudelo/Code/omarchy-setup` to confirm the working tree is clean.
2. Inform the user:
   - That changes were backed up and verified against secrets.
   - The number of modified files or if there were no pending changes.
   - Direct link to the repository: [https://github.com/dagudelob/omarchy-setup](https://github.com/dagudelob/omarchy-setup).

### Critical Security Rules
- **NEVER** commit `.env` files, database credentials, session tokens, or keys in `~/.ssh/`.
- The repository's `.gitignore` is active to reject these patterns.
- If the script aborts due to a detected secret pattern, show the flagged file to the user and request confirmation before taking any action.
