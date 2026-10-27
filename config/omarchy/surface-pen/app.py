#!/usr/bin/env python3
"""
Surface Pen Studio for Omarchy (omarchy-surface-pen)
Native GTK4 + Libadwaita + Cairo Control Center for the Microsoft Surface Pen.
"""

import math
import subprocess
import sys
import threading
from pathlib import Path

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, GLib, Gtk

import backends


def hex_to_rgb(hex_str: str) -> tuple[float, float, float]:
    h = hex_str.lstrip("#")
    if len(h) != 6:
        return (0.14, 0.85, 0.91)
    return tuple(int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4))


class PressureCurveGraph(Gtk.DrawingArea):
    """
    Renders the interactive Windows Surface App style pressure curve (Levels 1..12)
    and plots the real-time stylus pressure dot on the curve.
    """

    def __init__(self, palette: dict):
        super().__init__()
        self.palette = palette
        self.level = 6
        self.min_pressure = 0.05
        self.live_input = 0.0
        self.set_content_width(240)
        self.set_content_height(210)
        self.set_draw_func(self._on_draw)

    def set_params(self, level: int, min_pressure: float):
        self.level = level
        self.min_pressure = min_pressure
        self.queue_draw()

    def set_live_input(self, raw_p: float):
        self.live_input = max(0.0, min(1.0, raw_p))
        self.queue_draw()

    def map_pressure(self, raw_p: float) -> float:
        if raw_p <= self.min_pressure:
            return 0.0
        norm = (raw_p - self.min_pressure) / max(0.01, 1.0 - self.min_pressure)
        gamma = backends.level_to_gamma(self.level)
        return max(0.0, min(1.0, math.pow(norm, gamma)))

    def _on_draw(self, _area, cr, width, height):
        pad_l, pad_r, pad_t, pad_b = 34, 18, 16, 28
        w = max(10, width - pad_l - pad_r)
        h = max(10, height - pad_t - pad_b)

        bg_r, bg_g, bg_b = hex_to_rgb(self.palette.get("lighter_background", "#1a1d26"))
        fg_r, fg_g, fg_b = hex_to_rgb(self.palette.get("foreground", "#23dae7"))
        ac_r, ac_g, ac_b = hex_to_rgb(self.palette.get("cyan", "#23dae7"))

        # Rounded card background
        cr.set_source_rgba(bg_r, bg_g, bg_b, 0.9)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        # Grid lines
        cr.set_line_width(1.0)
        cr.set_source_rgba(fg_r, fg_g, fg_b, 0.14)
        for i in range(5):
            gx = pad_l + (w * i / 4.0)
            gy = pad_t + (h * i / 4.0)
            cr.move_to(gx, pad_t)
            cr.line_to(gx, pad_t + h)
            cr.move_to(pad_l, gy)
            cr.line_to(pad_l + w, gy)
        cr.stroke()

        # Linear diagonal reference (dashed)
        cr.set_dash([4.0, 4.0])
        cr.set_source_rgba(fg_r, fg_g, fg_b, 0.28)
        cr.move_to(pad_l, pad_t + h)
        cr.line_to(pad_l + w, pad_t)
        cr.stroke()
        cr.set_dash([])

        # Active pressure curve fill & stroke
        cr.move_to(pad_l, pad_t + h)
        steps = 60
        for i in range(steps + 1):
            x_val = i / float(steps)
            y_val = self.map_pressure(x_val)
            px = pad_l + x_val * w
            py = pad_t + h - y_val * h
            cr.line_to(px, py)

        cr.set_line_width(2.8)
        cr.set_source_rgba(ac_r, ac_g, ac_b, 0.95)
        cr.stroke_preserve()

        cr.line_to(pad_l + w, pad_t + h)
        cr.close_path()
        cr.set_source_rgba(ac_r, ac_g, ac_b, 0.16)
        cr.fill()

        # Live pressure dot if pressing
        if self.live_input > 0.005:
            out_y = self.map_pressure(self.live_input)
            dx = pad_l + self.live_input * w
            dy = pad_t + h - out_y * h
            cr.arc(dx, dy, 5.5, 0, 2 * math.pi)
            cr.set_source_rgba(1.0, 0.45, 0.35, 1.0)
            cr.fill()

        # Labels
        cr.set_source_rgba(fg_r, fg_g, fg_b, 0.7)
        cr.select_font_face("Sans", 0, 0)
        cr.set_font_size(10.5)
        cr.move_to(pad_l, height - 8)
        cr.show_text("Fuerza física (0% → 100%)")

        gamma = backends.level_to_gamma(self.level)
        cr.move_to(pad_l + 6, pad_t + 14)
        cr.show_text(f"Nivel {self.level}/12  (γ = {gamma:.2f})")


