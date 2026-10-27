#!/usr/bin/env python3
"""
Backend services for Surface Pen Studio (omarchy-surface-pen).
Manages:
- Persistent user settings (~/.config/omarchy/surface-pen/settings.json)
- Hyprland tablet config & top-button bindings (~/.config/hypr/surface-pen.lua)
- Xournal++ stylus, pressure curve, cursor, and barrel/eraser mappings (~/.config/xournalpp/settings.xml)
- IPTSD hardware digitizer & palm rejection (/etc/iptsd.d/90-omarchy-pen.conf)
- BlueZ Bluetooth status and GATT Battery reporting
- Omarchy active theme palette (~/.local/state/omarchy/current/theme/colors.toml)
"""

import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

HOME = Path.home()
APP_DIR = HOME / ".config" / "omarchy" / "surface-pen"
SETTINGS_FILE = APP_DIR / "settings.json"
HYPR_PEN_LUA = HOME / ".config" / "hypr" / "surface-pen.lua"
XOURNAL_SETTINGS = HOME / ".config" / "xournalpp" / "settings.xml"
IPTSD_CONF_PATH = Path("/etc/iptsd.d/90-omarchy-pen.conf")
APPLY_IPTSD_SCRIPT = APP_DIR / "apply-iptsd.sh"
THEME_COLORS_TOML = HOME / ".local" / "state" / "omarchy" / "current" / "theme" / "colors.toml"

BUTTON_PRESETS = {
    "xournalpp": ("Abrir Xournal++ (Notas y PDF)", "uwsm-app -- xournalpp"),
    "pen_studio": ("Abrir Surface Pen Studio", "omarchy-surface-pen"),
    "screenshot": ("Captura de pantalla (Región)", "omarchy-capture-screenshot"),
    "screenshot_full": ("Captura de pantalla completa", "omarchy-capture-screenshot fullscreen"),
    "omarchy_menu": ("Abrir Menú de Omarchy", "omarchy-menu"),
    "voice_dictation": ("Dictado por voz (Voxtype)", "voxtype record toggle"),
    "lock_screen": ("Bloquear pantalla", "omarchy-system-lock"),
    "custom": ("Comando personalizado...", ""),
    "disabled": ("Desactivado (Sin acción)", ""),
}

BARREL_ACTIONS = {
    "selectRegion": "Seleccionar región (Lazo libre)",
    "selectRect": "Seleccionar rectángulo",
    "eraser": "Borrador mientras se mantiene",
    "hand": "Desplazar lienzo (Mano)",
    "none": "Clic derecho estándar / Sin cambio",
}

ERASER_MODES = {
    "standard": "Borrador estándar (Por área)",
    "deleteStroke": "Borrar trazo completo al tocarlo",
    "whiteout": "Corrector blanco",
    "none": "Predeterminado de la aplicación",
}

CURSOR_TYPES = {
    "dot": "Punto discreto (Recomendado)",
    "big": "Cursor grande de alta visibilidad",
    "arrow": "Flecha estándar",
    "none": "Ocultar cursor al escribir",
}

DEFAULT_SETTINGS = {
    "pressure_sensitivity": True,
    "pressure_level": 6,          # 1 (Softest) .. 12 (Firmest), default 6 (Linear)
    "minimum_pressure": 0.05,     # 0.01 .. 0.25
    "tip_distance": 0.0,          # 0.0 .. 0.5 cm tilt compensation
    "single_click_preset": "xournalpp",
    "single_click_custom": "uwsm-app -- xournalpp",
    "double_click_preset": "screenshot",
    "double_click_custom": "omarchy-capture-screenshot",
    "long_press_preset": "pen_studio",
    "long_press_custom": "omarchy-surface-pen",
    "barrel_button_action": "selectRegion",
    "eraser_mode": "standard",
    "left_handed": False,
    "relative_input": False,
    "disable_on_stylus": True,
    "disable_on_palm": True,
    "disable_touchscreen": False,
    "stylus_cursor_type": "dot",
    "eraser_visibility": "hover",
    "last_known_battery": None,
    "last_battery_updated": None,
    "pen_mac": "D4:FA:41:5A:78:08",
}


def level_to_gamma(level: int) -> float:
    """
    Convert Windows Surface App pressure level (1..12) to a power-curve exponent gamma.
    Level 1  -> gamma = 0.45 (very soft: light touch produces thick strokes)
    Level 6  -> gamma = 1.00 (linear response)
    Level 12 -> gamma = 2.20 (very firm: requires strong pressure for max stroke)
    """
    lvl = max(1, min(12, int(level)))
    if lvl <= 6:
        # 1 -> 0.45, 6 -> 1.00
        return round(0.45 + (lvl - 1) * (0.55 / 5.0), 3)
    else:
        # 6 -> 1.00, 12 -> 2.20
        return round(1.00 + (lvl - 6) * (1.20 / 6.0), 3)


