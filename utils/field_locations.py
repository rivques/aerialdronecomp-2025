import numpy as np

# just a bunch of constants of where stuff is
# assumes starting on center of Mat 1 facing through red arch
# units are meters, coordinates are centerpoints of objects

def in_to_m(inches):
    return inches * 0.0254

keyhole_outer_dia = in_to_m(30)
keyhole_inner_dia = in_to_m(24)
prog_mat_size = np.array([in_to_m(96), in_to_m(42)])
color_mat_size = in_to_m(24)
arch_inner_height = in_to_m(63)
landing_pad_dia = in_to_m(15)

mat_1 = np.array([0, 0, 0])
mat_2 = np.array([color_mat_size/2+prog_mat_size[0]+prog_mat_size[1]/2, in_to_m(3), 0])

reset_offset = -mat_2

red_arch = np.array([color_mat_size/2+in_to_m(24), 0, arch_inner_height/2])
blue_arch = np.array([color_mat_size/2+in_to_m(72), 0, arch_inner_height/2])

# segment 2

yellow_keyhole = np.array([0, in_to_m(-36), in_to_m(54)+keyhole_outer_dia/2])
green_keyhole = np.array([in_to_m(-24), in_to_m(-86), in_to_m(42)+keyhole_outer_dia/2])

landing_pad = reset_offset + np.array([in_to_m(70), in_to_m(-96), 0])
large_landing_cube = reset_offset + np.array([in_to_m(48), in_to_m(-96), in_to_m(22)])
small_landing_cube = reset_offset + np.array([in_to_m(30), in_to_m(-96), in_to_m(15)])