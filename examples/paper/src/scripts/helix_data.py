"""The helix the paper and its webapp share: src/data/helix.npz."""

import numpy as np

import paths

t = np.linspace(0, 6 * np.pi, 400)
xyz = np.stack([np.cos(t), np.sin(t), t / (6 * np.pi) - 0.5], axis=1)
np.savez(paths.data / "helix.npz", xyz=xyz, turns=3)
