#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math

import svgwrite

from Lines.math_func import polar2xy, perpendicular

STROKE_WIDTH = 0.2

def lineProp( pointA, pointB ):
    lengthX = pointB[0] - pointA[0]
    lengthY = pointB[1] - pointA[1]
    return math.sqrt( math.pow(lengthX, 2) + math.pow(lengthY, 2)), math.atan2(lengthY, lengthX)


def controlPoint( current, _previous, _next, reverse ):
    p = _previous
    n = _next

    if _previous == None:
        p = current
    if _next == None:
        n = current

    smoothing = 0.2
    o = lineProp(p, n) 

    angle = o[1]
    if reverse: 
        angle += math.pi
    length = o[0] * smoothing

    x = current[0] + math.cos(angle) * length
    y = current[1] + math.sin(angle) * length

    return [x, y]


def bezierCommand( point, i, a ):

    #  start control point
    cpsX, cpsY = controlPoint(a[i - 1], a[i - 2], point, False) 

    #  end control point
    if i + 1 >= len(a):
        cpeX, cpeY = controlPoint(point, a[i - 1], None, True)
    else:
        cpeX, cpeY = controlPoint(point, a[i - 1], a[i + 1], True)

    return ' C ' + str(cpsX) + ',' + str(cpsY) + " " + str(cpeX) + "," + str(cpeY) + " " + str(point[0]) + "," + str(point[1])


# --------------------------------------------------- draw functions 

def dot( parent, center, radius ):
    rad = radius
    while rad >= 0:
        parent.add( svgwrite.shapes.Circle(center=center, r=rad) )
        rad -= STROKE_WIDTH

def line( parent, posA, posB, width=1 ):
    if width > 1:
        perp = perpendicular(A, B)
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
    if open_angle != None:
        posA = polar2xy(center[0], center[1], offset_angle + open_angle, radius)
        posB = polar2xy(center[0], center[1], offset_angle + 360 - open_angle, radius)
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
    parent.add( svgwrite.shapes.Rect(insert=center, size=size) )

def polyline(parent, points):
    parent.add( svgwrite.path.Polyline(points=points, fill="none", stroke='black', stroke_width=STROKE_WIDTH) )

def path(parent, points):
    path_string = "M " + str(points[0][0]) + " " + str(points[0][1])

    for point in points[1:]:
        path_string += " L " + str(point[0]) + " " + str(point[1])
    
    parent.add( svgwrite.path.Path(d=path_string, fill="none", stroke='black', stroke_width=STROKE_WIDTH) )

def smoothPath(parent, points):
    path_string = "M " + str(points[0][0]) + " " + str(points[0][1])

    for i in range(1, len(points)):
        path_string += bezierCommand(points[i], i, points)
    
    parent.add( svgwrite.path.Path(d=path_string, fill="none", stroke='black', stroke_width=STROKE_WIDTH) )
