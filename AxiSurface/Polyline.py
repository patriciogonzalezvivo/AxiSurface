#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .tools import pointInside, linesIntersection

class Polyline(object):
    def __init__( self, points ):

        self.points = points

    def inside( self, pos ):
        return pointInside( pos, self.points )
