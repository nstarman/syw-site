import matplotlib.pyplot as plt
import numpy as np

import paths

xyz = np.load(paths.data / "helix.npz")["xyz"]
for axis, name in ((0, "x"), (1, "y")):
    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    ax.plot(xyz[:, 1 - axis], xyz[:, 2])
    ax.set(xlabel=f"${'yx'[axis]}$", ylabel="$z$")
    fig.savefig(paths.figures / f"side_{name}.pdf", bbox_inches="tight")
