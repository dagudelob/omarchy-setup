# Enable and Configure Bluetooth Service on Surface Pro

- **Date:** 2026-10-10
- **Branch:** `fix/surface-bluetooth-enable`
- **Type:** `fix`

---

## 1. Issue / Requirement
The Bluetooth adapter on the Surface Pro was unavailable and did not start automatically with the system, preventing wireless peripherals from connecting.

## 2. Root Cause
The `bluetooth.service` systemd daemon from `bluez` was disabled by default following system setup, leaving controller `hci0` unpowered.

## 3. Applied Solution
1. Checked Bluetooth controller state with `rfkill` ensuring no hardware or software blocks were active.
2. Enabled and started system service with autostart:
   ```bash
   sudo systemctl enable --now bluetooth.service
   ```
3. Validated controller state with `bluetoothctl show` confirming `Powered: yes` and registered audio endpoints.

## 4. Modified Files
- `/usr/lib/systemd/system/bluetooth.service` (enabled and started via systemctl).

## 5. Validation
- Executed `systemctl status bluetooth` confirming `active (running)`.
- Verified with `rfkill list bluetooth` and `bluetoothctl show` that controller `hci0` is operational and discoverable.
