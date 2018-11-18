#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from Lines import Surface, text, circle, rect

WIDTH = 297
HEIGHT = 420.0
MARGIN = WIDTH*0.05
SCALE = 1.0

paper = Surface()
t = paper.child('test')

circle(t, center=(paper.width*0.5, paper.height*0.5), radius=paper.width*0.5 )
rect(t, center=(0,0), size=(paper.width, paper.height) )
text(t, text='hello world', center=(paper.width*0.5, paper.height*0.5) )

paper.toSVG('test.svg')