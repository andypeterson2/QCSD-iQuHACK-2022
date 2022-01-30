#
# From http://www.redblobgames.com/maps/mapgen2/
# Copyright 2017 Red Blob Games <redblobgames@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from qrng import *
from util import *
from water import *
from elevation import *
from rivers import *
from moisture import *
from biomes import *
from noisyedges import *

#
# Map generator
#
# Map coordinates are 0 ≤ x ≤ 1000, 0 ≤ y ≤ 1000.
#
# mesh: DualMesh
# noisyEdgeOptions: {length, amplitude, seed}
# makeRandInt: function(seed) -> function(N) -> an int from 0 to N-1
#
class Map:
    def __init__(self, mesh, noisyEdgeOptions, makeRandInt):
        self.mesh = mesh
        self.makeRandInt = makeRandInt
        self.s_lines = assign_s_segments(
            [],
            self.mesh,
            noisyEdgeOptions,
            self.makeRandInt(noisyEdgeOptions.seed)
        )

        self.r_water = []
        self.r_ocean = []
        self.t_coastdistance = []
        self.t_elevation = []
        self.t_downslope_s = []
        self.r_elevation = []
        self.s_flow = []
        self.r_waterdistance = []
        self.r_moisture = []
        self.r_coast = []
        self.r_temperature = []
        self.r_biome = []

 
    def calculate(self, options):
        #options = Object.assign({
        #    noise: null, // required: function(nx, ny) -> number from -1 to +1
        #    shape: {round: 0.5, inflate: 0.4, amplitudes: [1/2, 1/4, 1/8, 1/16]},
        #   numRivers: 30,
    	#  drainageSeed: 0,
	   	# riverSeed: 0,
        #noisyEdge: {length: 10, amplitude: 0.2, seed: 0},
        #biomeBias: {north_temperature: 0, south_temperature: 0, moisture: 0},
        #}, options)

        #assign_r_water(self.r_water, self.mesh, options.noise, options.shape)
        #assign_r_ocean(self.r_ocean, self.mesh, self.r_water)
        
#		#? what is this error here
		assign_t_elevation(
			self.t_elevation, self.t_coastdistance, self.t_downslope_s,
			self.mesh,
			self.r_ocean, self.r_water, self.makeRandInt(options.drainageSeed)
		)
		redistribute_t_elevation(self.t_elevation, self.mesh)
		assign_r_elevation(self.r_elevation, self.mesh, self.t_elevation, self.r_ocean)

		self.spring_t = find_spring_t(self.mesh, self.r_water, self.t_elevation, self.t_downslope_s)
		randomShuffle(self.spring_t, self.makeRandInt(options.riverSeed))
		
		self.river_t = self.spring_t.slice(0, options.numRivers)
		assign_s_flow(self.s_flow, self.mesh, self.t_downslope_s, self.river_t)
		
		assign_r_moisture(
			self.r_moisture, self.r_waterdistance,
			self.mesh,
			self.r_water, find_moisture_seeds_r(self.mesh, self.s_flow, self.r_ocean, self.r_water)
		)
		redistribute_r_moisture(self.r_moisture, self.mesh, self.r_water,
										options.biomeBias.moisture, 1 + options.biomeBias.moisture)

		assign_r_coast(self.r_coast, self.mesh, self.r_ocean)
		assign_r_temperature(
			self.r_temperature,
			self.mesh,
			self.r_ocean, self.r_water, self.r_elevation, self.r_moisture,
			options.biomeBias.north_temperature, options.biomeBias.south_temperature
		)
		assign_r_biome(
			self.r_biome,
			self.mesh,
			self.r_ocean, self.r_water, self.r_coast, self.r_temperature, self.r_moisture
		)
