import matplotlib.pyplot as plt
import numpy as np

import paths

xyz = np.load(paths.data / "helix.npz")["xyz"]
fig, ax = plt.subplots(figsize=(3.5, 3.5))
ax.plot(xyz[:, 0], xyz[:, 1])
ax.set(xlabel="$x$", ylabel="$y$", aspect="equal")
fig.savefig(paths.figures / "helix.pdf", bbox_inches="tight")
