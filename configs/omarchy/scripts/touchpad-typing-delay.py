#!/usr/bin/env python3
"""
Surface Touchpad Typing Delay Daemon for Omarchy / Hyprland
- Uses Linux kernel input device grabbing (ioctl EVIOCGRAB) on the Type Cover touchpad.
- When any key is pressed on the keyboard:
    * Grabs the touchpad device exclusively (0 events reach Hyprland/libinput).
    * Absolutely zero cursor jump or accidental clicks/taps can happen.
- Releases the touchpad exactly TYPING_DELAY seconds after the last key is released.
- Zero CPU usage, zero IPC socket overhead, bulletproof reliability.
"""

import fcntl
import glob
import os
import select
import struct
import sys
import threading
import time

TYPING_DELAY = 0.5  # seconds
TOUCHPAD_IDENTIFIERS = ["Microsoft Surface Type Cover Touchpad"]
KEYBOARD_IDENTIFIERS = ["Microsoft Surface Type Cover Keyboard", "keyboard"]
EVIOCGRAB = 0x40044590

def find_devices_by_name(identifiers):
    devices = []
    for name_path in glob.glob("/sys/class/input/event*/device/name"):
        try:
            with open(name_path, "r", encoding="utf-8") as f:
                dev_name = f.read().strip()
                if any(k.lower() in dev_name.lower() for k in identifiers):
                    event_dir = os.path.basename(os.path.dirname(os.path.dirname(name_path)))
                    dev_path = f"/dev/input/{event_dir}"
                    if os.path.exists(dev_path):
                        devices.append((dev_path, dev_name))
        except Exception:
            continue
    return devices

class HardwareTouchpadManager:
    def __init__(self, delay=1.5):
        self.delay = delay
        self.last_key_time = 0.0
        self.is_grabbed = False
        self.touchpad_fd = -1
        self.lock = threading.Lock()
        self.cv = threading.Condition(self.lock)
        self.running = True

    def open_touchpad(self):
        touchpad_devs = find_devices_by_name(TOUCHPAD_IDENTIFIERS)
        if not touchpad_devs:
            return False
        touchpad_path, _ = touchpad_devs[0]
        try:
            if self.touchpad_fd >= 0:
                self.release_touchpad()
                os.close(self.touchpad_fd)
            self.touchpad_fd = os.open(touchpad_path, os.O_RDWR | os.O_NONBLOCK)
            return True
        except Exception:
            self.touchpad_fd = -1
            return False

    def grab_touchpad(self):
        if self.touchpad_fd < 0:
            if not self.open_touchpad():
                return
        try:
            fcntl.ioctl(self.touchpad_fd, EVIOCGRAB, 1)
            self.is_grabbed = True
        except Exception:
            self.open_touchpad()

    def release_touchpad(self):
        if self.touchpad_fd >= 0 and self.is_grabbed:
            try:
                fcntl.ioctl(self.touchpad_fd, EVIOCGRAB, 0)
            except Exception:
                pass
            self.is_grabbed = False

    def on_key_pressed(self):
        with self.lock:
            self.last_key_time = time.monotonic()
            if not self.is_grabbed:
                self.grab_touchpad()
            self.cv.notify_all()

    def timer_loop(self):
        while self.running:
            with self.lock:
                if not self.is_grabbed:
                    self.cv.wait()
                    continue

                elapsed = time.monotonic() - self.last_key_time
                remaining = self.delay - elapsed

                if remaining > 0:
                    self.cv.wait(timeout=remaining)
                    continue

                # Delay elapsed without new typing: release touchpad
                self.release_touchpad()

    def close(self):
        self.running = False
        with self.lock:
            self.release_touchpad()
            if self.touchpad_fd >= 0:
                try:
                    os.close(self.touchpad_fd)
                except Exception:
                    pass
                self.touchpad_fd = -1

def main():
    manager = HardwareTouchpadManager(delay=TYPING_DELAY)
    if not manager.open_touchpad():
        sys.exit(1)

    timer_thread = threading.Thread(target=manager.timer_loop, daemon=True)
    timer_thread.start()

    # struct input_event on 64-bit Linux: timeval (16 bytes), uint16 type, uint16 code, int32 value = 24 bytes
    event_fmt = "llHHI"
    event_size = struct.calcsize(event_fmt)
    EV_KEY = 0x01

    open_fds = {}

    def ensure_keyboard_fds():
        target_devs = find_devices_by_name(KEYBOARD_IDENTIFIERS)
        for dev_path, dev_name in target_devs:
            if dev_path not in open_fds:
                try:
                    fd = os.open(dev_path, os.O_RDONLY | os.O_NONBLOCK)
                    open_fds[dev_path] = fd
                except Exception:
                    pass

    ensure_keyboard_fds()
    if not open_fds:
        sys.exit(1)

    try:
        while True:
            rlist, _, _ = select.select(list(open_fds.values()), [], [], 2.0)
            if not rlist:
                ensure_keyboard_fds()
                continue

            for fd in rlist:
                try:
                    data = os.read(fd, event_size * 16)
                    if not data:
                        continue
                    for i in range(0, len(data), event_size):
                        chunk = data[i:i + event_size]
                        if len(chunk) < event_size:
                            continue
                        _, _, ev_type, _, val = struct.unpack(event_fmt, chunk)
                        # val: 1 (key down), 2 (key repeat)
                        if ev_type == EV_KEY and (val == 1 or val == 2):
                            manager.on_key_pressed()
                except (BlockingIOError, InterruptedError):
                    continue
                except Exception:
                    for p, f in list(open_fds.items()):
                        if f == fd:
                            try:
                                os.close(fd)
                            except Exception:
                                pass
                            del open_fds[p]
                            break
                    ensure_keyboard_fds()
    finally:
        manager.close()

if __name__ == "__main__":
    main()
