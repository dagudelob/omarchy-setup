#!/usr/bin/env python3
"""
Touchpad Typing Delay Daemon for Omarchy / Hyprland (Microsoft Surface Type Cover)
- Disables the touchpad instantly whenever a keystroke is pressed.
- Keeps the touchpad disabled until exactly TYPING_DELAY seconds have elapsed
  without any keyboard activity.
- Uses direct Linux evdev + Hyprland UNIX IPC socket for sub-millisecond response
  and virtually zero CPU overhead.
"""

import glob
import os
import select
import socket
import struct
import sys
import threading
import time

TYPING_DELAY = 1.0  # seconds
TOUCHPAD_DEVICE_NAME = "microsoft-surface-type-cover-touchpad"
KEYBOARD_IDENTIFIERS = ["Microsoft Surface Type Cover Keyboard", "keyboard"]

def get_hypr_socket():
    xdg_runtime = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    his = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    
    if not his:
        # Fallback: find any hypr socket dir
        hypr_base = os.path.join(xdg_runtime, "hypr")
        if os.path.isdir(hypr_base):
            dirs = [d for d in os.listdir(hypr_base) if os.path.isdir(os.path.join(hypr_base, d))]
            if dirs:
                his = dirs[0]
                
    if his:
        sock_path = os.path.join(xdg_runtime, "hypr", his, ".socket.sock")
        if os.path.exists(sock_path):
            return sock_path
    return None

def send_hypr_command(cmd_str):
    sock_path = get_hypr_socket()
    if not sock_path:
        return False
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            s.connect(sock_path)
            s.sendall(cmd_str.encode("utf-8"))
            s.recv(1024)
        return True
    except Exception:
        return False

def set_touchpad_state(enabled: bool):
    state_str = "true" if enabled else "false"
    cmd = f'eval hl.config({{ device = {{ {{ name = "{TOUCHPAD_DEVICE_NAME}", enabled = {state_str} }} }} }})'
    return send_hypr_command(cmd)

def find_keyboard_event_devices():
    devices = []
    for name_path in glob.glob("/sys/class/input/event*/device/name"):
        try:
            with open(name_path, "r", encoding="utf-8") as f:
                dev_name = f.read().strip()
                if any(k.lower() in dev_name.lower() for k in KEYBOARD_IDENTIFIERS):
                    event_dir = os.path.basename(os.path.dirname(os.path.dirname(name_path)))
                    dev_path = f"/dev/input/{event_dir}"
                    if os.path.exists(dev_path):
                        devices.append((dev_path, dev_name))
        except Exception:
            continue
    return devices

class TouchpadDelayManager:
    def __init__(self, delay=1.0):
        self.delay = delay
        self.last_key_time = 0.0
        self.touchpad_enabled = True
        self.lock = threading.Lock()
        self.cv = threading.Condition(self.lock)
        self.running = True

    def on_key_pressed(self):
        with self.lock:
            self.last_key_time = time.monotonic()
            if self.touchpad_enabled:
                self.touchpad_enabled = False
                set_touchpad_state(False)
            self.cv.notify_all()

    def timer_loop(self):
        while self.running:
            with self.lock:
                if self.touchpad_enabled:
                    # Wait until next keystroke
                    self.cv.wait()
                    continue

                elapsed = time.monotonic() - self.last_key_time
                remaining = self.delay - elapsed

                if remaining > 0:
                    self.cv.wait(timeout=remaining)
                    continue

                # Delay elapsed with no new keys pressed -> re-enable touchpad
                self.touchpad_enabled = True
                set_touchpad_state(True)

def main():
    manager = TouchpadDelayManager(delay=TYPING_DELAY)

    # Start timer thread
    timer_thread = threading.Thread(target=manager.timer_loop, daemon=True)
    timer_thread.start()

    # Format of struct input_event on 64-bit Linux: timeval (2 * long = 16 bytes), uint16 type, uint16 code, int32 value = 24 bytes
    event_fmt = "llHHI"
    event_size = struct.calcsize(event_fmt)
    EV_KEY = 0x01

    open_fds = {}

    def ensure_fds():
        target_devs = find_keyboard_event_devices()
        for dev_path, dev_name in target_devs:
            if dev_path not in open_fds:
                try:
                    fd = os.open(dev_path, os.O_RDONLY | os.O_NONBLOCK)
                    open_fds[dev_path] = fd
                except Exception:
                    pass

    ensure_fds()
    if not open_fds:
        sys.exit(1)

    try:
        while True:
            # Poll open file descriptors
            rlist, _, _ = select.select(list(open_fds.values()), [], [], 2.0)
            if not rlist:
                ensure_fds()
                continue

            for fd in rlist:
                try:
                    data = os.read(fd, event_size * 16)
                    if not data:
                        continue
                    # Parse input_event chunks
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
                    # Re-scan if an FD was unplugged
                    for p, f in list(open_fds.items()):
                        if f == fd:
                            try:
                                os.close(fd)
                            except Exception:
                                pass
                            del open_fds[p]
                            break
                    ensure_fds()
    finally:
        set_touchpad_state(True)

if __name__ == "__main__":
    main()