def level_to_xournal_multiplier(level: int) -> float:
    """
    Convert pressure level (1..12) to Xournal++ pressureMultiplier.
    Soft levels (<6) amplify pressure (>1.0); firm levels (>6) attenuate (<1.0).
    """
    lvl = max(1, min(12, int(level)))
    if lvl <= 6:
        return round(1.75 - (lvl - 1) * (0.75 / 5.0), 2)
    else:
        return round(1.00 - (lvl - 6) * (0.45 / 6.0), 2)


def load_settings() -> dict:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    settings = dict(DEFAULT_SETTINGS)
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                if isinstance(saved, dict):
                    settings.update(saved)
        except Exception:
            pass

    # Sync initial state from /etc/iptsd.d/90-omarchy-pen.conf if present
    if IPTSD_CONF_PATH.exists():
        try:
            text = IPTSD_CONF_PATH.read_text(encoding="utf-8")
            m_stylus = re.search(r"DisableOnStylus\s*=\s*(true|false)", text, re.I)
            if m_stylus:
                settings["disable_on_stylus"] = m_stylus.group(1).lower() == "true"
            m_palm = re.search(r"DisableOnPalm\s*=\s*(true|false)", text, re.I)
            if m_palm:
                settings["disable_on_palm"] = m_palm.group(1).lower() == "true"
            m_tip = re.search(r"TipDistance\s*=\s*([0-9.]+)", text, re.I)
            if m_tip:
                settings["tip_distance"] = float(m_tip.group(1))
        except Exception:
            pass

    return settings


def save_settings(settings: dict) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


def resolve_button_command(settings: dict, prefix: str) -> str:
    preset = settings.get(f"{prefix}_preset", "disabled")
    if preset == "disabled":
        return ""
    if preset == "custom":
        return settings.get(f"{prefix}_custom", "").strip()
    return BUTTON_PRESETS.get(preset, ("", ""))[1]


