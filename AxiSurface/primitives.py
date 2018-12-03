#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math

import svgwrite

from AxiSurface.AxiSurface import AxiSurface
from AxiSurface.tools import polar2xy, perpendicular, bezierCommand

STROKE_WIDTH = 0.2


def dot( parent, center, radius ):
    if isinstance(parent, AxiSurface):
        parent = parent.body

    rad = radius
    while rad >= 0:
        parent.add( svgwrite.shapes.Circle(center=center, r=rad) )
        rad -= STROKE_WIDTH


def line( parent, posA, posB, width=1 ):
    if isinstance(parent, AxiSurface):
        parent = parent.body

    if width > 1.0:
        perp = perpendicular(posA, posB)
        posA += perp * STROKE_WIDTH * 0.5
        posB += perp * STROKE_WIDTH * 0.5
        parent.add( svgwrite.shapes.Line(posA, posB) )
        posA -= perp * STROKE_WIDTH 
        posB -= perp * STROKE_WIDTH 
        parent.add( svgwrite.shapes.Line(posA, posB) )
    else:
        parent.add( svgwrite.shapes.Line(posA, posB) )


def arc( parent, posA, posB, radius ):
    """ Adds an arc that bulges to the right as it moves from posA to posB """

    if isinstance(parent, AxiSurface):
        parent = parent.body

    args = {
        'x0':posA[0], 
        'y0':posA[1], 
        'xradius':radius, 
        'yradius':radius, 
        'ellipseRotation':0, #has no effect for circles
        'x1':(posB[0]-posA[0]), 
        'y1':(posB[1]-posA[1])}

    path_string = "M %(x0)f,%(y0)f a %(xradius)f,%(yradius)f %(ellipseRotation)f 0,0 %(x1)f,%(y1)f"%args
    parent.add( svgwrite.path.Path(d=path_string, fill="none", stroke='black', stroke_width=STROKE_WIDTH) )


def circle(parent, center, radius, open_angle=None, offset_angle=0):
    if isinstance(parent, AxiSurface):
        parent = parent.body

    if open_angle != None:
        posA = polar2xy(center, offset_angle + open_angle, radius)
        posB = polar2xy(center, offset_angle + 360 - open_angle, radius)
        args = {
                'x0':posA[0], 
                'y0':posA[1], 
                'xradius':radius, 
                'yradius':radius, 
                'ellipseRotation':0,
                'x1':posB[0], 
                'y1':posB[1]
            }

        path_string = "M %(x0)f,%(y0)f A %(xradius)f,%(yradius)f%(ellipseRotation)f 1,1 %(x1)f,%(y1)f"%args
        parent.add( svgwrite.path.Path(d=path_string, fill="none", stroke='black', stroke_width=STROKE_WIDTH) )
    else:
        parent.add( svgwrite.shapes.Circle(center=center, r=radius, fill="none", stroke='black', stroke_width=STROKE_WIDTH) )

def rect(parent, center, size=(1,1)):
    if isinstance(parent, AxiSurface):
        parent = parent.body

    parent.add( svgwrite.shapes.Rect(insert=center, size=size) )

def polyline(parent, points):
    if isinstance(parent, AxiSurface):
        parent = parent.body

    parent.add( svgwrite.shapes.Polyline(points=points, fill="none", stroke='black', stroke_width=STROKE_WIDTH) )

def path(parent, points):
    if isinstance(parent, AxiSurface):
        parent = parent.body

    parent.add( svgwrite.path.Path(d=points, fill="none", stroke='black', stroke_width=STROKE_WIDTH, debug=False) )

    # path_string = "M " + str(points[0][0]) + " " + str(points[0][1])
    # for point in points[1:]:
    #     path_string += " L " + str(point[0]) + " " + str(point[1])
    # parent.add( svgwrite.path.Path(d=path_string, fill="none", stroke='black', stroke_width=STROKE_WIDTH) )

def smoothPath(parent, points):
    if isinstance(parent, AxiSurface):
        parent = parent.body

    path_string = "M " + str(points[0][0]) + " " + str(points[0][1])

    for i in range(1, len(points)):
        path_string += bezierCommand(points[i], i, points)
    
    parent.add( svgwrite.path.Path(d=path_string, fill="none", stroke='black', stroke_width=STROKE_WIDTH) )
