#!/usr/bin/env python3
"""Convert the shared 66-position parse output to the 42-key XS right-trackball layout."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

# Positions that physically exist on XS with a right-side trackball.
# The values are indices in config/keymap.keymap before filtering.
XS_POSITIONS = [
    *range(13, 23),
    *range(25, 30),
    *range(32, 37),
    *range(39, 51),
    *range(53, 61),
    63,
    64,
]
POSITION_MAP = {old: new for new, old in enumerate(XS_POSITIONS)}

# Map S-layout combo indices to their positions in the shared 66-position keymap.
S_TO_SHARED = [
    *range(13, 23),
    *range(25, 30),
    *range(32, 37),
    *range(39, 51),
    *range(53, 65),
]


def flatten(values):
    for value in values:
        if isinstance(value, list):
            yield from flatten(value)
        else:
            yield value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    keymap = yaml.safe_load(args.input.read_text(encoding="utf-8"))

    for name, keys in keymap["layers"].items():
        flat_keys = list(flatten(keys))
        if len(flat_keys) != 66:
            raise ValueError(
                f"Layer {name!r} has {len(flat_keys)} positions; expected 66"
            )
        keymap["layers"][name] = [flat_keys[index] for index in XS_POSITIONS]

    filtered_combos = []
    for combo in keymap.get("combos", []):
        positions = combo.get("key_positions", combo.get("p"))
        if positions is None:
            filtered_combos.append(combo)
            continue
        # Combos using only S-layout indices are defined in the active physical
        # layout's 0-based numbering, while layers are parsed in shared order.
        if positions and all(0 <= position < len(S_TO_SHARED) for position in positions):
            positions = [S_TO_SHARED[position] for position in positions]
        if not all(position in POSITION_MAP for position in positions):
            continue
        mapped = [POSITION_MAP[position] for position in positions]
        if "key_positions" in combo:
            combo["key_positions"] = mapped
        else:
            combo["p"] = mapped
        filtered_combos.append(combo)
    keymap["combos"] = filtered_combos

    keymap["layout"] = {
        "qmk_info_json": "keymap-drawer/torabo-tsuki-lp-xs.json",
        "layout_name": "LAYOUT_xs_trackball_right",
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        yaml.safe_dump(keymap, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
