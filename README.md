# Keyboard configs

Personal keyboard configurations. Each keyboard lives under a firmware-specific directory (e.g. `zmk/<keyboard>/`) with its own keymap, board config, and build matrix.

## Structure

```
zmk/
├── corne/       # Corne 42-key split
│   ├── build.yaml     # Build matrix (board + shield pairs)
│   ├── west.yml       # West manifest (ZMK + modules)
│   ├── corne.keymap   # Keymap definition
│   ├── corne.conf     # Kconfig options
│   └── corne.dtsi     # Devicetree overlay
└── cradio/      # CRadio / Sweep-style 34-key split
    ├── build.yaml
    ├── west.yml
    ├── cradio.keymap
    ├── cradio.conf
    └── README.md
```

## CI

Pushes run two local workflows with keyboard-scoped selection:

- **Build firmware** — The custom workflow in `.github/workflows/build.yml` builds only affected keyboards. Shared workflow/drawer-config changes and manual `workflow_dispatch` select all keyboards.
- **Draw keymaps** — The local workflow in `.github/workflows/draw-keymap.yml` redraws only affected keyboards, with the same shared-file and manual-dispatch all-keyboards behavior.