class InkTestCanvas(Gtk.DrawingArea):
    """
    Interactive Stylus Test Canvas using Gtk.GestureStylus (with mouse fallback).
    Supports variable stroke width via pressure curve, tilt display, and physical rear eraser!
    """

    def __init__(self, curve_graph: PressureCurveGraph, on_telemetry, palette: dict):
        super().__init__()
        self.curve_graph = curve_graph
        self.on_telemetry = on_telemetry
        self.palette = palette
        self.strokes = []  # List of {"color": (r,g,b), "points": [(x, y, width)], "eraser": bool}
        self.current_stroke = None
        self.ink_color = hex_to_rgb(palette.get("cyan", "#23dae7"))
        self.hover_pos = None
        self.hover_is_eraser = False

        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_content_width(420)
        self.set_content_height(260)
        self.set_draw_func(self._on_draw)

        # Stylus controller (native Wayland tablet/IPTSD events)
        self.stylus = Gtk.GestureStylus.new()
        self.stylus.connect("proximity", self._on_stylus_proximity)
        self.stylus.connect("down", self._on_stylus_down)
        self.stylus.connect("motion", self._on_stylus_motion)
        self.stylus.connect("up", self._on_stylus_up)
        self.add_controller(self.stylus)

        # Mouse / Touchpad drag fallback so the canvas can also be tested without stylus
        self.drag = Gtk.GestureDrag.new()
        self.drag_start_pt = (0.0, 0.0)
        self.drag.connect("drag-begin", self._on_drag_begin)
        self.drag.connect("drag-update", self._on_drag_update)
        self.drag.connect("drag-end", self._on_drag_end)
        self.add_controller(self.drag)

    def _on_drag_begin(self, _gesture, x, y):
        if self.current_stroke is not None:
            return
        self.drag_start_pt = (x, y)
        mapped_p = self.curve_graph.map_pressure(0.5)
        self.curve_graph.set_live_input(0.5)
        width = 1.2 + mapped_p * 11.5
        self.current_stroke = {"color": self.ink_color, "points": [(x, y, width)]}
        self.strokes.append(self.current_stroke)
        self.on_telemetry("Touchpad / Ratón (50% sim)", 0.5, 0.0, 0.0)
        self.queue_draw()

    def _on_drag_update(self, _gesture, ox, oy):
        if self.current_stroke is None:
            return
        x = self.drag_start_pt[0] + ox
        y = self.drag_start_pt[1] + oy
        mapped_p = self.curve_graph.map_pressure(0.5)
        width = 1.2 + mapped_p * 11.5
        self.current_stroke["points"].append((x, y, width))
        self.queue_draw()

    def _on_drag_end(self, _gesture, _ox, _oy):
        self.current_stroke = None
        self.curve_graph.set_live_input(0.0)
        self.on_telemetry("Listo", 0.0, 0.0, 0.0)
        self.queue_draw()

    def clear_canvas(self):
        self.strokes.clear()
        self.current_stroke = None
        self.queue_draw()

    def set_ink_color(self, rgb: tuple[float, float, float]):
        self.ink_color = rgb

    def _extract_stylus_state(self, gesture: Gtk.GestureStylus):
        tool = gesture.get_device_tool()
        tool_type = tool.get_tool_type() if tool else Gdk.DeviceToolType.PEN
        is_eraser = tool_type == Gdk.DeviceToolType.ERASER

        ok_p, pressure = gesture.get_axis(Gdk.AxisUse.PRESSURE)
        if not ok_p or pressure is None:
            pressure = 0.5

        ok_tx, tx = gesture.get_axis(Gdk.AxisUse.XTILT)
        ok_ty, ty = gesture.get_axis(Gdk.AxisUse.YTILT)
        tilt_x = tx if (ok_tx and tx is not None) else 0.0
        tilt_y = ty if (ok_ty and ty is not None) else 0.0

        return is_eraser, float(pressure), float(tilt_x), float(tilt_y)

    def _on_stylus_proximity(self, gesture, x, y):
        is_eraser, pressure, tx, ty = self._extract_stylus_state(gesture)
        self.hover_pos = (x, y)
        self.hover_is_eraser = is_eraser
        tool_label = "Borrador trasero" if is_eraser else "Punta (En proximidad)"
        self.on_telemetry(tool_label, 0.0, tx, ty)
        self.curve_graph.set_live_input(0.0)
        self.queue_draw()

    def _on_stylus_down(self, gesture, x, y):
        is_eraser, pressure, tx, ty = self._extract_stylus_state(gesture)
        self.hover_pos = (x, y)
        self.hover_is_eraser = is_eraser
        mapped_p = self.curve_graph.map_pressure(pressure)
        self.curve_graph.set_live_input(pressure)

        if is_eraser:
            self._erase_near(x, y, radius=18.0 + mapped_p * 20.0)
            self.on_telemetry("Borrador físico activo", pressure, tx, ty)
        else:
            width = 1.2 + mapped_p * 11.5
            self.current_stroke = {
                "color": self.ink_color,
                "points": [(x, y, width)],
            }
            self.strokes.append(self.current_stroke)
            self.on_telemetry("Punta dibujando", pressure, tx, ty)
        self.queue_draw()

    def _on_stylus_motion(self, gesture, x, y):
        is_eraser, pressure, tx, ty = self._extract_stylus_state(gesture)
        self.hover_pos = (x, y)
        self.hover_is_eraser = is_eraser
        mapped_p = self.curve_graph.map_pressure(pressure)
        self.curve_graph.set_live_input(pressure)

        if is_eraser:
            self._erase_near(x, y, radius=18.0 + mapped_p * 20.0)
            self.on_telemetry("Borrador físico activo", pressure, tx, ty)
        elif self.current_stroke is not None:
            width = 1.2 + mapped_p * 11.5
            self.current_stroke["points"].append((x, y, width))
            self.on_telemetry("Punta dibujando", pressure, tx, ty)
        self.queue_draw()

    def _on_stylus_up(self, gesture, x, y):
        self.current_stroke = None
        self.curve_graph.set_live_input(0.0)
        self.on_telemetry("Listo", 0.0, 0.0, 0.0)
        self.queue_draw()

    def _erase_near(self, ex: float, ey: float, radius: float):
        r2 = radius * radius
        remaining = []
        for stroke in self.strokes:
            kept_pts = [pt for pt in stroke["points"] if (pt[0] - ex) ** 2 + (pt[1] - ey) ** 2 > r2]
            if len(kept_pts) >= 2:
                stroke["points"] = kept_pts
                remaining.append(stroke)
        self.strokes = remaining

    def _on_draw(self, _area, cr, width, height):
        # Dark notebook canvas background with subtle dot grid
        cr.set_source_rgba(0.06, 0.07, 0.09, 1.0)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        # Subtle dot grid
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.10)
        step = 24
        for gx in range(step, int(width), step):
            for gy in range(step, int(height), step):
                cr.arc(gx, gy, 1.0, 0, 2 * math.pi)
                cr.fill()

        # Hint watermark when empty
        if not self.strokes:
            cr.set_source_rgba(1.0, 1.0, 1.0, 0.28)
            cr.select_font_face("Sans", 0, 0)
            cr.set_font_size(13.0)
            cr.move_to(24, height / 2 - 8)
            cr.show_text("Escribe o dibuja aquí con tu Surface Pen para probar la presión.")
            cr.move_to(24, height / 2 + 14)
            cr.show_text("Voltea el lápiz y usa la parte trasera para probar el borrador físico.")

        # Draw strokes
        cr.set_line_cap(1)  # Round cap
        cr.set_line_join(1)
        for stroke in self.strokes:
            r, g, b = stroke["color"]
            pts = stroke["points"]
            if len(pts) == 1:
                x, y, w = pts[0]
                cr.set_source_rgba(r, g, b, 0.95)
                cr.arc(x, y, w / 2.0, 0, 2 * math.pi)
                cr.fill()
            else:
                cr.set_source_rgba(r, g, b, 0.95)
                for i in range(len(pts) - 1):
                    x1, y1, w1 = pts[i]
                    x2, y2, w2 = pts[i + 1]
                    cr.set_line_width((w1 + w2) * 0.5)
                    cr.move_to(x1, y1)
                    cr.line_to(x2, y2)
                    cr.stroke()

        # Draw eraser circle indicator when hovering with rear eraser
        if self.hover_pos and self.hover_is_eraser:
            hx, hy = self.hover_pos
            cr.set_source_rgba(1.0, 0.45, 0.45, 0.75)
            cr.set_line_width(1.5)
            cr.arc(hx, hy, 20.0, 0, 2 * math.pi)
            cr.stroke()


