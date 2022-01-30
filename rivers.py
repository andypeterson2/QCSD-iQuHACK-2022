MIN_SPRING_ELEV = 0.3
MAX_SPRING_ELEV = 0.9

# Find candidates for river sources
# Unlike assign_* functions, this does not write into an existing array

def find_spring_t(mesh, r_water, t_elevation, t_downslope_s):
    t_water = lambda t: r_water[mesh.s_begin_r(3*t)] or r_water[mesh.s_begin_r(3*t+1)] or r_water[mesh.s_begin_r(3*t+2)]

    spring_t = set()
    # Add everything above some elevation, but not lakes
    for t in range(mesh.numSolidTriangles):
        if  (t_elevation[t] >= MIN_SPRING_ELEV and
            t_elevation[t] <= MAX_SPRING_ELEV and
            (not t_water(t))):
            spring_t.add(t)
    return spring_t

def assign_s_flow(s_flow, mesh, t_downslope_s, river_t):
    # Each river in river_t contributes 1 flow down to the coastline
    s_flow.length = mesh.numSides
    s_flow.fill(0)
    for t in river_t:
        for p in iter(int, 1):
            s = t_downslope_s[t]
            if (s == -1): break
            s_flow[s] = s_flow[s] + 1
            next_t = mesh.s_outer_t(s)
            if (next_t == t): break
            t = next_t
    return s_flow