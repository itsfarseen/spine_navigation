import matplotlib.pyplot as plt
import numpy as np


tex3d = np.zeros((10, 10, 10), dtype=np.uint8)

for x in range(10):
    for y in range(10):
        for z in range(10):
            if (
                abs(np.sqrt((2 * x - 4.5) ** 2 + (y - 4.5) ** 2 + (z - 4.5) ** 2) - 5)
                <= 1
            ):
                tex3d[x, y, z] = 255

# and plot everything
ax = plt.figure().add_subplot(projection="3d")
ax.voxels(tex3d, edgecolor="k")

plt.show()
