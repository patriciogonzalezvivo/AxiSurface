#!/usr/bin/env python

"""
AxiSurface: Simple Python 2/3 module to make line SVG files for plotting
"""

from distutils.core import setup

doc_axisurface = __doc__.split('\n')

setup(  
  name              = 'AxiSurface',
  description       = doc_axisurface[0],
  long_description  = '\n'.join(doc_axisurface[2:]),
  version           = '0.1',
  author            = 'Patricio Gonzalez Vivo',
  author_email      = 'patriciogonzalezvivo@gmail.com',
  packages          = [ 'AxiSurface' ]
)