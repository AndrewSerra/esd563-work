from enum import Enum

b = 60
f = 6
ps = .006

width = 752
height = 480

center_x = width / 2
center_y = height / 2


def get_depth(left_centroid_x, right_centroid_x):
    return abs((left_centroid_x - center_x) - (right_centroid_x - center_x)) * ps

def get_position(x_centroid, y_centroid, depth):
    z = (b * f) / depth
    x = z * (x_centroid - center_x) * ps / f
    y = z * (y_centroid - center_y) * ps / f

    return (x, y, z)
