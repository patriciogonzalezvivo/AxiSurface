#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math

import svgwrite

from .AxiSurface import AxiSurface
from .tools import polar2xy, perpendicular, bezierCommand

STROKE_WIDTH = 0.2

# BASIC ELEMENTS
# ------------------------

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


def arc( parent, posA, posB, radius_x, rsdius_y=None ):
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


# BASIC SHAPES
# ------------------------

def circle( parent, center, radius, open_angle=None, offset_angle=0):
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


def rect( parent, center, size=(1,1) ):
    if isinstance(parent, AxiSurface):
        parent = parent.body

    parent.add( svgwrite.shapes.Rect(insert=center, size=size) )

# HEXAGONS
# ------------------------

def hexagon_corner(center, radius, i):
    angle_deg = 60.0 * i - 30.0
    angle_rad = math.pi / 180.0 * angle_deg
    return [center[0] + radius * math.cos(angle_rad), center[1] + radius * math.sin(angle_rad)]


def hexagon_coorners(center, radius):
    points = []
    for i in range(0, 6):
        points.append( hexagon_corner(center, radius, i) )
    return points


def hexagon_grid(center, cols, rows, hexagon_radius):
    hexagon_width = math.sqrt(3.0) * hexagon_radius
    hexagon_height = 2.0 * hexagon_radius

    points = []
    for row in range(-int(rows/2), int(rows/2)):
        for col in range(-int(cols/2), int(cols/2)):
            x = col * hexagon_width
            y = row * hexagon_height * 3/4
            if row % 2:
                x += hexagon_width * 0.5
            points.append([center[0] + x, center[1] + y])
    return points


def hexagon(parent, center, radius, type = 0):
    if isinstance(parent, AxiSurface):
        parent = parent.body

    if type == 0:
        # Close border
        points = hexagon_coorners(center, radius)
        points.append( points[0] )
        parent.add( svgwrite.shapes.Polyline(points=points, fill="none", stroke='black', stroke_width=STROKE_WIDTH) )

    elif type == 1:
        # Inner lines
        points = hexagon_coorners(center, radius)
        parent.add( svgwrite.shapes.Line(points[0], center) )
        parent.add( svgwrite.shapes.Line(points[2], center) )
        parent.add( svgwrite.shapes.Line(points[4], center) )

    elif type == 2:
        # Inner lines
        hexagon(parent=parent, center=center, radius=radius, type=0)
        hexagon(parent=parent, center=center, radius=radius, type=1)

    elif type == 3:
        # Inner lines
        points = hexagon_coorners(center, radius)
        parent.add( svgwrite.shapes.Line(points[1], center) )
        parent.add( svgwrite.shapes.Line(points[3], center) )
        parent.add( svgwrite.shapes.Line(points[5], center) )

    elif type == 4:
        # Inner lines
        hexagon(parent=parent, center=center, radius=radius, type=0)
        hexagon(parent=parent, center=center, radius=radius, type=3)

    elif type == 5:
        # Vertical lines
        points = hexagon_coorners(center, radius)
        parent.add( svgwrite.shapes.Line(points[5], points[2]) )


# POLYLINES
# ------------------------


def polyline( parent, points ):
    if isinstance(parent, AxiSurface):
        parent = parent.body

    parent.add( svgwrite.shapes.Polyline(points=points, fill="none", stroke='black', stroke_width=STROKE_WIDTH) )


# PATHS
# ------------------------


def path( parent, path_str ):
    if isinstance(parent, AxiSurface):
        parent = parent.body

    # if isinstance(path_str, basestring) or isinstance(path_str, str):
    parent.add( svgwrite.path.Path(d=path_str, fill="none", stroke='black', stroke_width=STROKE_WIDTH, debug=False) )
    # else:
    #     # asume path_str is actually an array of points
    #     path_str = "M " + str(points[0][0]) + " " + str(points[0][1])
    #     for point in points[1:]:
    #         path_str += " L " + str(point[0]) + " " + str(point[1])
    #     parent.add( svgwrite.path.Path(d=path_str, fill="none", stroke='black', stroke_width=STROKE_WIDTH) )


def smoothPath( parent, points ):
    if isinstance(parent, AxiSurface):
        parent = parent.body

    path_string = "M " + str(points[0][0]) + " " + str(points[0][1])

    for i in range(1, len(points)):
        path_string += bezierCommand(points[i], i, points)
    
    parent.add( svgwrite.path.Path(d=path_string, fill="none", stroke='black', stroke_width=STROKE_WIDTH) )
