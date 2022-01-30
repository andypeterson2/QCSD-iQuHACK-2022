#
# From http://www.redblobgames.com/maps/mapgen2/
# Copyright 2017 Red Blob Games <redblobgames@gmail.com>
# License: Apache v2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>
#

from util import *

# 'use strict';
# const util = require('./util');

from pickle import FALSE


def biome(ocean, water, coast, temperature, moisture):

	if ocean:
		return 'OCEAN'
	elif water:
		if temperature > 0.9:
			return 'MARSH'
		if temperature < 0.2:
			return 'ICE'
		return 'LAKE'
	elif coast:
		return 'BEACH'
	elif temperature < 0.2:
		if moisture > 0.50: 
			return 'SNOW'
		elif moisture > 0.33: 
			return 'TUNDRA'
		elif moisture > 0.16:
			return 'BARE'
		return 'SCORCHED'
	elif temperature < 0.4:
		if moisture > 0.66: 
			return 'TAIGA'
		elif moisture > 0.33: 
			return 'SHRUBLAND'
		return 'TEMPERATE_DESERT'
	elif temperature < 0.7:
		if moisture > 0.83: 
			return 'TEMPERATE_RAIN_FOREST'
		elif moisture > 0.50: 
			return 'TEMPERATE_DECIDUOUS_FOREST'
		elif moisture > 0.16: 
			return 'GRASSLAND'
		return 'TEMPERATE_DESERT'
	else:
		if moisture > 0.66: 
			return 'TROPICAL_RAIN_FOREST'
		elif moisture > 0.33: 
			return 'TROPICAL_SEASONAL_FOREST'
		elif moisture > 0.16: 
			return 'GRASSLAND'
		return 'SUBTROPICAL_DESERT'

#
# A coast region is land that has an ocean neighbor
#

def assign_r_coast(r_coast, mesh, r_ocean):
    r_coast.length = mesh.numRegions
    r_coast.fill(FALSE)
    
    out_r = []
    for r1 in range(0,mesh.numRegions):
        mesh.r_circulate_r(out_r, r1)
        if not r_ocean[r1]:
            for r2 in out_r:
                if r_ocean[r2]:
                    r_coast[r1] = TRUE
                    break
    return r_coast

#
# Temperature assignment
#
# Temperature is based on elevation and latitude.
# The normal range is 0.0=cold, 1.0=hot, but it is not 
# limited to that range, especially when using temperature bias.
#
# The northernmost parts of the map get bias_north added to them;
# the southernmost get bias_south added; in between it's a blend.
#
def assign_r_temperature(
    r_temperature,  
    mesh,
    r_ocean, r_water,
    r_elevation, r_moisture,
    bias_north, bias_south
	):
    r_temperature.length = mesh.numRegions
    for r in range(0,mesh.numRegions):
		# 0.0 - 1.0
        latitude = mesh.r_y(r) / 1000; 
        d_temperature = mix(bias_north, bias_south, latitude)        # mix is imported
        r_temperature[r] = 1.0 - r_elevation[r] + d_temperature
    return r_temperature



 #Biomes assignment -- see the biome() function above
 #
def assign_r_biome(
    r_biome,
    mesh,
    r_ocean, r_water, r_coast, r_temperature, r_moisture
	):
    r_biome.length = mesh.numRegions
    for r in range(0,mesh.numRegions):
        r_biome[r] = biome(r_ocean[r], r_water[r], r_coast[r],
                           r_temperature[r], r_moisture[r])
    return r_biome


