# Exclude Modifier Keys and Reduce Typing Delay to 400ms

- **Date:** 2026-10-27
- **Branch:** `fix/exclude-modifier-keys-typing-delay`
- **Type:** `fix`

---

## 1. Issue / Requirement
When holding down modifier keys (`Shift`, `Ctrl`, `Alt`, `Super`) to perform mouse shortcuts (`Ctrl + Click`, `Shift + Click`, `Alt + Drag`), the typing delay daemon locked the touchpad, preventing mouse input from registering with modifiers unless a delay expired. The requirement was to reduce the typing delay to 400ms and exclude modifier keys that do not produce printable characters from triggering the touchpad lock.

## 2. Root Cause
The `touchpad-typing-delay.py` daemon captured all keyboard key events (`EV_KEY`) indiscriminately. Pressing and holding modifiers dispatched key-press and autorepeat events that continuously invoked `EVIOCGRAB` on the touchpad device, starving libinput/Hyprland of touchpad input while modifiers were held.

## 3. Applied Solution
1. Reduced `TYPING_DELAY` from 1.0s / 0.5s down to `0.4` seconds (400ms).
2. Added `EXCLUDED_KEYCODES` set covering `KEY_LEFTCTRL`, `KEY_RIGHTCTRL`, `KEY_LEFTSHIFT`, `KEY_RIGHTSHIFT`, `KEY_LEFTALT`, `KEY_RIGHTALT`, `KEY_LEFTMETA`, `KEY_RIGHTMETA`, `KEY_CAPSLOCK`, `KEY_COMPOSE`, and `KEY_FN`.
3. Implemented `on_modifier_pressed()` to immediately release any active touchpad grab when a modifier is pressed down, allowing instantaneous mouse and touchpad interactions.
4. Updated `/home/dagudelo/.config/systemd/user/touchpad-typing-delay.service` description, ran `systemctl --user daemon-reload`, and restarted the service.

## 4. Modified Files
- `/home/dagudelo/.config/omarchy/scripts/touchpad-typing-delay.py`
- `/home/dagudelo/Code/omarchy-setup/config/omarchy/scripts/touchpad-typing-delay.py`
- `/home/dagudelo/.config/systemd/user/touchpad-typing-delay.service`
- `/home/dagudelo/Code/omarchy-setup/docs/resolutions/2026-10-27-exclude-modifier-keys-typing-delay.md`

## 5. Validation
- Verified syntax, struct parsing (`llHHi`), and input event loop execution.
- Reloaded and restarted `touchpad-typing-delay.service` via `systemctl --user`.
- Confirmed service state is `active (running)` with zero journal errors.
