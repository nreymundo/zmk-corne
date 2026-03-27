# AGENTS.md

## Contribution Rules

- **No attribution lines unless explicitly requested.** Never add any attribution, co-authorship, or tool-credit trailer to commit messages unless explicitly asked.
- **Commit messages describe changes only.** State what changed and why. No metadata about how the change was made, which tool was used, or any other non-essential information.
- **No unauthorized changes.** Only modify what was explicitly asked for.

## Repository Layout

```
zmk-corne/
├── .github/workflows/
│   ├── build.yml                # Calls ZMK reusable workflow per keyboard
│   └── draw-keymap.yml          # Calls keymap-drawer on keymap changes
├── assets/keymaps/
│   ├── keymap_drawer.config.yaml  # Shared drawing config (all keyboards)
│   ├── corne.yaml                 # Generated — do not edit
│   └── corne.svg                  # Generated — do not edit
├── boards/shields/               # Custom shield definitions (if needed)
├── zephyr/module.yml             # Zephyr module config (board_root: .)
└── zmk/
    └── <keyboard>/               # One directory per keyboard
        ├── build.yaml            # Build matrix (board + shield pairs)
        ├── west.yml              # West manifest (ZMK + modules)
        ├── <keyboard>.keymap     # Keymap definition
        ├── <keyboard>.conf       # Kconfig options
        ├── <keyboard>.dtsi       # Devicetree overlay (if needed)
        └── README.md             # Keyboard-specific info + layout image
```

## Adding a New ZMK Keyboard

### 1. Create the directory

```
zmk/<keyboard>/
```

### 2. Add `zmk/<keyboard>/west.yml`

```yaml
manifest:
  remotes:
    - name: zmkfirmware
      url-base: https://github.com/zmkfirmware
  projects:
    - name: zmk
      remote: zmkfirmware
      revision: main
      import: app/west.yml
    # Add extra modules here if needed (e.g. nice-view-gem, zmk-helpers)
  self:
    path: zmk/<keyboard>    # MUST match the actual directory path
```

### 3. Add `zmk/<keyboard>/build.yaml`

```yaml
---
include:
  - board: <board_name>
    shield: <shield>_left
  - board: <board_name>
    shield: <shield>_right
```

### 4. Add config files

| File | Purpose |
|------|---------|
| `<keyboard>.keymap` | Layer definitions, bindings, combos, behaviors |
| `<keyboard>.conf` | Kconfig options (keyboard name, sleep, mouse, display) |
| `<keyboard>.dtsi` | Devicetree overlay (custom matrix, peripherals) — optional |
| `README.md` | Keyboard description + layout image |

### 5. Wire up the build workflow

Add a new job in `.github/workflows/build.yml`:

```yaml
  build-<keyboard>:
    uses: zmkfirmware/zmk/.github/workflows/build-user-config.yml@main
    with:
      build_matrix_path: zmk/<keyboard>/build.yaml
      config_path: zmk/<keyboard>
```

### 6. Add keymap drawing (optional)

If the keyboard has a keymap to visualize, update `.github/workflows/draw-keymap.yml`:
- The `keymap_patterns: "zmk/**/*.keymap"` glob already picks up new keyboards automatically.
- Update `json_path` if keymap-drawer needs per-keyboard parse context.

## CI Behavior

- **Build**: Every push to `master` (or manual trigger) builds firmware for all keyboards. Each produces downloadable artifacts (e.g. `corne_left.uf2`, `corne_right.uf2`).
- **Draw keymaps**: Every push that touches a `.keymap` or `.dtsi` file under `zmk/` regenerates SVG visualizations in `assets/keymaps/` and amends them to the commit.
