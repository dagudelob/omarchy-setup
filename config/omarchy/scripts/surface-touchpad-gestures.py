#!/usr/bin/env python3
"""
Surface Pro Ultra-Low-Latency Precision Touchpad Continuous Gestures for Omarchy:
- Zero-latency event loop with non-blocking asynchronous volume worker.
- 4-finger vertical swipe: Instant, 1:1 proportional volume slider with zero drift & zero runaway.
- Decoupled asynchronous OSD worker for fluid visual feedback without audio lag.
- 4-finger horizontal swipe: Next track (swipe right) / Previous track (swipe left).
- 4-finger tap: Pause / Resume audio & video playback toggle.
(3-finger tap is handled natively by libinput as BTN_MIDDLE for 0ms middle click)
"""

import os
import sys
import time
import math
import re
import shlex
import subprocess
import threading
import glob
import fcntl
import struct

def find_touchpad():
    for p in sorted(glob.glob("/dev/input/event*")):
        try:
            with open(p, "rb") as fd:
                buf = bytearray(128)
                fcntl.ioctl(fd.fileno(), 0x80004521 + (128 << 16), buf)
                if (buf[335 // 8] >> (335 % 8)) & 1:
                    return p
        except Exception:
            pass
    return None

def ensure_environment():
    if "OMARCHY_PATH" not in os.environ:
        os.environ["OMARCHY_PATH"] = "/usr/share/omarchy"

    path = os.environ.get("PATH", "")
    for bin_dir in ["/usr/share/omarchy/bin", f"{os.path.expanduser('~')}/.local/bin", "/usr/local/bin", "/usr/bin"]:
        if bin_dir not in path:
            path = f"{bin_dir}:{path}"
    os.environ["PATH"] = path

    resolve_wayland_display()

def resolve_wayland_display():
    runtime_dir = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    current = os.environ.get("WAYLAND_DISPLAY")
    if current and os.path.exists(f"{runtime_dir}/{current}"):
        return current
    try:
        sockets = sorted(glob.glob(f"{runtime_dir}/wayland-[0-9]*"), key=os.path.getmtime, reverse=True)
        sockets = [s for s in sockets if not s.endswith(".lock")]
        if sockets:
            disp = os.path.basename(sockets[0])
            os.environ["WAYLAND_DISPLAY"] = disp
            return disp
    except Exception:
        pass
    return current

def read_sink_volume():
    try:
        res = subprocess.check_output(
            ["pactl", "get-sink-volume", "@DEFAULT_SINK@"],
            stderr=subprocess.DEVNULL,
            text=True
        )
        for part in res.split():
            if part.endswith("%"):
                return float(part[:-1])
    except Exception:
        pass
    return 50.0

class OsdWorker(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.target_vol = None
        self.last_shown = -1
        self.wake_event = threading.Event()
        self.running = True

    def update(self, vol):
        self.target_vol = vol
        self.wake_event.set()

    def run(self):
        while self.running:
            self.wake_event.wait()
            self.wake_event.clear()

            target = self.target_vol
            if target is None:
                continue

            if target != self.last_shown:
                self.last_shown = target
                resolve_wayland_display()
                icon = "volume-muted" if target == 0 else "volume-high"
                subprocess.run(
                    ["omarchy-osd", "-i", icon, "-p", str(target)],
                    stderr=subprocess.DEVNULL
                )

            # Prevent saturating the quickshell IPC socket while user is actively swiping
            time.sleep(0.02)

class VolumeWorker(threading.Thread):
    def __init__(self, osd_worker):
        super().__init__(daemon=True)
        self.osd_worker = osd_worker
        self.target_vol = None
        self.last_applied = -1
        self.wake_event = threading.Event()
        self.running = True

    def update(self, vol):
        self.target_vol = max(0.0, min(100.0, vol))
        self.wake_event.set()

    def run(self):
        while self.running:
            self.wake_event.wait()
            self.wake_event.clear()

            target = self.target_vol
            if target is None:
                continue

            int_vol = int(round(target))
            if int_vol != self.last_applied:
                self.last_applied = int_vol
                # Direct pactl set-sink-volume (fast ~1-2ms, audio changes immediately)
                subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "0"], stderr=subprocess.DEVNULL)
                subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{int_vol}%"], stderr=subprocess.DEVNULL)

                # Show Omarchy OSD asynchronously so audio latency is never blocked
                self.osd_worker.update(int_vol)

            # Rate limiter between audio volume updates (60+ FPS responsiveness)
            time.sleep(0.015)

class QuadtapWatcher(threading.Thread):
    def __init__(self, controller):
        super().__init__(daemon=True)
        self.controller = controller
        self.running = True
        self.last_tap_time = 0.0

    def trigger_play_pause(self):
        resolve_wayland_display()
        # 1. Direct MPRIS DBus call via busctl (instant ~5ms, identical to headphone click)
        try:
            cmd = "busctl --user list --acquired 2>/dev/null | grep 'org.mpris.MediaPlayer2.' | awk '{print $1}'"
            services = subprocess.check_output(cmd, shell=True, text=True).strip().split()
            if services:
                for svc in services:
                    subprocess.run(
                        ["busctl", "--user", "call", svc, "/org/mpris/MediaPlayer2", "org.mpris.MediaPlayer2.Player", "PlayPause"],
                        stderr=subprocess.DEVNULL
                    )
                subprocess.run(["omarchy-shell", "-q", "media", "status"], stderr=subprocess.DEVNULL)
                return
        except Exception:
            pass

        # 2. Fallback to omarchy-shell media playPause
        subprocess.run(["omarchy-shell", "media", "playPause"], stderr=subprocess.DEVNULL)

    def run(self):
        EVENT_FORMAT = "llHHi"
        EVENT_SIZE = struct.calcsize(EVENT_FORMAT)

        while self.running:
            dev_path = find_touchpad()
            if not dev_path:
                time.sleep(2)
                continue

            try:
                with open(dev_path, "rb") as fd:
                    # 4-finger state
                    quad_active = False
                    quad_start = 0.0

                    # Centroid & movement tracking
                    start_x = None
                    start_y = None
                    curr_x = None
                    curr_y = None
                    max_dist = 0.0

                    while self.running:
                        data = fd.read(EVENT_SIZE)
                        if not data or len(data) < EVENT_SIZE:
                            break
                        _, _, ev_type, ev_code, ev_value = struct.unpack(EVENT_FORMAT, data)

                        # EV_ABS = 3 (Only track ABS_X=0 and ABS_Y=1)
                        if ev_type == 3:
                            if ev_code == 0:  # ABS_X
                                curr_x = ev_value
                                if quad_active:
                                    if start_x is None:
                                        start_x = curr_x
                                    dx = curr_x - start_x
                                    dy = (curr_y - start_y) if (curr_y is not None and start_y is not None) else 0.0
                                    dist = math.hypot(dx, dy)
                                    if dist > max_dist:
                                        max_dist = dist
                            elif ev_code == 1:  # ABS_Y
                                curr_y = ev_value
                                if quad_active:
                                    if start_y is None:
                                        start_y = curr_y
                                    dy = curr_y - start_y
                                    dx = (curr_x - start_x) if (curr_x is not None and start_x is not None) else 0.0
                                    dist = math.hypot(dx, dy)
                                    if dist > max_dist:
                                        max_dist = dist

                        # EV_KEY = 1
                        elif ev_type == 1:
                            now = time.time()

                            # BTN_TOOL_QUADTAP = 335 (4 fingers -> Pause/Resume)
                            if ev_code == 335:
                                if ev_value == 1:
                                    quad_active = True
                                    quad_start = now
                                    start_x = curr_x
                                    start_y = curr_y
                                    max_dist = 0.0
                                elif ev_value == 0:
                                    if quad_active:
                                        quad_active = False
                                        duration = now - quad_start
                                        with self.controller.lock:
                                            is_swiping = (self.controller.mode is not None or self.controller.action_triggered)
                                        if (now - self.last_tap_time) > 0.25 and 0.03 <= duration <= 0.50 and max_dist < 220.0 and not is_swiping:
                                            self.last_tap_time = now
                                            print(f"[gestures] 4-finger tap detected ({int(duration*1000)}ms, dist={int(max_dist)}px) -> Play/Pause", flush=True)
                                            threading.Thread(target=self.trigger_play_pause, daemon=True).start()

                            # BTN_TOUCH = 330: safety cleanup when all fingers leave
                            elif ev_code == 330 and ev_value == 0:
                                quad_active = False
            except Exception:
                time.sleep(1)

class SurfaceGestureController:
    def __init__(self):
        self.lock = threading.Lock()
        self.osd_worker = OsdWorker()
        self.osd_worker.start()
        self.worker = VolumeWorker(self.osd_worker)
        self.worker.start()
        self.quadtap_watcher = QuadtapWatcher(self)
        self.quadtap_watcher.start()

        self.current_vol = read_sink_volume()
        self.active_fingers = 0
        self.start_time = 0.0
        self.start_vol = self.current_vol
        self.cum_dx = 0.0
        self.cum_dy = 0.0
        self.mode = None
        self.action_triggered = False

        # Sensitivity: ~0.85 gives instant, snappy response
        self.sensitivity = 0.85

    def on_begin(self, fingers):
        with self.lock:
            self.active_fingers = fingers
            self.start_time = time.time()
            self.cum_dx = 0.0
            self.cum_dy = 0.0
            self.mode = None
            self.action_triggered = False
            if fingers == 4:
                # Fast asynchronous volume sync without blocking touch begin
                self.start_vol = self.current_vol
                threading.Thread(target=self._sync_volume, daemon=True).start()

    def _sync_volume(self):
        vol = read_sink_volume()
        with self.lock:
            if self.mode is None:
                self.start_vol = vol
                self.current_vol = vol

    def on_update(self, fingers, dx, dy):
        with self.lock:
            if fingers != 4:
                return

            self.cum_dx += dx
            self.cum_dy += dy
            dist = math.hypot(self.cum_dx, self.cum_dy)

            # Instant direction detection with ultra-low deadzone (2.0 units)
            if self.mode is None and dist >= 2.0:
                if abs(self.cum_dy) >= abs(self.cum_dx):
                    self.mode = 'vertical'
                else:
                    self.mode = 'horizontal'

            # Continuous 1:1 Proportional Volume Control (Vertical)
            if self.mode == 'vertical':
                delta_vol = (-self.cum_dy) * self.sensitivity
                target = self.start_vol + delta_vol
                bounded = max(0.0, min(100.0, target))
                self.current_vol = bounded
                self.worker.update(bounded)

            # Track Navigation (Horizontal)
            elif self.mode == 'horizontal' and not self.action_triggered:
                if self.cum_dx >= 18.0:
                    self.action_triggered = True
                    resolve_wayland_display()
                    threading.Thread(
                        target=lambda: subprocess.run(["omarchy-shell", "media", "next"], stderr=subprocess.DEVNULL),
                        daemon=True
                    ).start()
                elif self.cum_dx <= -18.0:
                    self.action_triggered = True
                    resolve_wayland_display()
                    threading.Thread(
                        target=lambda: subprocess.run(["omarchy-shell", "media", "previous"], stderr=subprocess.DEVNULL),
                        daemon=True
                    ).start()

    def on_end(self, fingers):
        with self.lock:
            duration = time.time() - self.start_time
            dist = math.hypot(self.cum_dx, self.cum_dy)
            mode = self.mode
            was_triggered = self.action_triggered

            self.active_fingers = 0
            self.mode = None

        if fingers == 4:
            # Ensure final volume is displayed on OSD when gesture ends
            if mode == 'vertical':
                final_vol = int(round(self.current_vol))
                self.osd_worker.update(final_vol)

            # Fallback 4-finger Tap detection from libinput swipe end
            elif mode is None and not was_triggered and dist < 6.0 and duration < 0.30:
                now = time.time()
                if (now - self.quadtap_watcher.last_tap_time) > 0.35:
                    self.quadtap_watcher.last_tap_time = now
                    resolve_wayland_display()
                    threading.Thread(
                        target=lambda: subprocess.run(["omarchy-shell", "media", "playPause"], stderr=subprocess.DEVNULL),
                        daemon=True
                    ).start()

def main():
    ensure_environment()
    controller = SurfaceGestureController()

    cmd = shlex.split("stdbuf -oL -- libinput debug-events")
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1
        )
    except Exception as e:
        sys.exit(1)

    for line in proc.stdout or []:
        if 'GESTURE_' not in line or ' +' not in line:
            continue

        try:
            split1, split2 = line.split(' +', maxsplit=1)
            parts = split1.split()
            if len(parts) < 2 or not parts[1].startswith('GESTURE_'):
                continue
            event_type = parts[1][8:]

            tokens = split2.split(maxsplit=2)
            fingers = int(tokens[1]) if len(tokens) > 1 and tokens[1].isdigit() else 0

            if event_type == 'SWIPE_BEGIN':
                controller.on_begin(fingers)
            elif event_type == 'SWIPE_UPDATE':
                params = tokens[2].rstrip() if len(tokens) > 2 else ''
                clean_nums = re.split(r'[^-.\d]+', params)
                if len(clean_nums) >= 2 and clean_nums[0] and clean_nums[1]:
                    dx = float(clean_nums[0])
                    dy = float(clean_nums[1])
                    controller.on_update(fingers, dx, dy)
            elif event_type in ('SWIPE_END', 'HOLD_END'):
                controller.on_end(fingers)
        except Exception:
            continue

if __name__ == "__main__":
    main()
