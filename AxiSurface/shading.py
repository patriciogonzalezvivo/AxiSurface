
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import svgwrite

import numpy as np
from .image import load_grayscale, load_normalmap, remove_mask, remove_threshold
from .texture import make_stripes_texture, rotate_texture, texture_map, texture_plot, fit_texture

# import matplotlib.pyplot as plt
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
        z_coef * surface -
        y_coef * np.expand_dims(np.linspace(0., 1., s), axis=1)
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

def layer_to_path_gen(layer):
    """Generates an SVG path from a given layer.
    Args:
        layer (layer): the layer to convert
    Yields:
        str: the next component of the path
    """
    draw = False
    for x, y in zip(*layer):
        if np.isnan(x) or np.isnan(y):
            draw = False
        elif not draw:
            yield 'M {} {}'.format(x, y)
            draw = True
        else:
            yield 'L {} {}'.format(x, y)


def layer_to_path(layer):
    """Generates an SVG path from a given layer.
    Args:
        layer (layer): the layer to convert
    Returns:
        str: an SVG path
    """
    return ' '.join(layer_to_path_gen(layer))


def addLayers(svg_surface, layers, name="shading"):
    flipped_plot = [(x * svg_surface.width, -y * svg_surface.height) for x, y in layers]
    root = svg_surface.body.add( svgwrite.container.Group(id=name, fill='none', stroke='black', stroke_width=STROKE_WIDTH ) )
    for layer in flipped_plot:
        root.add( svgwrite.path.Path(d=layer_to_path(layer)) )

#  High Level Operations
#  --------------------------------------------------------

def gradient_texture(layers, gradientmap, angle, camera_angle=0, invert=False, mask=None, total_shades=10, num_lines=100, resolution=500):

    # Mask
    use_mask = False
    if isinstance(mask, (np.ndarray, np.generic) ):
        use_mask = True

    tonestep = 1.0 / total_shades
    for shade in range(total_shades):
        tone = shade * tonestep

        grad = gradientmap.copy()
        
        if invert:
            grad = remove_mask(grad, tone < grad)
        else:
            grad = remove_mask(grad, 1.0-tone > grad)
        
        if use_mask:
            grad = remove_mask(grad, mask)

        # plt.imshow(grad, cmap='gray');
        # plt.show()
        
        offset = shade/total_shades 
        texture_sub = make_stripes_texture( num_lines, resolution, offset )

        resolution_unit = 1.0 / resolution
        resolution_offset = offset * resolution_unit

        lines_unit = 1.0 / num_lines
        lines_offset = offset * lines_unit

        texture_sub = rotate_texture(texture_sub, angle) #, x_offset=resolution_unit*0.5, y_offset=lines_offset*0.5)

        lines = texture_plot(texture_sub, grad, camera_angle)
        layers.append(lines)


def shadeGrayscale( svg_surface, filename, texture_angle=0, texture_presicion=1.0, total_shades=6, mask=None, texture_resolution=None):
    gradientmap = load_grayscale( filename )

    # Texture
    height, width = heightmap.shape[:2]

    if texture_resolution == None:
        texture_resolution = min(width, height) * 0.5

    # Mask 
    if isinstance(mask, basestring) or isinstance(mask, str):
        mask = load_grayscale(mask) > 0.5

    gradient_texture(layers, gradientmap, angle, mask=mask, total_shades=total_shades, num_lines=100, resolution=min(width, height) * texture_presicion)

    addLayers(svg_surface, layers, filename)


def shadeHeightmap( svg_surface, filename, texture_angle=0, camera_angle=1.0, texture_presicion=1.0, threshold=None, mask=None, texture=None, texture_resolution=None):

    heightmap = load_grayscale( filename )

    # Remove not visible
    heightmap = remove_mask(heightmap, make_visible_mask(heightmap, camera_angle))

    if threshold != None:
        heightmap = remove_threshold(heightmap, threshold)

    # Mask
    if isinstance(mask, basestring) or isinstance(mask, str):
        mask_heightmap = load_grayscale(mask)
        heightmap = remove_mask(heightmap, mask_heightmap > 0.5 )
    elif isinstance(mask, (np.ndarray, np.generic) ):
        heightmap = remove_mask(heightmap, mask)

    # Texture
    height, width = heightmap.shape[:2]

    if texture_resolution == None:
        texture_resolution = min(width, height) * 0.5

    if texture == None:
        texture = make_stripes_texture(texture_resolution, min(width, height) * texture_presicion)
        # texture = make_grid_texture(100, 100, 200)

    if texture_angle != 0:
        texture = rotate_texture(texture, texture_angle)

    # texture = fit_texture(texture)

    layer = texture_plot(texture, heightmap, camera_angle)
    
    addLayers(svg_surface, [layer], filename)

def shadeNormalmap( svg_surface, filename, total_faces=18, texture_presicion=1.0, mask=None, texture=None, texture_resolution=None, grayscale=None ):
    normalmap = load_normalmap( filename )

    # Texture 
    height, width = normalmap.shape[:2]
    if texture_resolution == None:
        texture_resolution = min(width, height) * 0.5

    if texture == None:
        texture = make_stripes_texture(texture_resolution, min(width, height) * texture_presicion)

    #  ANGLE MAP
    anglemap = normal2angle( normalmap )
    anglemap = (anglemap / np.pi) * 0.5 + 0.5
    step = 1.0/total_faces
    step_angle = 360.0/total_faces
    anglemap = decimate(anglemap, float(total_faces))

    # Mask 
    use_mask = False
    if isinstance(mask, basestring) or isinstance(mask, str):
        mask = load_grayscale(mask) > 0.5
        use_mask = True
    elif isinstance(mask, (np.ndarray, np.generic) ):
        use_mask = True

    # Grayscale
    use_grayscale = False
    if isinstance(grayscale, basestring) or isinstance(grayscale, str):
        grayscale = load_grayscale(mask)
        use_grayscale = True
    elif isinstance(grayscale, (np.ndarray, np.generic) ):
        use_grayscale = True

    layers = []
    for cut in range(total_faces):
        surface = anglemap.copy()
        surface.fill(1.0)

        if use_mask:
            surface = remove_mask(surface, mask)   

        mask_sub = np.isclose(anglemap, cut * step)
        surface = remove_mask(surface, mask_sub)

        angle_sub = cut*-step_angle + 90

        if use_grayscale:
            gradient_texture(layers, grayscale, angle_sub, mask=surface > 0.5, num_lines=200, total_shades=10, resolution=min(width, height) * texture_presicion)
        else:
            texture_sub = rotate_texture(texture, angle_sub)
            lines = texture_plot(texture_sub, surface, 0)
            layers.append(lines)

    addLayers(svg_surface, layers, filename)
