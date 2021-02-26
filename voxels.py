import numpy as np

# define array size and sphere radius
def sphere(size_x, size_y, size_z, sphere_radius):
    size = [size_x, size_y, size_z]
    radius = sphere_radius

    # compute center index of array
    center = [int(size[0] / 2), int(size[1] / 2), int(size[2] / 2)]

    # create index grid for array
    ind_0, ind_1, ind_2 = np.indices((size[0], size[1], size[2]))

    # calculate "distance" of indices to center index
    distance = (
        (ind_0 - center[0]) ** 2
        + (ind_1 - center[1]) ** 2
        + (ind_2 - center[2]) ** 2
    ) ** 0.5

    # create output
    output = np.ones(shape=(size[0], size[1], size[2])) * (distance <= radius)
    return output
