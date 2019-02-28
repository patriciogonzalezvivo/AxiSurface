#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from AxiSurface import *

WIDTH = 297.0
# HEIGHT = 420.0
# CENTER = (WIDTH*0.5, HEIGHT*0.5)
MARGIN = WIDTH*0.01

fonts = [ASTROLOGY, CURSIVE, CYRILC_1, CYRILLIC, FUTURAL, FUTURAM, GOTHGBT, GOTHGRT, GOTHICENG, GOTHICGER, GOTHICITA, GOTHITT, GREEK, GREEKC, GREEKS, JAPANESE, MARKERS, MATHLOW, MATHUPP, METEOROLOGY, MUSIC, ROWMAND, ROWMANS, ROWMANT, SCRIPTC, SCRIPTS, SYMBOLIC, TIMESG, TIMESI, TIMESIB, TIMESR, TIMESRB]
fonts_names = ['ASTROLOGY', 'CURSIVE', 'CYRILC_1', 'CYRILLIC', 'FUTURAL', 'FUTURAM', 'GOTHGBT', 'GOTHGRT', 'GOTHICENG', 'GOTHICGER', 'GOTHICITA', 'GOTHITT', 'GREEK', 'GREEKC', 'GREEKS', 'JAPANESE', 'MARKERS', 'MATHLOW', 'MATHUPP', 'METEOROLOGY', 'MUSIC', 'ROWMAND', 'ROWMANS', 'ROWMANT', 'SCRIPTC', 'SCRIPTS', 'SYMBOLIC', 'TIMESG', 'TIMESI', 'TIMESIB', 'TIMESR', 'TIMESRB']


axi = AxiSurface()

def charRow(y, font_index):
    axi.text( fonts_names[font_index], [WIDTH*0.1, y + 5], scale=0.1, stroke_width=2.0)
    y += 10
    str_line = ""
    for i in range(32, 128):
        if i == 91:
            axi.text(str_line, [WIDTH*0.5,y], scale=0.15, font=fonts[font_index])
            y += 5
            str_line = ""

        str_line += chr(i)
    axi.text(str_line, [WIDTH*0.5,y], scale=0.15, font=fonts[font_index])
    
    

y = MARGIN
for i in range(len(fonts)):
    charRow(y, i)
    y += 20

axi.toSVG('fonts.svg')