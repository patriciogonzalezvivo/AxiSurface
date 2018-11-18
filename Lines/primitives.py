#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math

import svgwrite

from math_func import polar2xy, perpendicular

STROKE_WIDTH = 0.2

def lineProp(pointA, pointB):
    lengthX = pointB[0] - pointA[0]
    lengthY = pointB[1] - pointA[1]
    return math.sqrt( math.pow(lengthX, 2) + math.pow(lengthY, 2)), math.atan2(lengthY, lengthX)


def controlPoint(current, _previous, _next, reverse):
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


def bezierCommand(point, i, a):

    #  start control point
    cpsX, cpsY = controlPoint(a[i - 1], a[i - 2], point, False) 

    #  end control point
    if i + 1 >= len(a):
        cpeX, cpeY = controlPoint(point, a[i - 1], None, True)
    else:
        cpeX, cpeY = controlPoint(point, a[i - 1], a[i + 1], True)

    return ' C ' + str(cpsX) + ',' + str(cpsY) + " " + str(cpeX) + "," + str(cpeY) + " " + str(point[0]) + "," + str(point[1])


# --------------------------------------------------- draw functions 

def dot(_parent, _center, _radius):
    rad = _radius
    while rad >= 0:
        _parent.add( svgwrite.shapes.Circle(center=_center, r=rad) )
        rad -= STROKE_WIDTH

def line(_parent, _posA, _posB, width=1):
    if width > 1:
        perp = perpendicular(A, B)
        _posA += perp * STROKE_WIDTH * 0.5
        _posB += perp * STROKE_WIDTH * 0.5
        _parent.add( svgwrite.shapes.Line(_posA, _posB) )
        _posA -= perp * STROKE_WIDTH 
        _posB -= perp * STROKE_WIDTH 
        _parent.add( svgwrite.shapes.Line(_posA, _posB) )
    else:
        _parent.add( svgwrite.shapes.Line(_posA, _posB) )


def arc(_parent, _posA, _posB, _rad):
    """ Adds an arc that bulges to the right as it moves from _posA to _posB """
    args = {
        'x0':_posA[0], 
        'y0':_posA[1], 
        'xradius':_radius, 
        'yradius':_radius, 
        'ellipseRotation':0, #has no effect for circles
        'x1':(_posB[0]-_posA[0]), 
        'y1':(_posB[1]-_posA[1])}

    path_string = "M %(x0)f,%(y0)f a %(xradius)f,%(yradius)f %(ellipseRotation)f 0,0 %(x1)f,%(y1)f"%args
    _parent.add( svgwrite.path.Path(d=path_string, fill="none", stroke='black', stroke_width=STROKE_WIDTH) )


def circle(_parent, _center, _radius, _open_angle=None, _offset_angle = 0):
    if _open_angle != None:
        _posA = polar2xy(_center[0], _center[1], _offset_angle + _open_angle, _radius)
        _posB = polar2xy(_center[0], _center[1], _offset_angle + 360 - _open_angle, _radius)
        args = {
                'x0':_posA[0], 
                'y0':_posA[1], 
                'xradius':_radius, 
                'yradius':_radius, 
                'ellipseRotation':0,
                'x1':_posB[0], 
                'y1':_posB[1]
            }

        path_string = "M %(x0)f,%(y0)f A %(xradius)f,%(yradius)f%(ellipseRotation)f 1,1 %(x1)f,%(y1)f"%args
        _parent.add( svgwrite.path.Path(d=path_string, fill="none", stroke='black', stroke_width=STROKE_WIDTH) )
    else:
        _parent.add( svgwrite.shapes.Circle(center=center, r=radius, fill="none", stroke='black', stroke_width=STROKE_WIDTH) )

def rect(_parent, _center, size=(1,1)):
    _parent.add( svgwrite.shapes.Rect(insert=_center, size=size) )

def polyline(_parent, _points):
    _parent.add( svgwrite.path.Polyline(points=_points, fill="none", stroke='black', stroke_width=STROKE_WIDTH) )

def path(_parent, _points):
    path_string = "M " + str(_points[0][0]) + " " + str(_points[0][1])

    for point in _points[1:]:
        path_string += " L " + str(point[0]) + " " + str(point[1])
    
    _parent.add( svgwrite.path.Path(d=path_string, fill="none", stroke='black', stroke_width=STROKE_WIDTH) )

def smoothPath(_parent, _points):
    path_string = "M " + str(_points[0][0]) + " " + str(_points[0][1])

    for i in range(1, len(_points)):
        path_string += bezierCommand(_points[i], i, _points)
    
    _parent.add( svgwrite.path.Path(d=path_string, fill="none", stroke='black', stroke_width=STROKE_WIDTH) )
