import math
from util import *

# NOTE: r_water, r_ocean, other fields are boolean valued so it
# could be more efficient to pack them as bit fields in Uint8Array
# a region is water if the noise value is low 
def assign_r_water(r_water, mesh, noise, params):
    r_water.length = mesh.numRegions
    for r in range(mesh.numRegions):
        if (mesh.r_ghost(r) or mesh.r_boundary(r)):
            r_water[r] = True
        else:
            nx = (mesh.r_x(r) - 500) / 500
            ny = (mesh.r_y(r) - 500) / 500
            distance = math.max(math.abs(nx), math.abs(ny))
            n = util.fbm_noise(noise, params.amplitudes, nx, ny)
            n = util.mix(n, 0.5, params.round)
            r_water[r] = n - (1.0 - params.inflate) * distance*distance < 0

    return r_water

# a region is ocean if it is a water region connected to the ghost region,
#  which is outside the boundary of the map; this could be any seed set but
#  for islands, the ghost region is a good seed 
def assign_r_ocean(r_ocean, mesh, r_water):
    r_ocean.length = mesh.numRegions
    r_ocean.fill(False)
    stack = [mesh.ghost_r()]
    r_out = []
    while (stack.length > 0):
        r1 = stack.pop()
        mesh.r_circulate_r(r_out, r1)
        for r2 in r_out:
            if  r_water[r2] and not r_ocean[r2]:
                r_ocean[r2] = True
                stack.append(r2)

    return r_ocean