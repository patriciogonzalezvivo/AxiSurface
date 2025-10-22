#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from Surface import *

axi = Surface()

def charRow(y, font_index):
    axi.text( FONTS_NAMES[font_index], [axi.width*0.1, y + 5], scale=0.1, stroke_width=2.0)
    y += 10
    str_line = ""
    for i in range(32, 128):
        if i == 91:
            axi.text(str_line, [axi.width*0.5,y], scale=0.15, font=FONTS[font_index])
            y += 5
            str_line = ""

        str_line += chr(i)
    axi.text(str_line, [axi.width*0.5,y], scale=0.15, font=FONTS[font_index])
    
    

y = axi.width*0.01
for i in range(len(FONTS)):
    charRow(y, i)
    y += 20

axi.toSVG('fonts.svg')