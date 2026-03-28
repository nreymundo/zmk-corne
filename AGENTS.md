# AGENTS.md

## Contribution Rules

- **No attribution lines unless explicitly requested.** Never add any attribution, co-authorship, or tool-credit trailer to commit messages unless explicitly asked.
- **Commit messages describe changes only.** State what changed and why. No metadata about how the change was made, which tool was used, or any other non-essential information.
- **No unauthorized changes.** Only modify what was explicitly asked for.
- **Keep docs in sync.** After any structural change (moving files, changing paths, updating workflows, adding/removing keyboards), re-evaluate all READMEs, AGENTS.md, and any other documentation to ensure they still reflect the current state of the repo.

## Repository Layout

```
zmk-corne/
├── .github/workflows/
│   ├── build.yml                # Custom build workflow (not the ZMK reusable one)
│   └── draw-keymap.yml          # Calls keymap-drawer on keymap changes
├── assets/keymaps/
│   ├── keymap_drawer.config.yaml  # Shared drawing config (all keyboards)
│   ├── corne.yaml                 # Generated — do not edit
│   └── corne.svg                  # Generated — do not edit
└── zmk/
    └── <keyboard>/               # One directory per keyboard
        ├── build.yaml            # Build matrix (board + shield pairs)
        ├── west.yml              # West manifest (ZMK + modules)
        ├── <keyboard>.keymap     # Keymap definition
        ├── <keyboard>.conf       # Kconfig options
        ├── <keyboard>.dtsi       # Devicetree overlay — optional
        ├── boards/shields/       # Optional local helper shields/overlays
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

Add a new build block in `.github/workflows/build.yml`. The workflow uses a custom build pipeline (not the ZMK reusable workflow) because nested `config_path` values like `zmk/<keyboard>` break the reusable workflow's west workspace resolution. Follow the existing `corne` pattern: add a matrix fetch step, a build step with `container: zmkfirmware/zmk-build-arm:stable`, and the west init/update/build sequence.

### 6. Add keymap drawing (optional)

If the keyboard has a keymap to visualize, update `.github/workflows/draw-keymap.yml`:
- The `keymap_patterns: "zmk/**/*.keymap"` glob already picks up new keyboards automatically.
- Update `json_path` if keymap-drawer needs per-keyboard parse context.

## CI Behavior

- **Build**: Every push to `master` (or manual trigger) builds firmware for all keyboards. Each produces downloadable artifacts (e.g. `corne_left.uf2`, `corne_right.uf2`).
- **Draw keymaps**: Every push that touches a `.keymap` or `.dtsi` file under `zmk/` regenerates SVG visualizations in `assets/keymaps/` and amends them to the commit.

## CI Architecture Notes

- **Custom build workflow, not the ZMK reusable one.** The ZMK reusable workflow (`zmkfirmware/zmk/.github/workflows/build-user-config.yml@main`) does not support nested `config_path` values like `zmk/corne`. It breaks at `west update` because `west init -l zmk/corne` creates the workspace at `zmk/` (one level up from the manifest), but the workflow runs `west update` from the repo root which is outside that workspace. The custom workflow in this repo handles this by running `west init` from the repo root and `west update` from the `zmk/` directory.
- **No `zephyr/module.yml`.** This file was removed because it triggered the reusable workflow's `/tmp/zmk-config/` copy path, which uses `mkdir` (not `mkdir -p`) and fails on nested directory structures. Local helper shields under `zmk/<keyboard>/boards/shields/` work via the keyboard config's west `self.path`, so `zephyr/module.yml` is still not needed.
- **Container path resolution.** The build runs inside a Docker container (`zmkfirmware/zmk-build-arm:stable`). Inside container `run` steps, use `$GITHUB_WORKSPACE` (env var) instead of `${{ github.workspace }}` (expression). The expression resolves to the host path which differs from the container's mount point (`/__w/...`).
- **Adding a keyboard.** Each keyboard needs its own `west.yml` with `self.path: zmk/<keyboard>` matching its actual directory path, and a corresponding build block in `.github/workflows/build.yml`.
