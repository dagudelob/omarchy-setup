# Install Linear as Omarchy Web App

- **Date:** 2026-11-26
- **Branch:** `feature/linear-webapp`
- **Type:** `feature`

---

## 1. Issue / Requirement
Install Linear on Omarchy so it is accessible from the app launcher (`SUPER + SPACE`) and stays automatically up to date when running `omarchy update`.

## 2. Root Cause
Linear does not provide an official native Linux desktop client (only macOS, Windows, and web). Installing it as an Omarchy web app ensures Linear loads the latest version directly from `https://linear.app`, while `omarchy update` (`omarchy-update-system-pkgs`) keeps the underlying Chromium-based browser and `omarchy-launch-webapp` runner updated.

## 3. Applied Solution
Installed Linear using Omarchy's built-in web app installer, which automatically fetched the high-resolution `apple-touch-icon.png` from `https://linear.app` and generated the desktop entry:

```bash
omarchy-webapp-install "Linear" "https://linear.app" ""
```

## 4. Modified Files
- `/home/dagudelo/.local/share/applications/Linear.desktop`
- `/home/dagudelo/.local/share/icons/hicolor/256x256/apps/linear.png`
- `/home/dagudelo/Code/omarchy-setup/docs/resolutions/2026-11-26-linear-webapp.md`

## 5. Validation
- Verified `/home/dagudelo/.local/share/applications/Linear.desktop` exists with `Exec=omarchy-launch-webapp "https://linear.app"` and `StartupWMClass=chrome-linear.app__-Default`.
- Verified `/home/dagudelo/.local/share/icons/hicolor/256x256/apps/linear.png` is a valid 180×180 PNG image.
