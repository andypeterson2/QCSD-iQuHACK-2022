#
# From http://www.redblobgames.com/maps/mapgen2/
# Copyright 2017 Red Blob Games <redblobgames@gmail.com>
# License: Apache v2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>
#

import math
# 'use strict';

#
# Coast corners are connected to coast sides, which have
# ocean on one side and land on the other
#


def find_coasts_t(mesh, r_ocean):
	coasts_t = []
	for s in range(0,mesh.numSides):
		r0 = mesh.s_begin_r(s)
		r1 = mesh.s_end_r(s)
		t = mesh.s_inner_t(s)
		if r_ocean[r0] and not r_ocean[r1]:
			# It might seem that we also need to check !r_ocean[r0] && r_ocean[r1]
			# and it might seem that we have to add both t and its opposite but
			# each t vertex shows up in *four* directed sides, so we only have to test
			# one fourth of those conditions to get the vertex in the list once.
			coasts_t.append(t)
	return coasts_t


#
# Elevation is based on breadth first search from the seed points,
# which are the coastal graph nodes. Since breadth first search also
# calculates the 'parent' pointers, return those for use as the downslope
# graph. To handle lakes, which should have all corners at the same elevation,
# there are two deviations from breadth first search:
# 1. Instead of pushing to the end of the queue, push to the beginning.
# 2. Like uniform cost search, check if the new distance is better than
#     previously calculated distances. It is possible that one lake corner
#     was reached with distance 2 and another with distance 3, and we need
#     to revisit that node and make sure it's set to 2.
# 
def assign_t_elevation(
    t_elevation, t_coastdistance, t_downslope_s,
    mesh,
    r_ocean, r_water, randInt
	):
	t_coastdistance.length = mesh.numTriangles
	t_downslope_s.length = mesh.numTriangles
	t_elevation.length = mesh.numTriangles
	t_coastdistance.fill(None)
	t_downslope_s.fill(-1)
    
	# constants/lambda functions
	t_ocean = lambda t: r_ocean[mesh.s_begin_r(3*t)]
	r_lake = lambda r:r_water[r] and not r_ocean[r]
	s_lake = lambda s: r_lake(mesh.s_begin_r(s)) or r_lake(mesh.s_end_r(s))

	out_s = []
	queue_t = find_coasts_t(mesh, r_ocean)
	for t in queue_t:
		t_coastdistance[t] = 0
	minDistance, maxDistance = 1, 1

	while queue_t.length > 0:

		current_t = queue_t[0]
		queue_t = queue_t[1:]
		mesh.t_circulate_s(out_s, current_t)
		iOffset = randInt(out_s.length)
		for i in range(0,out_s.length):
			s = out_s[(i + iOffset) % out_s.length]
			lake = s_lake(s)
			neighbor_t = mesh.s_outer_t(s)
			newDistance = (1 if lake else 0) + t_coastdistance[current_t]
			if t_coastdistance[neighbor_t] == None or newDistance < t_coastdistance[neighbor_t]:
				t_downslope_s[neighbor_t] = mesh.s_opposite_s(s)
				t_coastdistance[neighbor_t] = newDistance
				if (t_ocean(neighbor_t) and newDistance > minDistance):
					minDistance = newDistance
				if (not t_ocean(neighbor_t) and newDistance > maxDistance):
					maxDistance = newDistance
				if lake:
					queue_t.insert(0,neighbor_t)
				else:
					queue_t.append(neighbor_t)

	for t,d in enumerate(t_coastdistance):
		t_elevation[t] = (-d / minDistance) if t_ocean(t) else (d / maxDistance)


# 
# Set r elevation to the average of the t elevations. There's a
# corner case though: it is possible for an ocean region (r) to be
# surrounded by coastline corners (t), and coastlines are set to 0
# elevation. This means the region elevation would be 0. To avoid
# this, I subtract a small amount for ocean regions. */
def assign_r_elevation(r_elevation, mesh, t_elevation, r_ocean):
	max_ocean_elevation = -0.01
	r_elevation.length = mesh.numRegions
	out_t = []
	for r in range(0,mesh.numRegions):
		mesh.r_circulate_t(out_t, r)
		elevation = 0.0
		for t in out_t:
			elevation = elevation + t_elevation[t]
		r_elevation[r] = elevation/out_t.length
		if r_ocean[r] and r_elevation[r] > max_ocean_elevation:
			r_elevation[r] = max_ocean_elevation
	return r_elevation


#
# Redistribute elevation values so that lower elevations are more common
# than higher elevations. Specifically, we want elevation Z to have frequency
# (1-Z), for all the non-ocean regions.
#
# TODO: this messes up lakes, as they will no longer all be at the same elevation
def redistribute_t_elevation(t_elevation, mesh):
	# NOTE: This is the same algorithm I used in 2010, because I'm
	# trying to recreate that map generator to some extent. I don't
	# think it's a great approach for other games but it worked well
	# enough for that one.
	
	# SCALE_FACTOR increases the mountain area. At 1.0 the maximum
	# elevation barely shows up on the map, so we set it to 1.1.
	SCALE_FACTOR = 1.1

	nonocean_t = []
	for t in range(0,mesh.numSolidTriangles):
		if t_elevation[t] > 0.0:
			nonocean_t.append(t)
	
	nonocean_t.sort(key=lambda t1, t2: t_elevation[t1] - t_elevation[t2])

	for i in range(0,nonocean_t.length):
		# Let y(x) be the total area that we want at elevation <= x.
		# We want the higher elevations to occur less than lower
		# ones, and set the area to be y(x) = 1 - (1-x)^2.
		y = i / (nonocean_t.length-1)
		# Now we have to solve for x, given the known y.
		#  *  y = 1 - (1-x)^2
		#  *  y = 1 - (1 - 2x + x^2)
		#  *  y = 2x - x^2
		#  *  x^2 - 2x + y = 0
		# From this we can use the quadratic equation to get:
		x = math.sqrt(SCALE_FACTOR) - math.sqrt(SCALE_FACTOR*(1-y))
		if x > 1.0:
			x = 1.0
		t_elevation[nonocean_t[i]] = x