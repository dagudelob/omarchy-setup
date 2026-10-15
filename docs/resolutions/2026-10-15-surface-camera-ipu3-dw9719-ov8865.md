# Fix Surface Pro IPU3 Cameras (DW9719 VCM and OV8865 Mode Stalling)

- **Date:** 2026-10-15
- **Branch:** `fix/surface-camera-ipu3-dw9719-ov8865`
- **Type:** `fix`

---

## 1. Issue / Requirement
On a Microsoft Surface Pro running Arch Linux with the `linux-surface` kernel (6.19.8), neither camera worked in apps like Zoom or photo viewers:
- Initially, no cameras were detected (`cam -l` showed 0 available cameras).
- After fixing the initial enumeration, the front camera worked properly, but the rear camera displayed a solid green screen / freeze.

## 2. Root Cause
Two distinct kernel driver issues on the Intel IPU3 subsystem:
1. **DW9719 VCM Driver ID Table Missing:** In upstream kernel 6.19+, `dw9719` had its `i2c_device_id` table removed. On Surface devices using ACPI matching via `ipu-bridge`, the driver failed to bind to `i2c-INT347A:00-VCM`. Because IPU3 waits for all companion sub-devices to bind before establishing CSI-2 links, the bridge never created the media pipeline, preventing `libcamera` from discovering any cameras.
2. **OV8865 Stale Mode Stalling (Green Screen):** Once the VCM was bound, desktop services (WirePlumber/PipeWire) held the device runtime-active. The `ov8865` driver originally only wrote mode registers to hardware during runtime PM resume, not during `ov8865_s_stream`. As a result, resolution changes never reached hardware; the sensor streamed stale binned frames while IPU3 expected the newly negotiated format, causing zero-filled YUV buffers (displayed as a solid green screen).

## 3. Applied Solution
1. **Patched & Compiled `dw9719.ko`:** Restored `i2c_device_id dw9719_id_table[]` in `drivers/media/i2c/dw9719.c` with aliases for `dw9719` and `dw9718s`.
2. **Patched & Compiled `ov8865.ko` (PR #2169):** Added logic in `ov8865_s_stream` to reprogram the sensor hardware mode if the state changed while held powered, and balanced PM runtime references.
3. **Installed Updates:** Placed patched modules into `/lib/modules/$(uname -r)/updates/`, ran `depmod -a`, and rebooted.

## 4. Modified Files
- `/lib/modules/6.19.8-arch1-3-surface/updates/dw9719.ko`
- `/lib/modules/6.19.8-arch1-3-surface/updates/ov8865.ko`

## 5. Validation
- `cam -l` enumerates both internal cameras:
  - `Internal back camera (\_SB_.PCI0.I2C3.CAMR)` (OV8865)
  - `Internal front camera (\_SB_.PCI0.I2C2.CAMF)` (OV5693)
- Tested video and photo capture across both front and rear cameras in Zoom and native camera apps; video stream renders clean frames without green tints or freezing.
