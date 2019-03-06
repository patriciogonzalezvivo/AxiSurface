#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from AxiSurface import *
from AxiSurface.tools import remap

# Depth
img = Image('logo_sdf.png')
area_size = [70, 70]

samples = 10
depth_target = -5.0
depth_step = depth_target/samples
threshold_step = 1.0/samples
head_width = 0.5

axi = AxiSurface(area_size)
gcode_str = axi.getGCODEHeader()


for i in range(1, samples):
    depth = i * depth_step
    threshold = i * threshold_step

    polygons = ImageThresholdToPolygons(img, threshold, scale=0.087)

    path = Path()
    for polygon in polygons:
        polygon.head_width = head_width
        polygon.fill = True

        # path.add( polygon.getPath().getSimplify().getSorted().getJoined() )

        path.add( polygon.getPath(overlap=0.0).getSimplify().getSorted().getJoined(boundary=polygon._toShapelyGeom()) )

        # if i == 1:
        #     path.add( polygon.getPath() )
        # else:
        #     path.add( polygon.getFillPath() )

    path.getSimplify().getSorted().getJoined()
    path = path.getCentered(axi.width, axi.height)
    path = path.getTranslated(-axi.width*0.5, -axi.height*0.5)
    print(i, threshold, depth, path.bounds)

    gcode_str += path.getGCodeString( head_down_height=depth )

gcode_str += axi.getGCODEFooter()

with open('logo.cnc', "w") as file:
    file.write(gcode_str)
