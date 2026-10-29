# Fix Intel IPU3 Cameras in Google Meet and Brave on Microsoft Surface

- **Date:** 2026-10-28
- **Branch:** `fix/surface-camera-google-meet-ipu3`
- **Type:** `fix`

---

## 1. Issue / Requirement
On Microsoft Surface running Omarchy Linux, both front (`ov5693`) and rear (`ov8865`) cameras worked on camera testing websites (`probarcamara.com`), but in Google Meet (Google Chrome) the front camera failed with a continuous white hardware LED and the error *"Camera might be blocked"*. Furthermore, Brave Browser failed to recognize either camera (*"Camera not found"*). Both cameras needed to work seamlessly in Google Meet without losing access to either sensor.

## 2. Root Cause
1. **Google Meet WebRTC sensor-mode renegotiation crash:** While camera test sites stream stably at 1280x720 (where `libcamera` keeps `ov5693` at its full native `2592x1944` resolution), Google Meet dynamically renegotiates the PipeWire stream to 640x360 after ~0.8 seconds. When requesting 640x360, upstream `libcamera` switched the sensor to binned mode `1296x972`, triggering hardware CSI-2/DMA synchronization errors in kernel driver `ipu3-cio2` (`CSI-2 receiver port 1: frame sync error`, `payload length is 1617408, received 0`).
2. **libcamera calculateBDSHeight assertion abort:** In `libcamera` 0.7.2, calculating Bayer Downscaler height for small input sizes underflowed `unsigned int minIFHeight`, triggering `Assertion '!(__hi < __lo)' failed` in `std::clamp`.
3. **Brave Browser missing PipeWire flags and portal permissions:** Brave on Wayland did not have `~/.config/brave-flags.conf` with `--enable-features=WebRTCPipeWireCamera`, preventing it from enumerating PipeWire camera nodes.

## 3. Applied Solution
1. **Patched and compiled `libcamera` (v0.7.2) in user-space (`~/.local/libcamera-patched/`):**
   - In `src/libcamera/pipeline/ipu3/ipu3.cpp`, forced `rawSize` in `IPU3CameraConfiguration::validate()` to always use full sensor resolution (`cio2_.sensor()->resolution()`), keeping the sensor at native `2592x1944` and eliminating the unstable `1296x972` sensor mode.
   - In `PipelineHandlerIPU3::generateConfiguration()`, fixed advertised `streamFormats` for `Viewfinder`/`VideoRecording` to `1280x720`, ensuring PipeWire only advertises 1280x720 and browsers handle lower WebRTC simulcast resolutions via software scaling without stopping the hardware stream.
   - In `src/libcamera/pipeline/ipu3/imgu.cpp`, protected `minIFHeight` against underflow when `iif.height < kIFMaxCropHeight`.
2. **Configured WirePlumber user override:**
   - Deployed `~/.config/systemd/user/wireplumber.service.d/override.conf` injecting `LD_LIBRARY_PATH`, `LIBCAMERA_IPA_PROXY_PATH`, `LIBCAMERA_IPA_MODULE_PATH`, and `LIBCAMERA_IPA_CONFIG_PATH` pointing to `~/.local/libcamera-patched/`.
3. **Configured Brave and Chrome flags & Portal Permissions:**
   - Created `~/.config/brave-flags.conf` and updated `~/.config/brave-origin-flags.conf`, `~/.config/chrome-flags.conf`, and `~/.config/chromium-flags.conf` with `--enable-features=WebRTCPipeWireCamera,WebRtcPipeWireCamera`.
   - Granted camera access to Chrome and Brave in XDG Desktop Portal `PermissionStore`.

## 4. Modified Files
- `~/.local/libcamera-patched/libcamera.so.0.7.2`
- `~/.local/libcamera-patched/libcamera-base.so.0.7.2`
- `~/.local/libcamera-patched/libcamera/ipa/ipa_ipu3.so`
- `~/.local/libcamera-patched/libexec/libcamera/ipu3_ipa_proxy`
- `~/.config/systemd/user/wireplumber.service.d/override.conf`
- `~/.config/brave-flags.conf`
- `~/.config/brave-origin-flags.conf`
- `~/.config/chrome-flags.conf`
- `~/.config/chromium-flags.conf`
- `patches/libcamera-v0.7.2-ipu3-stable-sensor-mode.patch`

## 5. Validation
- Verified with `pw-dump Node` that both `Built-in Front Camera` and `Built-in Back Camera` are registered and active.
- Verified frame capture via `gst-launch-1.0 pipewiresrc` on both cameras with 0 kernel errors.
- Verified both cameras stream successfully in Google Meet on Google Chrome and Brave Browser.
