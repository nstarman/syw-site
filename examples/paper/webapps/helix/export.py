"""Export the helix webapp's dataset from the paper's src/data/helix.npz.

    python webapps/helix/export.py --out build/data
"""

import argparse
from pathlib import Path

import numpy as np

import figpress_apps

DATASET = "points"  # the name the app loads (widget.js)


def main(out: Path) -> Path:
    xyz = np.load(Path(__file__).parents[2] / "src/data/helix.npz")["xyz"]
    return figpress_apps.export(
        out, DATASET,
        {"xyz": xyz},                          # float64 stays float64 unless you pass narrow=[...]
        meta={"title": "The helix", "view": [0.0, 0.0, 1.0]},
        units={"xyz": "kpc"}, descriptions={"xyz": "the helix of Figure 1"},
        licence="MIT", overwrite=True,
    )


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("build/data"))
    print(main(ap.parse_args().out))
