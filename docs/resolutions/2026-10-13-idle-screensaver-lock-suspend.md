# Idle Configuration: Screensaver (2m), Lock/Display Off (5m), and Suspend (15m)

- **Date:** 2026-10-13
- **Branch:** `feature/idle-screensaver-lock-suspend`
- **Type:** `feature`

---

## 1. Issue / Requirement
Configure Omarchy idle timeouts so that after 2 minutes the screensaver starts, after 5 minutes the session locks and turns off the display, and after 15 minutes of inactivity the device automatically suspends.

## 2. Root Cause
Omarchy manages screensaver and lock timers via Quickshell in `shell.json`, but hibernation was unavailable (zRAM swap without persistent swap or boot hooks) and no default timeout was present for automatic system sleep after prolonged inactivity.

## 3. Applied Solution
1. Adjusted idle thresholds in `~/.config/omarchy/shell.json`:
   - `idle.screensaver`: `120` (2 minutes).
   - `idle.lock`: `300` (5 minutes, turns off display via DPMS).
2. Created executable monitor `~/.local/bin/omarchy-idle-suspend` that respects the *Stay Awake* state and executes `systemctl suspend` after 10 minutes of screen lock (15 minutes total inactivity).
3. Created and enabled user systemd service `omarchy-idle-suspend.service` for graphical session integration.

## 4. Modified Files
- `~/.config/omarchy/shell.json`
- `~/.local/bin/omarchy-idle-suspend`
- `~/.config/systemd/user/omarchy-idle-suspend.service`

## 5. Validation
- Realtime verification via `omarchy-shell idle status` confirming `screensaver: 120` and `lock: 300`.
- Verified active and running state of `omarchy-idle-suspend.service` via `systemctl --user status`.
