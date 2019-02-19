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

invert = True
threshold_value = 0.5
angle = 10
scale = 0.2
translate=[0.0, 40.0]
samples = 20

# Depth
heightmap = Image('lucy_depth.png')
mask = heightmap.copy()
mask.threshold(0.1)

grayscale = Image( 'lucy_dof.png' )

axi = AxiSurface()

contours = Path()
for threshold in range(samples):
    contours.add( ImageContourToPath(heightmap, 0.1+threshold*0.01) )

texture = contours.getScaled(scale).getTexture(width=heightmap.width*scale, height=heightmap.height*scale)
# texture = GrayscaleToTexture(grayscale, texture=texture,invert=invert, mask=mask)
texture = HeightmapToTexture(heightmap, texture=texture, camera_angle=angle, grayscale=grayscale, threshold=threshold_value, invert=invert, mask=mask)
axi.texture( texture )

axi.toSVG('lucy.svg')