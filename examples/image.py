#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from AxiSurface import *
from AxiSurface.convert import *

import numpy as np
import matplotlib.pyplot as plt

invert = False
threshold_value = 0.5
angle = 10
scale = 0.1
translate=[0.0, 40.0]
samples = 20
texture_resolution = 200

# Depth
heightmap = Image('lucy_depth.png')
mask = heightmap.copy()
mask.threshold(0.1)

grayscale = Image( 'lucy_dof.png' )

axi = AxiSurface()

contours = Path()
for threshold in range(samples):
    contours.add( ImageContourToPath(heightmap, 0.1+threshold*0.01) )

contours_texture = contours.getScaled(scale).getTexture(width=heightmap.width*scale, height=heightmap.height*scale)
# contours_texture.transform = [100.0, 150.0]  
axi.texture( contours_texture, translate=[0.0, 150.0]  )
axi.text( "ImageContourToPath > Texture", center=[50.0, 250.0], scale=0.1 )

axi.texture( GrayscaleToTexture(grayscale, threshold=0.5, invert=invert, texture_resolution=200, texture_angle=45, mask=mask), translate=[0.0, 15.0] )
axi.text( "GrayscaleToTexture", center=[50.0, 100.0], scale=0.1 )

axi.texture( HeightmapToTexture(heightmap, camera_angle=angle, grayscale=grayscale, threshold=threshold_value, invert=invert, texture_resolution=texture_resolution, texture_angle=45, mask=mask), translate=[100.0, 20.0] )
axi.text( "HeightmapToTexture", center=[150.0, 100.0], scale=0.1 )

contours_filtered_texture = HeightmapToTexture(heightmap, camera_angle=angle, grayscale=grayscale, threshold=threshold_value, invert=invert, texture=contours_texture, mask=mask)
axi.texture( contours_filtered_texture, translate=[100.0, 150.0] )
axi.text( "ImageContourToPath > Texture > HeightmapToTexture ", center=[150.0, 250.0], scale=0.1 )

axi.toSVG('image.svg')