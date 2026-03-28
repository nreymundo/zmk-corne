#!/usr/bin/env python3
"""Select keyboards impacted by changed files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SHARED_TRIGGER_FILES = {
    ".github/workflows/build.yml",
    ".github/workflows/draw-keymap.yml",
    "assets/keymaps/keymap_drawer.config.yaml",
    ".github/scripts/select_keyboards.py",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--changed-file", action="append", default=[])
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--all-keyboards", action="store_true")
    parser.add_argument("--github-output", default="")
    return parser.parse_args()


def normalize(path: str) -> str:
    return path.strip().lstrip("./")


def discover_keyboards(repo_root: Path) -> list[str]:
    zmk_root = repo_root / "zmk"
    if not zmk_root.exists():
        return []
    return sorted(build_file.parent.name for build_file in zmk_root.glob("*/build.yaml") if build_file.is_file())


def parse_build_matrix(build_yaml_path: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    in_include = False

    for raw_line in build_yaml_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        stripped = line.strip()
        if not stripped or stripped == "---":
            continue

        if not in_include:
            if stripped == "include:":
                in_include = True
            continue

        if stripped.startswith("-"):
            if current is not None:
                entries.append(current)
            current = {}
            stripped = stripped[1:].strip()
            if stripped and ":" in stripped:
                key, value = stripped.split(":", 1)
                current[key.strip()] = value.strip()
            continue

        if current is not None and ":" in stripped:
            key, value = stripped.split(":", 1)
            current[key.strip()] = value.strip()

    if current is not None:
        entries.append(current)

    return entries


def select_keyboards(changed_paths: list[str], keyboards: list[str], all_keyboards: bool) -> tuple[list[str], str]:
    if all_keyboards:
        return keyboards, "manual_dispatch"

    normalized_paths = [normalize(path) for path in changed_paths if normalize(path)]
    if not normalized_paths:
        return [], "no_changed_files"

    if any(path in SHARED_TRIGGER_FILES for path in normalized_paths):
        return keyboards, "shared_change"

    known_keyboards = set(keyboards)
    selected = {
        path.split("/", 2)[1]
        for path in normalized_paths
        if path.startswith("zmk/") and len(path.split("/", 2)) >= 2 and path.split("/", 2)[1] in known_keyboards
    }
    if selected:
        return sorted(selected), "keyboard_scoped_change"

    return [], "no_matching_keyboard"


def build_matrix_for(repo_root: Path, keyboards: list[str]) -> dict[str, list[dict[str, str]]]:
    include_entries: list[dict[str, str]] = []
    for keyboard in keyboards:
        build_yaml = repo_root / "zmk" / keyboard / "build.yaml"
        if not build_yaml.exists():
            continue
        for entry in parse_build_matrix(build_yaml):
            include_entries.append({"keyboard": keyboard, **entry})
    return {"include": include_entries}


def write_outputs(output_path: Path, keyboards: list[str], matrix: dict[str, list[dict[str, str]]], should_run: bool, reason: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("a", encoding="utf-8") as handle:
        handle.write(f"selected_keyboards_json={json.dumps(keyboards, separators=(',', ':'))}\n")
        handle.write(f"selected_keyboards={','.join(keyboards)}\n")
        handle.write(f"primary_keyboard={keyboards[0] if keyboards else ''}\n")
        handle.write(f"build_matrix={json.dumps(matrix, separators=(',', ':'))}\n")
        handle.write(f"should_run={'true' if should_run else 'false'}\n")
        handle.write(f"reason={reason}\n")


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    keyboards = discover_keyboards(repo_root)
    changed_paths = [*args.changed_file, *args.paths]
    selected_keyboards, reason = select_keyboards(changed_paths, keyboards, args.all_keyboards)
    matrix = build_matrix_for(repo_root, selected_keyboards)
    should_run = bool(selected_keyboards and matrix["include"])

    result = {
        "reason": reason,
        "changed_files": [normalize(path) for path in changed_paths if normalize(path)],
        "all_keyboards": keyboards,
        "selected_keyboards": selected_keyboards,
        "build_matrix": matrix,
        "should_run": should_run,
    }
    print(json.dumps(result, indent=2, sort_keys=True))

    if args.github_output:
        write_outputs(Path(args.github_output), selected_keyboards, matrix, should_run, reason)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
