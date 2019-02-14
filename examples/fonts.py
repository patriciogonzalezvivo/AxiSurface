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
    x = MARGIN
    axi.text( fonts_names[font_index], translate=[WIDTH*0.1, y + 5], scale=0.15)
    y += 10
    for i in range(32, 128):
        if i == 91:
            x = MARGIN * 2.0
            y += 5
        t = axi.text( chr(i), translate=[x,y], scale=0.1, font=fonts[font_index])
        x += t.getWidth() * 2.0
    

y = MARGIN
for i in range(len(fonts)):
    charRow(y, i)
    y += 20

axi.toSVG('fonts.svg')