def apply_hyprland_settings(settings: dict) -> tuple[bool, str]:
    """
    Generate ~/.config/hypr/surface-pen.lua and reload Hyprland.
    """
    left_handed = "true" if settings.get("left_handed", False) else "false"
    relative_input = "true" if settings.get("relative_input", False) else "false"

    cmd_single = resolve_button_command(settings, "single_click")
    cmd_double = resolve_button_command(settings, "double_click")
    cmd_long = resolve_button_command(settings, "long_press")

    lines = [
        "-- Auto-generated by Surface Pen Studio (omarchy-surface-pen)",
        "-- Do not edit manually if you use the Surface Pen Studio GUI.",
        "",
        "hl.config({",
        "  input = {",
        "    tablet = {",
        f"      left_handed = {left_handed},",
        f"      relative_input = {relative_input},",
        "    },",
        "  },",
        "})",
        "",
        "-- Floating window rules for Surface Pen Studio",
        'o.window("com.omarchy.SurfacePenStudio", { float = true })',
        'o.window("com.omarchy.SurfacePenStudio", { center = true })',
        'o.window("com.omarchy.SurfacePenStudio", { size = { 940, 680 } })',
        "",
        "-- Surface Pen Bluetooth Top Button Shortcuts",
        "-- Hardware emits: Single-click = SUPER+F20, Double-click = SUPER+F19, Long-press = SUPER+F18",
        'hl.unbind("SUPER + F20")',
        'hl.unbind("SUPER + F19")',
        'hl.unbind("SUPER + F18")',
        'hl.unbind("XF86Launch1")',
        "",
    ]

    if cmd_single:
        escaped = cmd_single.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'o.bind("SUPER + F20", "Surface Pen: Single Click", "{escaped}", {{ locked = true }})')
    if cmd_double:
        escaped = cmd_double.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'o.bind("SUPER + F19", "Surface Pen: Double Click", "{escaped}", {{ locked = true }})')
    if cmd_long:
        escaped = cmd_long.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'o.bind("SUPER + F18", "Surface Pen: Long Press", "{escaped}", {{ locked = true }})')

    lines.append("")

    try:
        HYPR_PEN_LUA.parent.mkdir(parents=True, exist_ok=True)
        HYPR_PEN_LUA.write_text("\n".join(lines), encoding="utf-8")
        subprocess.run(["hyprctl", "reload"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
        err = subprocess.check_output(["hyprctl", "configerrors"], text=True, timeout=3).strip()
        if err:
            return False, f"Hyprland config error: {err}"
        return True, "Atajos y opciones de Hyprland aplicados en vivo."
    except Exception as e:
        return False, str(e)


def apply_xournalpp_settings(settings: dict) -> tuple[bool, str]:
    """
    Update ~/.config/xournalpp/settings.xml preserving user layout and comments.
    """
    if not XOURNAL_SETTINGS.exists():
        return True, "Xournal++ aún no tiene archivo de configuración (se aplicará cuando se inicie)."

    try:
        content = XOURNAL_SETTINGS.read_text(encoding="utf-8")

        def replace_prop(xml_text: str, prop_name: str, val: str) -> str:
            pattern = rf'(<property\s+name="{re.escape(prop_name)}"\s+value=")[^"]*("\s*/>)'
            return re.sub(pattern, rf"\g<1>{val}\g<2>", xml_text)

        pressure_on = "true" if settings.get("pressure_sensitivity", True) else "false"
        min_press = f"{float(settings.get('minimum_pressure', 0.05)):.2f}"
        mult = f"{level_to_xournal_multiplier(settings.get('pressure_level', 6)):.2f}"
        cursor = settings.get("stylus_cursor_type", "dot")
        eraser_vis = settings.get("eraser_visibility", "hover")
        disable_touch = "true" if settings.get("disable_on_stylus", True) else "false"
        barrel_tool = settings.get("barrel_button_action", "selectRegion")
        eraser_mode = settings.get("eraser_mode", "standard")

        content = replace_prop(content, "pressureSensitivity", pressure_on)
        content = replace_prop(content, "minimumPressure", min_press)
        content = replace_prop(content, "pressureMultiplier", mult)
        content = replace_prop(content, "stylusCursorType", cursor)
        content = replace_prop(content, "eraserVisibility", eraser_vis)

        # Update <data name="stylus"> tool attribute
        content = re.sub(
            r'(<data\s+name="stylus">\s*<attribute\s+name="tool"\s+type="string"\s+value=")[^"]*("\s*/>)',
            rf"\g<1>{barrel_tool}\g<2>",
            content,
        )
        # Update <data name="eraser"> eraserMode attribute
        content = re.sub(
            r'(<data\s+name="eraser">\s*<attribute\s+name="eraserMode"\s+type="string"\s+value=")[^"]*("\s*/>)',
            rf"\g<1>{eraser_mode}\g<2>",
            content,
        )
        # Update <data name="touch"> disableTouch attribute
        content = re.sub(
            r'(<attribute\s+name="disableTouch"\s+type="boolean"\s+value=")[^"]*("\s*/>)',
            rf"\g<1>{disable_touch}\g<2>",
            content,
        )

        XOURNAL_SETTINGS.write_text(content, encoding="utf-8")
        return True, "Configuración sincronizada con Xournal++."
    except Exception as e:
        return False, f"Error actualizando Xournal++: {e}"


def generate_iptsd_conf(settings: dict) -> str:
    disable_touch = "true" if settings.get("disable_touchscreen", False) else "false"
    disable_on_palm = "true" if settings.get("disable_on_palm", True) else "false"
    disable_on_stylus = "true" if settings.get("disable_on_stylus", True) else "false"
    tip_distance = f"{float(settings.get('tip_distance', 0.0)):.2f}"

    return "\n".join([
        "# Generated by Surface Pen Studio (omarchy-surface-pen)",
        "[Touchscreen]",
        f"Disable = {disable_touch}",
        f"DisableOnPalm = {disable_on_palm}",
        f"DisableOnStylus = {disable_on_stylus}",
        "",
        "[Stylus]",
        "Disable = false",
        f"TipDistance = {tip_distance}",
        "",
    ])


def apply_iptsd_settings(settings: dict) -> tuple[bool, str]:
    """
    Write /etc/iptsd.d/90-omarchy-pen.conf using pkexec helper and restart iptsd.
    """
    conf_text = generate_iptsd_conf(settings)
    if IPTSD_CONF_PATH.exists():
        try:
            if IPTSD_CONF_PATH.read_text(encoding="utf-8").strip() == conf_text.strip():
                return True, "El digitalizador IPTSD ya tiene esta configuración activa."
        except Exception:
            pass

    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".conf", delete=False) as tmp:
            tmp.write(conf_text)
            tmp_path = tmp.name

        res = subprocess.run(
            ["pkexec", str(APPLY_IPTSD_SCRIPT), tmp_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

        if res.returncode == 0:
            return True, "Digitalizador IPTSD actualizado y reiniciado correctamente."
        return False, f"No se pudo aplicar en IPTSD: {res.stderr.strip() or 'Cancelado por el usuario'}"
    except Exception as e:
        return False, f"Error ejecutando pkexec: {e}"


def get_iptsd_status() -> dict:
    status = {
        "running": False,
        "unit": "",
        "stylus_device": False,
        "touch_device": False,
    }
    try:
        out = subprocess.check_output(
            ["systemctl", "list-units", "iptsd@*", "--no-legend", "--plain"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=2,
        )
        for line in out.splitlines():
            parts = line.split()
            if parts and "iptsd@" in parts[0]:
                status["unit"] = parts[0]
                status["running"] = "active" in line or "running" in line
                break
    except Exception:
        pass

    try:
        devs = Path("/proc/bus/input/devices").read_text(encoding="utf-8")
        status["stylus_device"] = "IPTSD Virtual Stylus" in devs or "IPTS 045E:001F" in devs
        status["touch_device"] = "IPTSD Virtual Touchscreen" in devs
    except Exception:
        pass

    return status


def get_pen_bluetooth_status(settings: dict) -> dict:
    mac = settings.get("pen_mac", "D4:FA:41:5A:78:08")
    info = {
        "mac": mac,
        "name": "Surface Pen",
        "paired": False,
        "connected": False,
        "trusted": False,
        "battery": settings.get("last_known_battery"),
        "battery_updated": settings.get("last_battery_updated"),
    }

    try:
        devs_out = subprocess.check_output(
            ["bluetoothctl", "devices"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=2,
        )
        for line in devs_out.splitlines():
            if "Surface Pen" in line:
                parts = line.split()
                if len(parts) >= 2:
                    mac = parts[1]
                    info["mac"] = mac
                    break
    except Exception:
        pass

    try:
        bt_out = subprocess.check_output(
            ["bluetoothctl", "info", mac],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=2,
        )
        info["paired"] = "Paired: yes" in bt_out
        info["connected"] = "Connected: yes" in bt_out
        info["trusted"] = "Trusted: yes" in bt_out

        # Parse Battery Percentage: 0x5f (95)
        m_bat = re.search(r"Battery Percentage:\s*(?:0x[0-9a-fA-F]+\s*)?\((\d+)\)", bt_out)
        if m_bat:
            bat_val = int(m_bat.group(1))
            info["battery"] = bat_val
            info["battery_updated"] = time.strftime("%H:%M")
            settings["last_known_battery"] = bat_val
            settings["last_battery_updated"] = info["battery_updated"]
            save_settings(settings)
    except Exception:
        pass

    # Also check BlueZ DBus Battery1 interface directly if not found in bluetoothctl
    if info["battery"] is None:
        dbus_path = "/org/bluez/hci0/dev_" + mac.replace(":", "_")
        try:
            bus_out = subprocess.check_output(
                ["busctl", "get-property", "org.bluez", dbus_path, "org.bluez.Battery1", "Percentage"],
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=1,
            ).strip()
            # Format: "y 85"
            parts = bus_out.split()
            if len(parts) == 2 and parts[1].isdigit():
                bat_val = int(parts[1])
                info["battery"] = bat_val
                info["battery_updated"] = time.strftime("%H:%M")
                settings["last_known_battery"] = bat_val
                settings["last_battery_updated"] = info["battery_updated"]
                save_settings(settings)
        except Exception:
            pass

    return info


def load_omarchy_theme() -> dict:
    palette = {
        "background": "#0f1117",
        "lighter_background": "#1a1d26",
        "foreground": "#e5e9f0",
        "accent": "#437ea7",
        "cyan": "#23dae7",
        "green": "#41cce9",
        "red": "#d4866f",
        "yellow": "#c8887d",
        "muted": "#686163",
    }
    if THEME_COLORS_TOML.exists():
        try:
            for line in THEME_COLORS_TOML.read_text(encoding="utf-8").splitlines():
                m = re.match(r"^\s*([a-zA-Z0-9_]+)\s*=\s*\"(#[0-9a-fA-F]{6})\"", line)
                if m:
                    palette[m.group(1)] = m.group(2)
        except Exception:
            pass
    return palette


if __name__ == "__main__":
    import sys
    if "--self-test" in sys.argv:
        s = load_settings()
        save_settings(s)
        ok_h, msg_h = apply_hyprland_settings(s)
        ok_x, msg_x = apply_xournalpp_settings(s)
        print("Hyprland:", ok_h, msg_h)
        print("Xournal++:", ok_x, msg_x)
        print("IPTSD status:", get_iptsd_status())
        print("Pen BT status:", get_pen_bluetooth_status(s))
        sys.exit(0 if (ok_h and ok_x) else 1)
