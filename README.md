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
│   ├── corne.dtsi     # Devicetree overlay
│   └── boards/shields/ # Optional local shield overlays/helpers
```

## CI

Every push to `master` (or manual trigger) runs two workflows:

- **Build firmware** — Uses the repo's custom workflow in `.github/workflows/build.yml`. Each entry in a keyboard's `build.yaml` produces a firmware artifact (e.g. `corne_left`, `corne_right`) ready to flash.
- **Draw keymaps** — When a `.keymap` or `.dtsi` changes, [keymap-drawer](https://github.com/caksoylar/keymap-drawer) parses the keymaps and commits updated SVG visualizations to `assets/keymaps/`.
