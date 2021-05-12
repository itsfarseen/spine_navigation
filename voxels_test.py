import matplotlib.pyplot as plt
import numpy as np
import nibabel as nib
import math

img = nib.load("ct/ct.nii.gz")

data = img.get_fdata()
assert len(data.shape) == 3, "Not 3D data"


def next_power_of_two(x):
    return 2 ** (math.ceil(math.log(x, 2)))


def show_slices(slices):
    """Function to display row of image slices"""
    fig, axes = plt.subplots(1, len(slices))
    for i, slice in enumerate(slices):
        axes[i].imshow(slice.T, cmap="gray", origin="lower")


pads = []
for s in data.shape:
    next_two_power = next_power_of_two(s)
    pad = next_two_power - s
    pads.append((0, pad))

padded = np.pad(data, pads)
print("in", data.shape)
print("in padded", padded.shape)

tex3d = padded

slice_0 = padded[26, :, :]
slice_1 = padded[:, 30, :]
slice_2 = padded[:, :, 16]
show_slices([slice_0, slice_1, slice_2])
plt.suptitle("Center slices for EPI image")

# and plot everything
# ax = plt.figure().add_subplot(projection="3d")
# ax.voxels(tex3d, edgecolor="k")

plt.show()
