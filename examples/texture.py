#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from AxiSurface import *

heightmap = Image('lucy_depth.png')
axi = AxiSurface()
contours = ImageContourToPath(heightmap, 0.1).getScaled(0.1)
contour = Polyline( contours.path[0] )

axi = AxiSurface()

texture_strip = Texture( stripes_texture(num_lines=100, resolution=100) )
axi.texture( texture_strip )
texture_strip.turn(45)
axi.texture( texture_strip, translate=[100.0, 0.0], scale=0.70)
texture_strip.mask( contour, 100, 100)
axi.texture( texture_strip, translate=[200.0, 0.0])


texture_crosses = Texture(crosses_textures(resolution=33))
axi.texture( texture_crosses, translate=[0.0, 100.0])
texture_crosses.turn(45)
axi.texture( texture_crosses, translate=[100.0, 100.0], scale=0.70 )
texture_crosses.mask( contour, 100, 100)
axi.texture( texture_crosses, translate=[200.0, 100.0])


# texture_grid = Texture( grid_texture(num_h_lines=50, num_v_lines=50 ) )
# axi.texture( texture_grid, translate=[0.0, 100.0])
# texture_grid.turn(45)
# axi.texture( texture_grid, translate=[100.0, 100.0], scale=0.70 )
# texture_grid.mask( contour, 100, 100)
# axi.texture( texture_grid, translate=[200.0, 100.0])

# texture_spiral = Texture( spiral_texture(spirals=20) )
# axi.texture( texture_spiral, translate=[0.0, 200.0])
# texture_spiral.mask( contour, 100, 100)
# axi.texture( texture_spiral, translate=[0.0, 300.0])

# texture_hex = Texture( hex_texture(), scale=0.01 )
# texture_hex.mask( contour, 100, 100)
# axi.texture( texture_hex, translate=[100.0, 200.0])

axi.toSVG('texture.svg')