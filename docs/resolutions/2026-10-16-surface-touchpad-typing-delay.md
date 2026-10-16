# Surface Touchpad Hardware Typing Delay via EVIOCGRAB

- **Date:** 2026-10-16
- **Branch:** `fix/surface-touchpad-typing-delay`
- **Type:** `fix`

---

## 1. Issue / Requirement
On Microsoft Surface Type Cover, typing on the compact keyboard frequently leads to accidental palm touches on the touchpad, unexpectedly jumping the cursor and stealing focus while typing. Hyprland's native `disable_while_typing` has an unconfigurable, very short timeout (~500ms) and dynamic `hl.config` device toggles fail to detach hardware events in real time under Aquamarine. A reliable delay mechanism of 0.5s of inactivity was required.

## 2. Root Cause
In Hyprland 0.56.2 (Aquamarine backend), dynamic device toggles via IPC do not alter existing libinput event subscriptions for active input descriptors. Additionally, `libinput` hardcodes its disable-while-typing timeout into C source without exposure to user configuration.

## 3. Applied Solution
1. Developed a zero-overhead Python daemon (`~/.config/omarchy/scripts/touchpad-typing-delay.py`) that monitors keyboard events on `/dev/input/event*`.
2. When a keystroke occurs, it instantly claims exclusive access of the Type Cover touchpad via the Linux kernel's `ioctl(fd, EVIOCGRAB, 1)`. While grabbed, 0 events or touches reach Hyprland/libinput.
3. Automatically releases the grab (`ioctl(fd, EVIOCGRAB, 0)`) after exactly 0.5 seconds of inactivity.
4. Installed and enabled a persistent systemd user service (`touchpad-typing-delay.service`).

## 4. Modified Files
- `/home/dagudelo/.config/omarchy/scripts/touchpad-typing-delay.py`
- `/home/dagudelo/.config/systemd/user/touchpad-typing-delay.service`
- `/home/dagudelo/.config/hypr/input.lua`
- `configs/hypr/input.lua`
- `configs/omarchy/scripts/touchpad-typing-delay.py`
- `configs/systemd/user/touchpad-typing-delay.service`

## 5. Validation
- Verified with active typing across multiple windows: touchpad is completely inert while keys are pressed.
- Verified timer release: touchpad smoothly wakes up 0.5s after the last key press without cursor drift or jumps.
- Verified systemd status: active, running, consumes <6MB RSS and <0.1% CPU.
