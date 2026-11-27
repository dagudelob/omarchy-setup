-- Keep only your personal keybinding overrides here. Add new bindings with
-- o.bind or replace defaults with o.rebind.

-- See current bindings and descriptions:
--   omarchy menu keybindings --print

-- To disable every Omarchy default binding, set this in
-- ~/.config/hypr/hyprland.lua before require("default.hypr.omarchy"), then add
-- only the bindings you want below:
--   omarchy_default_bindings = false

-- To disable all preinstalled app/webapp bindings, set:
--   omarchy_preinstalled_bindings = false

-- Add a new binding.
-- o.bind("SUPER + SHIFT + R", "SSH", "alacritty -e ssh your-server")

-- Cambiar distribución de teclado (alternativa rápida con tecla Super)
o.bind("SUPER + ALT + K", "Switch keyboard layout", "hyprctl switchxkblayout all next")

-- Cerrar ventana con Alt + F4
o.bind("ALT + F4", "Close window", hl.dsp.window.close())

-- Abrir Files (administrador de archivos) con Super + E
o.bind("SUPER + E", "Files", { launch = "nautilus" })

-- Change an existing binding. o.rebind takes the same arguments as o.bind.
-- This example replaces the default file manager with Flea.
-- o.rebind("SUPER + SHIFT + F", "File manager", { launch = "flea" })

-- Disable a default binding without replacing it.
-- hl.unbind("SUPER + SHIFT + B")

-- Logitech MX Keys examples:
-- o.bind("SUPER + SHIFT + S", nil, "omarchy-capture-screenshot")
-- o.bind("SUPER + H", nil, "voxtype record toggle")
-- o.bind("SUPER + PERIOD", nil, { panel = "omarchy.emojis" })

-- Dictation keys: override default Right Alt (Alt_R) with AltGr + Space (MOD5 + SPACE)
-- since us(intl-livequote) maps Right Alt to ISO_Level3_Shift (AltGr).
if o.dictation_installed and o.dictation_installed() then
  hl.unbind("ALT + Alt_R")
  o.bind_hold("MOD5 + SPACE", "Start dictation (push-to-talk)", "omarchy-dictation start", "Stop dictation (push-to-talk)", "omarchy-dictation stop")

  -- Legacy dictation keys from before Alt + Space and Right Alt became the defaults.
  o.bind("SUPER + CTRL + X", "Toggle dictation", "omarchy-dictation toggle")
  o.bind_hold("F9", "Start dictation (push-to-talk)", "omarchy-dictation start", "Stop dictation (push-to-talk)", "omarchy-dictation stop")
end