class SurfacePenWindow(Adw.ApplicationWindow):
    def __init__(self, app: Adw.Application):
        super().__init__(application=app, title="Surface Pen Studio")
        self.set_default_size(940, 680)

        self.settings = backends.load_settings()
        self.palette = backends.load_omarchy_theme()
        self._apply_theme_css()

        # Root layout with ToastOverlay & ToolbarView
        self.toast_overlay = Adw.ToastOverlay.new()
        self.set_content(self.toast_overlay)

        toolbar_view = Adw.ToolbarView.new()
        self.toast_overlay.set_child(toolbar_view)

        header = Adw.HeaderBar.new()
        self.view_stack = Adw.ViewStack.new()

        switcher = Adw.ViewSwitcher.new()
        switcher.set_stack(self.view_stack)
        switcher.set_policy(Adw.ViewSwitcherPolicy.WIDE)
        header.set_title_widget(switcher)

        # Quick test / launch Xournal++ button in header
        btn_notes = Gtk.Button.new_with_label("Abrir Notas")
        btn_notes.add_css_class("suggested-action")
        btn_notes.set_tooltip_text("Abrir Xournal++ con la configuración actual")
        btn_notes.connect("clicked", lambda *_: subprocess.Popen(["uwsm-app", "--", "xournalpp"]))
        header.pack_end(btn_notes)

        toolbar_view.add_top_bar(header)
        toolbar_view.set_content(self.view_stack)

        # Build the 4 pages
        self._build_device_page()
        self._build_pressure_page()
        self._build_buttons_page()
        self._build_touch_page()

        # Initial status refresh
        self.refresh_hardware_status()

    def _apply_theme_css(self):
        css_provider = Gtk.CssProvider()
        accent = self.palette.get("cyan", "#23dae7")
        css = f"""
        .pen-badge {{
            padding: 4px 10px;
            border-radius: 999px;
            font-weight: bold;
            font-size: 0.85em;
        }}
        .pen-card {{
            border-radius: 12px;
            padding: 12px;
        }}
        .swatch-btn {{
            min-width: 26px;
            min-height: 26px;
            border-radius: 999px;
            padding: 0;
        }}
        """
        css_provider.load_from_string(css)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def show_toast(self, message: str):
        toast = Adw.Toast.new(message)
        toast.set_timeout(2)
        self.toast_overlay.add_toast(toast)

    # ------------------------------------------------------------------
    # TAB 1: DISPOSITIVO Y BATERÍA
    # ------------------------------------------------------------------
    def _build_device_page(self):
        page = Adw.PreferencesPage.new()

        # Group 1: Surface Pen Bluetooth & Battery
        grp_bt = Adw.PreferencesGroup.new()
        grp_bt.set_title("Microsoft Surface Pen (Bluetooth y Batería)")
        grp_bt.set_description(
            "El lápiz utiliza Bluetooth Low Energy (BLE) para el botón superior y el reporte de batería, "
            "mientras que la punta escribe directamente por inducción electromagnética en la pantalla."
        )

        self.row_bt_status = Adw.ActionRow.new()
        self.row_bt_status.set_title("Surface Pen")
        self.row_bt_status.set_subtitle("Consultando estado Bluetooth...")
        self.lbl_bt_badge = Gtk.Label.new("...")
        self.lbl_bt_badge.add_css_class("pen-badge")
        self.row_bt_status.add_suffix(self.lbl_bt_badge)
        grp_bt.add(self.row_bt_status)

        self.row_battery = Adw.ActionRow.new()
        self.row_battery.set_title("Nivel de Batería (Pila AAAA)")
        self.row_battery.set_subtitle("Servicio GATT Battery (0x180f)")
        self.lbl_battery = Gtk.Label.new("--%")
        self.lbl_battery.add_css_class("title-3")
        self.row_battery.add_suffix(self.lbl_battery)
        grp_bt.add(self.row_battery)

        row_bt_actions = Adw.ActionRow.new()
        row_bt_actions.set_title("Acciones de Conexión")
        row_bt_actions.set_subtitle("Presiona el botón superior del lápiz para despertarlo y actualizar su batería")

        btn_refresh = Gtk.Button.new_with_label("Actualizar Estado")
        btn_refresh.set_valign(Gtk.Align.CENTER)
        btn_refresh.connect("clicked", lambda *_: self.refresh_hardware_status(notify=True))
        row_bt_actions.add_suffix(btn_refresh)

        btn_connect = Gtk.Button.new_with_label("Conectar Bluetooth")
        btn_connect.set_valign(Gtk.Align.CENTER)
        btn_connect.connect("clicked", self._on_reconnect_bt)
        row_bt_actions.add_suffix(btn_connect)
        grp_bt.add(row_bt_actions)

        page.add(grp_bt)

        # Group 2: IPTSD Digitizer
        grp_ipts = Adw.PreferencesGroup.new()
        grp_ipts.set_title("Digitalizador de Pantalla (Intel Precise Touch y Stylus)")
        grp_ipts.set_description("Motor en espacio de usuario (iptsd) encargado de presión, inclinación y rechazo de palma.")

        self.row_ipts_status = Adw.ActionRow.new()
        self.row_ipts_status.set_title("Servicio IPTSD (045E:001F)")
        self.row_ipts_status.set_subtitle("Verificando unidad systemd...")
        self.lbl_ipts_badge = Gtk.Label.new("...")
        self.lbl_ipts_badge.add_css_class("pen-badge")
        self.row_ipts_status.add_suffix(self.lbl_ipts_status_widget())
        grp_ipts.add(self.row_ipts_status)

        page.add(grp_ipts)

        # Group 3: Active Profile Summary
        grp_summary = Adw.PreferencesGroup.new()
        grp_summary.set_title("Resumen de tu Configuración Actual")
        self.row_summary_curve = Adw.ActionRow.new()
        self.row_summary_curve.set_title("Sensibilidad y Mano Dominante")
        grp_summary.add(self.row_summary_curve)

        self.row_summary_shortcuts = Adw.ActionRow.new()
        self.row_summary_shortcuts.set_title("Atajos del Botón Superior")
        grp_summary.add(self.row_summary_shortcuts)
        page.add(grp_summary)

        self.view_stack.add_titled_with_icon(
            page, "device", "Dispositivo", "input-tablet-symbolic"
        )

    def lbl_ipts_status_widget(self):
        return self.lbl_ipts_badge

    def _on_reconnect_bt(self, _btn):
        mac = self.settings.get("pen_mac", "D4:FA:41:5A:78:08")
        self.show_toast("Intentando conectar con el Surface Pen...")

        def worker():
            subprocess.run(["bluetoothctl", "connect", mac], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            GLib.idle_add(lambda: self.refresh_hardware_status(notify=True))

        threading.Thread(target=worker, daemon=True).start()

    def refresh_hardware_status(self, notify: bool = False):
        bt = backends.get_pen_bluetooth_status(self.settings)
        ipts = backends.get_iptsd_status()

        mac = bt["mac"]
        if bt["connected"]:
            self.row_bt_status.set_subtitle(f"MAC: {mac}  •  Conectado activamente")
            self.lbl_bt_badge.set_text("Conectado")
        elif bt["paired"]:
            self.row_bt_status.set_subtitle(
                f"MAC: {mac}  •  Vinculado (En reposo BLE de ahorro de energía)"
            )
            self.lbl_bt_badge.set_text("Vinculado (BLE)")
        else:
            self.row_bt_status.set_subtitle(f"MAC: {mac}  •  No emparejado")
            self.lbl_bt_badge.set_text("Sin vincular")

        if bt["battery"] is not None:
            upd = f" (leído a las {bt['battery_updated']})" if bt.get("battery_updated") else ""
            self.lbl_battery.set_text(f"{bt['battery']}%")
            self.row_battery.set_subtitle(f"Batería en buen estado{upd}")
        else:
            self.lbl_battery.set_text("BLE Standby")
            self.row_battery.set_subtitle(
                "Haz 1 clic en el botón superior del lápiz y pulsa «Actualizar Estado» para leer el %"
            )

        if ipts["running"]:
            self.row_ipts_status.set_subtitle(
                f"Unidad activa: {ipts['unit']}  •  Stylus virtual detectado"
            )
            self.lbl_ipts_badge.set_text("Activo (OK)")
        else:
            self.row_ipts_status.set_subtitle("El servicio iptsd no está corriendo actualmente")
            self.lbl_ipts_badge.set_text("Inactivo")

        # Update summary rows
        lvl = self.settings.get("pressure_level", 6)
        hand = "Zurdo (Izquierda)" if self.settings.get("left_handed") else "Diestro (Derecha)"
        palm = "Activado" if self.settings.get("disable_on_stylus") else "Desactivado"
        self.row_summary_curve.set_subtitle(
            f"Curva de presión: Nivel {lvl}/12  •  Mano: {hand}  •  Ignorar táctil al escribir: {palm}"
        )

        s1 = backends.BUTTON_PRESETS.get(self.settings.get("single_click_preset", "xournalpp"), ("Personalizado", ""))[0]
        s2 = backends.BUTTON_PRESETS.get(self.settings.get("double_click_preset", "screenshot"), ("Personalizado", ""))[0]
        self.row_summary_shortcuts.set_subtitle(f"1 Clic: {s1}   |   Doble Clic: {s2}")

        if notify:
            self.show_toast("Estado del hardware actualizado")

    # ------------------------------------------------------------------
    # TAB 2: PRESIÓN Y LIENZO DE PRUEBA (SURFACE APP STYLE)
    # ------------------------------------------------------------------
    def _build_pressure_page(self):
        scrolled = Gtk.ScrolledWindow.new()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        clamp = Adw.Clamp.new()
        clamp.set_maximum_size(900)
        clamp.set_margin_top(16)
        clamp.set_margin_bottom(16)
        clamp.set_margin_start(16)
        clamp.set_margin_end(16)
        scrolled.set_child(clamp)

        main_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 16)
        clamp.set_child(main_box)

        # Top split: Left = Curve Graph & Sliders, Right = Live Ink Canvas
        split_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 16)
        split_box.set_homogeneous(False)
        main_box.append(split_box)

        # --- LEFT COLUMN: Pressure Curve & Sliders ---
        left_card = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
        left_card.set_size_request(330, -1)
        split_box.append(left_card)

        lbl_curve_title = Gtk.Label.new("Curva de Sensibilidad (1 – 12)")
        lbl_curve_title.add_css_class("title-4")
        lbl_curve_title.set_halign(Gtk.Align.START)
        left_card.append(lbl_curve_title)

        self.curve_graph = PressureCurveGraph(self.palette)
        self.curve_graph.set_params(
            self.settings.get("pressure_level", 6),
            self.settings.get("minimum_pressure", 0.05),
        )
        left_card.append(self.curve_graph)

        # Level 1..12 Slider
        lbl_lvl = Gtk.Label.new("Nivel de dureza (1 = Muy suave, 6 = Natural, 12 = Muy firme):")
        lbl_lvl.set_halign(Gtk.Align.START)
        lbl_lvl.add_css_class("caption")
        left_card.append(lbl_lvl)

        self.scale_level = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, 12, 1)
        self.scale_level.set_draw_value(True)
        self.scale_level.set_digits(0)
        self.scale_level.set_value(self.settings.get("pressure_level", 6))
        for mark in (1, 6, 12):
            self.scale_level.add_mark(mark, Gtk.PositionType.BOTTOM, str(mark))
        self.scale_level.connect("value-changed", self._on_pressure_params_changed)
        left_card.append(self.scale_level)

        # Minimum Pressure Deadzone Slider
        lbl_minp = Gtk.Label.new("Umbral mínimo de activación (Deadzone):")
        lbl_minp.set_halign(Gtk.Align.START)
        lbl_minp.add_css_class("caption")
        left_card.append(lbl_minp)

        self.scale_minp = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0.01, 0.25, 0.01)
        self.scale_minp.set_draw_value(True)
        self.scale_minp.set_digits(2)
        self.scale_minp.set_value(self.settings.get("minimum_pressure", 0.05))
        self.scale_minp.connect("value-changed", self._on_pressure_params_changed)
        left_card.append(self.scale_minp)

        # TipDistance Tilt Compensation Slider
        lbl_tip = Gtk.Label.new("Compensación de inclinación (TipDistance cm):")
        lbl_tip.set_halign(Gtk.Align.START)
        lbl_tip.add_css_class("caption")
        left_card.append(lbl_tip)

        self.scale_tip = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0.0, 0.40, 0.02)
        self.scale_tip.set_draw_value(True)
        self.scale_tip.set_digits(2)
        self.scale_tip.set_value(self.settings.get("tip_distance", 0.0))
        self.scale_tip.connect("value-changed", self._on_pressure_params_changed)
        left_card.append(self.scale_tip)

        btn_save_pressure = Gtk.Button.new_with_label("Guardar y Sincronizar con Apps")
        btn_save_pressure.add_css_class("suggested-action")
        btn_save_pressure.connect("clicked", self._on_save_pressure_clicked)
        left_card.append(btn_save_pressure)

        # --- RIGHT COLUMN: Live Ink Test Canvas ---
        right_card = Gtk.Box.new(Gtk.Orientation.VERTICAL, 8)
        right_card.set_hexpand(True)
        split_box.append(right_card)

        header_row = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 10)
        right_card.append(header_row)

        lbl_canvas = Gtk.Label.new("Lienzo de Prueba en Vivo (Punta + Borrador)")
        lbl_canvas.add_css_class("title-4")
        lbl_canvas.set_halign(Gtk.Align.START)
        lbl_canvas.set_hexpand(True)
        header_row.append(lbl_canvas)

        # Color swatches
        swatch_colors = [
            ("Cyan", (0.14, 0.85, 0.91)),
            ("Blanco", (0.95, 0.96, 0.98)),
            ("Coral", (0.98, 0.48, 0.40)),
            ("Verde", (0.30, 0.88, 0.58)),
            ("Ámbar", (0.98, 0.80, 0.32)),
        ]
        for name, rgb in swatch_colors:
            b = Gtk.Button.new_with_label("●")
            b.set_tooltip_text(f"Color: {name}")
            b.connect("clicked", lambda _b, c=rgb: self.ink_canvas.set_ink_color(c))
            header_row.append(b)

        btn_clear = Gtk.Button.new_with_label("Limpiar")
        btn_clear.connect("clicked", lambda *_: self.ink_canvas.clear_canvas())
        header_row.append(btn_clear)

        # Telemetry bar (Tool + Live Pressure Progress + Tilt)
        telemetry_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 12)
        right_card.append(telemetry_box)

        self.lbl_tool_state = Gtk.Label.new("Herramienta: Listo")
        self.lbl_tool_state.add_css_class("caption")
        telemetry_box.append(self.lbl_tool_state)

        self.bar_live_pressure = Gtk.ProgressBar.new()
        self.bar_live_pressure.set_hexpand(True)
        self.bar_live_pressure.set_valign(Gtk.Align.CENTER)
        telemetry_box.append(self.bar_live_pressure)

        self.lbl_tilt_state = Gtk.Label.new("Presión: 0%  |  Tilt: 0°, 0°")
        self.lbl_tilt_state.add_css_class("caption")
        telemetry_box.append(self.lbl_tilt_state)

        self.ink_canvas = InkTestCanvas(self.curve_graph, self._update_telemetry, self.palette)
        frame = Gtk.Frame.new()
        frame.set_child(self.ink_canvas)
        right_card.append(frame)

        self.view_stack.add_titled_with_icon(
            scrolled, "pressure", "Presión y Lienzo", "applications-graphics-symbolic"
        )

    def _update_telemetry(self, tool_label: str, pressure: float, tx: float, ty: float):
        self.lbl_tool_state.set_text(f"Herramienta: {tool_label}")
        self.bar_live_pressure.set_fraction(max(0.0, min(1.0, pressure)))
        pct = int(round(pressure * 100))
        self.lbl_tilt_state.set_text(f"Presión: {pct}%  |  Tilt: {tx:.0f}°, {ty:.0f}°")

    def _on_pressure_params_changed(self, _widget):
        lvl = int(round(self.scale_level.get_value()))
        min_p = round(self.scale_minp.get_value(), 2)
        tip_d = round(self.scale_tip.get_value(), 2)
        self.settings["pressure_level"] = lvl
        self.settings["minimum_pressure"] = min_p
        self.settings["tip_distance"] = tip_d
        self.curve_graph.set_params(lvl, min_p)

    def _on_save_pressure_clicked(self, _btn):
        backends.save_settings(self.settings)
        ok, msg = backends.apply_xournalpp_settings(self.settings)
        self.refresh_hardware_status()
        self.show_toast(msg if ok else f"Aviso: {msg}")

    # ------------------------------------------------------------------
    # TAB 3: BOTONES Y ATAJOS
    # ------------------------------------------------------------------
    def _build_buttons_page(self):
        page = Adw.PreferencesPage.new()

        grp_top = Adw.PreferencesGroup.new()
        grp_top.set_title("Botón Superior Bluetooth (Atajos de Windows Ink)")
        grp_top.set_description(
            "El botón superior retráctil envía señales Bluetooth independientes para 1 clic, doble clic y mantener presionado."
        )

        self.preset_keys = list(backends.BUTTON_PRESETS.keys())
        preset_labels = [backends.BUTTON_PRESETS[k][0] for k in self.preset_keys]

        # Single Click (SUPER + F20)
        self.row_single, self.dd_single, self.entry_single = self._create_shortcut_rows(
            grp_top,
            "Un solo clic (Single-click)",
            "Señal de hardware: SUPER + F20",
            "single_click",
            preset_labels,
        )

        # Double Click (SUPER + F19)
        self.row_double, self.dd_double, self.entry_double = self._create_shortcut_rows(
            grp_top,
            "Doble clic (Double-click)",
            "Señal de hardware: SUPER + F19",
            "double_click",
            preset_labels,
        )

        # Long Press (SUPER + F18)
        self.row_long, self.dd_long, self.entry_long = self._create_shortcut_rows(
            grp_top,
            "Mantener presionado (Press y Hold)",
            "Señal de hardware: SUPER + F18",
            "long_press",
            preset_labels,
        )

        page.add(grp_top)

        # Group 2: Side Barrel Button & Rear Eraser
        grp_side = Adw.PreferencesGroup.new()
        grp_side.set_title("Botón Lateral (Barrel Button) y Borrador Físico")
        grp_side.set_description("Comportamiento al dibujar o tomar notas en aplicaciones compatibles como Xournal++.")

        # Barrel button dropdown
        self.barrel_keys = list(backends.BARREL_ACTIONS.keys())
        barrel_labels = [backends.BARREL_ACTIONS[k] for k in self.barrel_keys]
        row_barrel = Adw.ActionRow.new()
        row_barrel.set_title("Acción del Botón Lateral")
        row_barrel.set_subtitle("Al mantener presionado el botón del costado cerca de la pantalla")
        self.dd_barrel = Gtk.DropDown.new_from_strings(barrel_labels)
        self.dd_barrel.set_valign(Gtk.Align.CENTER)
        cur_barrel = self.settings.get("barrel_button_action", "selectRegion")
        if cur_barrel in self.barrel_keys:
            self.dd_barrel.set_selected(self.barrel_keys.index(cur_barrel))
        self.dd_barrel.connect("notify::selected", self._on_barrel_or_eraser_changed)
        row_barrel.add_suffix(self.dd_barrel)
        grp_side.add(row_barrel)

        # Eraser mode dropdown
        self.eraser_keys = list(backends.ERASER_MODES.keys())
        eraser_labels = [backends.ERASER_MODES[k] for k in self.eraser_keys]
        row_eraser = Adw.ActionRow.new()
        row_eraser.set_title("Comportamiento del Borrador Trasero")
        row_eraser.set_subtitle("Al voltear el lápiz y apoyar la goma sobre la pantalla")
        self.dd_eraser = Gtk.DropDown.new_from_strings(eraser_labels)
        self.dd_eraser.set_valign(Gtk.Align.CENTER)
        cur_eraser = self.settings.get("eraser_mode", "standard")
        if cur_eraser in self.eraser_keys:
            self.dd_eraser.set_selected(self.eraser_keys.index(cur_eraser))
        self.dd_eraser.connect("notify::selected", self._on_barrel_or_eraser_changed)
        row_eraser.add_suffix(self.dd_eraser)
        grp_side.add(row_eraser)

        page.add(grp_side)

        self.view_stack.add_titled_with_icon(
            page, "buttons", "Botones", "preferences-desktop-keyboard-shortcuts-symbolic"
        )

    def _create_shortcut_rows(self, group, title, subtitle, prefix, preset_labels):
        row = Adw.ActionRow.new()
        row.set_title(title)
        row.set_subtitle(subtitle)

        dd = Gtk.DropDown.new_from_strings(preset_labels)
        dd.set_valign(Gtk.Align.CENTER)
        cur_preset = self.settings.get(f"{prefix}_preset", "xournalpp")
        if cur_preset in self.preset_keys:
            dd.set_selected(self.preset_keys.index(cur_preset))

        btn_test = Gtk.Button.new_with_label("Probar")
        btn_test.set_valign(Gtk.Align.CENTER)
        btn_test.connect("clicked", lambda *_: self._test_shortcut(prefix))

        row.add_suffix(dd)
        row.add_suffix(btn_test)
        group.add(row)

        entry_row = Adw.EntryRow.new()
        entry_row.set_title(f"Comando personalizado ({title})")
        entry_row.set_text(self.settings.get(f"{prefix}_custom", ""))
        entry_row.set_visible(cur_preset == "custom")
        group.add(entry_row)

        def on_dd_changed(*_):
            idx = dd.get_selected()
            key = self.preset_keys[idx]
            self.settings[f"{prefix}_preset"] = key
            entry_row.set_visible(key == "custom")
            backends.save_settings(self.settings)
            ok, msg = backends.apply_hyprland_settings(self.settings)
            self.refresh_hardware_status()
            self.show_toast(msg if ok else f"Error: {msg}")

        def on_entry_changed(*_):
            self.settings[f"{prefix}_custom"] = entry_row.get_text().strip()
            backends.save_settings(self.settings)
            backends.apply_hyprland_settings(self.settings)

        dd.connect("notify::selected", on_dd_changed)
        entry_row.connect("changed", on_entry_changed)
        return row, dd, entry_row

    def _test_shortcut(self, prefix: str):
        cmd = backends.resolve_button_command(self.settings, prefix)
        if not cmd:
            self.show_toast("Este botón está configurado como «Sin acción»")
            return
        self.show_toast(f"Ejecutando: {cmd}")
        subprocess.Popen(["bash", "-lc", cmd])

    def _on_barrel_or_eraser_changed(self, *_args):
        b_idx = self.dd_barrel.get_selected()
        e_idx = self.dd_eraser.get_selected()
        self.settings["barrel_button_action"] = self.barrel_keys[b_idx]
        self.settings["eraser_mode"] = self.eraser_keys[e_idx]
        backends.save_settings(self.settings)
        ok, msg = backends.apply_xournalpp_settings(self.settings)
        self.show_toast(msg)

    # ------------------------------------------------------------------
    # TAB 4: TÁCTIL, PALMA Y CALIBRACIÓN
    # ------------------------------------------------------------------
    def _build_touch_page(self):
        page = Adw.PreferencesPage.new()

        grp_ergo = Adw.PreferencesGroup.new()
        grp_ergo.set_title("Ergonomía y Mano Dominante (Windows Ink)")
        grp_ergo.set_description("Configuración de orientación del digitalizador y estilo de puntero.")

        # Handedness
        row_hand = Adw.ActionRow.new()
        row_hand.set_title("Elige la mano con la que escribes")
        row_hand.set_subtitle("Optimiza la orientación del lápiz en Hyprland")
        self.dd_hand = Gtk.DropDown.new_from_strings(["Diestro (Mano derecha)", "Zurdo (Mano izquierda)"])
        self.dd_hand.set_valign(Gtk.Align.CENTER)
        self.dd_hand.set_selected(1 if self.settings.get("left_handed", False) else 0)
        self.dd_hand.connect("notify::selected", self._on_ergo_changed)
        row_hand.add_suffix(self.dd_hand)
        grp_ergo.add(row_hand)

        # Cursor style
        self.cursor_keys = list(backends.CURSOR_TYPES.keys())
        cursor_labels = [backends.CURSOR_TYPES[k] for k in self.cursor_keys]
        row_cursor = Adw.ActionRow.new()
        row_cursor.set_title("Mostrar cursor al acercar el lápiz")
        row_cursor.set_subtitle("Define el indicador visual cuando la punta flota sobre la pantalla")
        self.dd_cursor = Gtk.DropDown.new_from_strings(cursor_labels)
        self.dd_cursor.set_valign(Gtk.Align.CENTER)
        cur_c = self.settings.get("stylus_cursor_type", "dot")
        if cur_c in self.cursor_keys:
            self.dd_cursor.set_selected(self.cursor_keys.index(cur_c))
        self.dd_cursor.connect("notify::selected", self._on_ergo_changed)
        row_cursor.add_suffix(self.dd_cursor)
        grp_ergo.add(row_cursor)

        # Relative input mode (Use pen as mouse)
        self.sw_relative = Adw.SwitchRow.new()
        self.sw_relative.set_title("Permitirme usar el lápiz como ratón (Modo Relativo)")
        self.sw_relative.set_subtitle("Desactívalo para dibujo natural 1:1 sobre la pantalla")
        self.sw_relative.set_active(self.settings.get("relative_input", False))
        self.sw_relative.connect("notify::active", self._on_ergo_changed)
        grp_ergo.add(self.sw_relative)

        page.add(grp_ergo)

        # Group 2: Palm Rejection & Touchscreen (IPTSD)
        grp_palm = Adw.PreferencesGroup.new()
        grp_palm.set_title("Rechazo de Palma y Control Táctil (IPTSD)")
        grp_palm.set_description(
            "Ajustes a nivel de hardware para apoyar la mano cómodamente sobre la pantalla sin generar toques accidentales."
        )

        self.sw_disable_on_stylus = Adw.SwitchRow.new()
        self.sw_disable_on_stylus.set_title("Ignorar entrada táctil cuando uso el lápiz (DisableOnStylus)")
        self.sw_disable_on_stylus.set_subtitle(
            "Desactiva automáticamente los dedos en cuanto la punta del lápiz se acerca a la pantalla"
        )
        self.sw_disable_on_stylus.set_active(self.settings.get("disable_on_stylus", True))
        grp_palm.add(self.sw_disable_on_stylus)

        self.sw_disable_on_palm = Adw.SwitchRow.new()
        self.sw_disable_on_palm.set_title("Rechazo de palma automático (DisableOnPalm)")
        self.sw_disable_on_palm.set_subtitle("Ignora contactos grandes producidos al apoyar la muñeca o la mano")
        self.sw_disable_on_palm.set_active(self.settings.get("disable_on_palm", True))
        grp_palm.add(self.sw_disable_on_palm)

        self.sw_disable_touch = Adw.SwitchRow.new()
        self.sw_disable_touch.set_title("Modo Exclusivo para Lápiz (Desactivar táctil de dedos)")
        self.sw_disable_touch.set_subtitle("La pantalla solo responderá al Surface Pen e ignorará siempre los dedos")
        self.sw_disable_touch.set_active(self.settings.get("disable_touchscreen", False))
        grp_palm.add(self.sw_disable_touch)

        row_apply_ipts = Adw.ActionRow.new()
        row_apply_ipts.set_title("Guardar en el Digitalizador del Sistema (/etc/iptsd.d/)")
        row_apply_ipts.set_subtitle("Aplica rechazo de palma y compensación de inclinación en el servicio IPTSD")
        btn_apply_ipts = Gtk.Button.new_with_label("Aplicar al Digitalizador")
        btn_apply_ipts.add_css_class("suggested-action")
        btn_apply_ipts.set_valign(Gtk.Align.CENTER)
        btn_apply_ipts.connect("clicked", self._on_apply_iptsd_clicked)
        row_apply_ipts.add_suffix(btn_apply_ipts)
        grp_palm.add(row_apply_ipts)

        row_calibrate = Adw.ActionRow.new()
        row_calibrate.set_title("Calibración Física de Pantalla (iptsd-calibrate)")
        row_calibrate.set_subtitle("Abre la herramienta oficial para calibrar desviaciones de contacto")
        btn_cal = Gtk.Button.new_with_label("Calibrar Pantalla...")
        btn_cal.set_valign(Gtk.Align.CENTER)
        btn_cal.connect(
            "clicked",
            lambda *_: subprocess.Popen(
                ["omarchy-launch-floating-terminal-with-presentation", "sudo iptsd-calibrate"]
            ),
        )
        row_calibrate.add_suffix(btn_cal)
        grp_palm.add(row_calibrate)

        page.add(grp_palm)

        self.view_stack.add_titled_with_icon(
            page, "touch", "Táctil y Palma", "touchpad-enabled-symbolic"
        )

    def _on_ergo_changed(self, *_args):
        self.settings["left_handed"] = self.dd_hand.get_selected() == 1
        self.settings["stylus_cursor_type"] = self.cursor_keys[self.dd_cursor.get_selected()]
        self.settings["relative_input"] = self.sw_relative.get_active()
        backends.save_settings(self.settings)
        backends.apply_hyprland_settings(self.settings)
        backends.apply_xournalpp_settings(self.settings)
        self.refresh_hardware_status()
        self.show_toast("Preferencias de ergonomía y cursor aplicadas")

    def _on_apply_iptsd_clicked(self, _btn):
        self.settings["disable_on_stylus"] = self.sw_disable_on_stylus.get_active()
        self.settings["disable_on_palm"] = self.sw_disable_on_palm.get_active()
        self.settings["disable_touchscreen"] = self.sw_disable_touch.get_active()
        backends.save_settings(self.settings)
        backends.apply_xournalpp_settings(self.settings)

        self.show_toast("Solicitando autorización para actualizar IPTSD...")

        def worker():
            ok, msg = backends.apply_iptsd_settings(self.settings)
            GLib.idle_add(lambda: (self.refresh_hardware_status(), self.show_toast(msg)))

        threading.Thread(target=worker, daemon=True).start()


class SurfacePenStudioApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.omarchy.SurfacePenStudio")
        self.connect("activate", self._on_activate)

    def _on_activate(self, app):
        win = self.props.active_window
        if not win:
            win = SurfacePenWindow(app)
        win.present()


def main():
    app = SurfacePenStudioApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
