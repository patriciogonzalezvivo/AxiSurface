
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import svgwrite

import numpy as np
from .image import load_grayscale, load_normalmap, remove_mask, remove_threshold, dither
# from .texture import make_stripes_texture, rotate_texture, texture_map, texture_plot, fit_texture

from .Texture import *

import matplotlib.pyplot as plt
# from penkit.write import write_plot

STROKE_WIDTH = 0.2

# This code is adapted from Paul Butler great Surface Projection tutorial
# https://bitaesthetics.com/posts/surface-projection.html and PenKit https://github.com/paulgb/penkit/

#  Special Masks
#  --------------------------------------------------------

def make_visible_mask(surface, angle):
    s = surface.shape[0]
    
    # Just as in projection, we calculate the Y and Z
    # coefficients with sin/cos.
    y_coef = np.cos(np.radians(angle))
    z_coef = np.sin(np.radians(angle))
    
    # Rotate the surface so that the visibilty mask represents
    # the visibility at the desired angle.
    projected_surface = (
        - y_coef * np.expand_dims(np.linspace(0., 1., s), axis=1)
        + z_coef * surface
    )
    
    # Calculate the cumulative maximum along each cross-section of
    # the projected surface. We flip on the input and output because
    # we want to accumulate from the bottom of the surface up, rather
    # than the top-down. This is because we interpret the bottom of
    # the surface as closer to the observer.
    projected_surface_max = np.flipud(np.maximum.accumulate(np.flipud(projected_surface)))
    
    # Compare each point on the surface to the cumulative maximum
    # along its cross-section.
    return projected_surface == projected_surface_max


def normal2angle(image):
    return np.arctan2(image[..., 1], image[..., 0]) 


def decimate(array, dec):
    return (np.floor(array * dec)) / dec

# SVG convertion
#  --------------------------------------------------------

def shadeGrayscale( svg_surface, filename, threshold=0.5, invert=False, texture=None, texture_resolution=None, texture_presicion=1.0, texture_angle=0, texture_offset=0, mask=None ):
    if isinstance(filename, basestring) or isinstance(filename, str):
        gradientmap = load_grayscale( filename )
    else:
        gradientmap = filename

    shade = dither(gradientmap, threshold) < 0.5

    if invert:
        shade = not shade

    surface = gradientmap.copy()
    surface.fill(1.0)

    # Mask 
    if isinstance(mask, basestring) or isinstance(mask, str):
        mask = load_grayscale(mask) > 0.5

    if isinstance(mask, (np.ndarray, np.generic) ):
        surface= remove_mask(surface, mask )

    surface = remove_mask(surface, shade )

    # Texture
    height, width = gradientmap.shape[:2]

    if texture_resolution == None:
        texture_resolution = min(width, height) * 0.5

    if texture == None:
        texture = Texture( stripes_texture(texture_resolution, min(width, height) * texture_presicion, texture_offset) )

    if texture_angle > 0:
        texture.rotate(texture_angle)

    texture.plot(surface)

    root = svg_surface.body.add( svgwrite.container.Group(id=filename, fill='none', stroke='black', stroke_width=STROKE_WIDTH) )
    root.add( svgwrite.path.Path(d=texture.toPaths(svg_surface.width, svg_surface.height), debug=False) )


def shadeHeightmap( svg_surface, filename, camera_angle=1.0, grayscale=None, threshold=None, invert=False, texture=None, texture_resolution=None, texture_presicion=1.0, texture_angle=0, texture_offset=0, mask=None ):
    if isinstance(filename, basestring) or isinstance(filename, str):
        heightmap = load_grayscale( filename )
    else:
        heightmap = filename


    # Remove not visible
    # heightmap = remove_mask(heightmap, make_visible_mask(heightmap, camera_angle))

    # Mask
    if isinstance(mask, basestring) or isinstance(mask, str):
        mask = load_grayscale(mask) > 0.5
    
    if isinstance(mask, (np.ndarray, np.generic) ):
        heightmap = remove_mask(heightmap, mask)

    # Grayscale
    if isinstance(grayscale, basestring) or isinstance(grayscale, str):
        grayscale = load_grayscale(mask)

    if isinstance(grayscale, (np.ndarray, np.generic) ):
        if invert:
            shade = dither(grayscale, threshold) > 0.5
        else:
            shade = dither(grayscale, threshold) < 0.5
        
        heightmap = remove_mask(heightmap, shade)

    # Texture
    height, width = heightmap.shape[:2]
    if texture_resolution == None:
        texture_resolution = min(width, height) * 0.5

    if texture == None:
        texture = Texture( stripes_texture(texture_resolution, min(width, height) * texture_presicion, texture_offset) )

    if texture_angle != 0:
        texture.rotate(texture_angle)

    texture.plot(heightmap, camera_angle)
    
    root = svg_surface.body.add( svgwrite.container.Group(id=filename, fill='none', stroke='black', stroke_width=STROKE_WIDTH) )
    root.add( svgwrite.path.Path(d=texture.toPaths(svg_surface.width, svg_surface.height), debug=False) )

def shadeNormalmap( svg_surface, filename, total_faces=18, heightmap=None, camera_angle=0, grayscale=None, threshold=0.5, invert=False, texture=None, texture_resolution=None, texture_presicion=1.0, texture_angle=0, texture_offset=0, mask=None):
    if isinstance(filename, basestring) or isinstance(filename, str):
        normalmap = load_normalmap( filename )
    else:
        normalmap = filename

    # Angle map
    anglemap = normal2angle( normalmap )
    anglemap = (anglemap / np.pi) * 0.5 + 0.5
    step = 1.0/total_faces
    step_angle = 360.0/total_faces
    anglemap = decimate(anglemap, float(total_faces))

    surface = anglemap.copy()
    surface.fill(0.0)

    if isinstance(heightmap, basestring) or isinstance(heightmap, str):
        heightmap = load_grayscale( filename )
        
    if heightmap.any():
        # heightmap = remove_mask(heightmap, make_visible_mask(heightmap, camera_angle))
        surface = heightmap.copy()
        
    # Mask 
    if isinstance(mask, basestring) or isinstance(mask, str):
        mask = load_grayscale(mask) > 0.5

    if isinstance(mask, (np.ndarray, np.generic) ):
        surface = remove_mask(surface, mask )
        
    # Grayscale
    if isinstance(grayscale, basestring) or isinstance(grayscale, str):
        grayscale = load_grayscale(mask)

    if isinstance(grayscale, (np.ndarray, np.generic) ):
        if invert:
            shade = dither(grayscale, threshold) > 0.5
        else:
            shade = dither(grayscale, threshold) < 0.5
        
        surface = remove_mask(surface, shade )

    # Texture 
    height, width = normalmap.shape[:2]
    if texture_resolution == None:
        texture_resolution = min(width, height) * 0.5

    if texture == None:
        texture = stripes_texture(texture_resolution, min(width, height) * texture_presicion, texture_offset)

    root = svg_surface.body.add( svgwrite.container.Group(id=filename, fill='none', stroke='black', stroke_width=STROKE_WIDTH) )
    for cut in range(total_faces):
        sub_surface = surface.copy()

        mask_sub = np.isclose(anglemap, cut * step)
        sub_surface = remove_mask(sub_surface, mask_sub)

        angle_sub = cut*-step_angle + 90 + texture_angle

        texture_sub = Texture( texture )
        texture_sub.rotate(angle_sub)
        texture_sub.plot(sub_surface, camera_angle)

        root.add( svgwrite.path.Path(d=texture_sub.toPaths(svg_surface.width, svg_surface.height), debug=False) )