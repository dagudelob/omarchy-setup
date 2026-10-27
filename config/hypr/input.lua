-- Keep only your personal input overrides here. Uncommented settings below
-- replace Omarchy's defaults.

-- Keyboard layout and options.
-- See https://wiki.hypr.land/Configuring/Basics/Variables/#input
hl.config({
  input = {
    -- Distribución US Internacional personalizada (comillas dobles vivas, tildes y eñes muertas)
    kb_layout = "us",
    kb_variant = "intl-livequote",
    -- kb_options sin compose:caps para mantener Caps Lock estándar
    kb_options = "",

    touchpad = {
      -- Use natural (inverse) scrolling.
      natural_scroll = true,

      -- Allow clicking in the lower-right corner for right-click (software buttons).
      clickfinger_behavior = false,

      -- Tap to click
      tap_to_click = true,

      -- Control the speed of your scrolling.
      scroll_factor = 0.4,

      -- Enable the touchpad while typing.
      disable_while_typing = true,

      -- 3-finger tap for middle click (drag_3fg = 0 to allow native middle click)
      drag_3fg = 0,
      tap_button_map = "lrm",
    },
  },
})

-- Enable touchpad gestures for changing workspaces.
-- See https://wiki.hypr.land/Configuring/Advanced-and-Cool/Gestures/
hl.gesture({ fingers = 3, direction = "horizontal", action = "workspace" })


-- Enable touchpad gestures for moving focus (helpful on scrolling layout).
-- hl.gesture({ fingers = 3, direction = "left", action = function() hl.dispatch(hl.dsp.focus({ direction = "l" })) end })
-- hl.gesture({ fingers = 3, direction = "right", action = function() hl.dispatch(hl.dsp.focus({ direction = "r" })) end })


