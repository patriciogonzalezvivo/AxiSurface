#!/usr/bin/env python

"""
Lines: Simple Python 2/3 module to make pure line SVG images for plotting
"""

from distutils.core import setup

doc_lines = __doc__.split('\n')

setup(  
  name              = 'Lines',
  description       = doc_lines[0],
  long_description  = '\n'.join(doc_lines[2:]),
  version           = '0.1',
  author            = 'Patricio Gonzalez Vivo',
  author_email      = 'patriciogonzalezvivo@gmail.com',
  packages          = [ 'Lines' ]
)