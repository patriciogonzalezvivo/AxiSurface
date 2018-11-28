
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import svgwrite

import numpy as np
from PIL import Image

STROKE_WIDTH = 0.2

# This code is adapted from Paul Butler great Surface Projection tutorial
# https://bitaesthetics.com/posts/surface-projection.html and PenKit https://github.com/paulgb/penkit/

#  Textures
#  --------------------------------------------------------

def make_joy_texture(num_lines=10, resolution=50):
    # np.meshgrid is a handy way to generate a grid of points. It
    # returns a pair of matrices, which we will flatten into arrays.
    # For the x-coordinates, we put a nan value at the end so that when
    # we flatten them there is a separater between each horizontal line.
    x, y = np.meshgrid(
        np.hstack([np.linspace(0, 1, resolution), np.nan]),
        np.linspace(0, 1, num_lines),
    )
    
    # For coordinates where the x value is nan, set the y value to nan
    # as well. nan coordinates represent breaks in the path, indicating
    # here that the pen should be raised between each horizontal line.
    y[np.isnan(x)] = np.nan
    return x.flatten(), y.flatten()


def make_grid_texture(num_h_lines=10, num_v_lines=10, resolution=50):
    x_h, y_h = make_joy_texture(num_h_lines, resolution)
    y_v, x_v = make_joy_texture(num_v_lines, resolution)
    return np.concatenate([x_h, x_v]), np.concatenate([y_h, y_v])


def rotate_texture(texture, rotation, x_offset=0.5, y_offset=0.5):
    """Rotates the given texture by a given angle.
    Args:
        texture (texture): the texture to rotate
        rotation (float): the angle of rotation in degrees
        x_offset (float): the x component of the center of rotation (optional)
        y_offset (float): the y component of the center of rotation (optional)
    Returns:
        texture: A texture.
    """
    x, y = texture
    x = x.copy() - x_offset
    y = y.copy() - y_offset
    angle = np.radians(rotation)
    x_rot = x * np.cos(angle) + y * np.sin(angle)
    y_rot = x * -np.sin(angle) + y * np.cos(angle)
    return x_rot + x_offset, y_rot + y_offset


def fit_texture(layer):
    """Fits a layer into a texture by scaling each axis to (0, 1).
    Does not preserve aspect ratio (TODO: make this an option).
    Args:
        layer (layer): the layer to scale
    Returns:
        texture: A texture.
    """
    x, y = layer
    x = (x - np.nanmin(x)) / (np.nanmax(x) - np.nanmin(x))
    y = (y - np.nanmin(y)) / (np.nanmax(y) - np.nanmin(y))
    return x, y


def texture_map(texture, surface):
    texture_x, texture_y = texture
    surface_w, surface_h = surface.shape
    
    # First, we convert the points along the texture into integers within
    # the bounds of the surface's index. The clipping here will also convert
    # the nan values to 0.
    index_x = np.clip(np.int32(surface_w * texture_x), 0, surface_w - 1)
    index_y = np.clip(np.int32(surface_h * texture_y), 0, surface_h - 1)
    
    # Grab z-values along the texture path. Note that this will include values
    # for every point, even if it is nan or had to be clipped to within the
    # bounds of the surface, so we have to fix that next.
    surface_z = surface[index_x, index_y]
    
    # Set z-values that are either out of bounds or nan in the texture to nan
    # in the output.
    # Numpy wants to warn about the fact that there are nan values in the
    # textures, so we silence warnings about this.
    with np.errstate(invalid='ignore'):
        surface_z[(texture_x < 0) | (texture_x >= 1) |
                  (texture_y < 0) | (texture_y >= 1)] = np.nan
    
    return surface_z


def texture_plot(texture, surface, angle=45, **kwargs):
    # Extract the Xs and Ys from the texture
    surface_x, surface_y = texture
    
    # Map the texture to get the Zs
    surface_z = texture_map(texture, surface.T)
    
    # The projection is as simple as linearly blending the Z and Y
    # dimensions. The multiples are calculated from the given
    # angle with standard trig.
    z_coef = np.sin(np.radians(angle))
    y_coef = np.cos(np.radians(angle))
    plot = (surface_x, -surface_y * y_coef + surface_z * z_coef)

    return plot


# Image operations
# 
def remove_image(surface, image):
    surface = np.copy(surface)
    surface[np.invert(image)] = np.nan
    return surface


def remove_threshold(surface, threshold):
    mask = np.copy(surface)
    # mask[..., 0] = np.minimum(mask[..., 0], threshold)
    # mask = np.clip(mask, threshold, 1.0)
    return remove_image(surface, mask > threshold)


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


def remove_hidden_parts(surface, angle):
    return remove_image(surface, make_visible_mask(surface, angle))
    # surface = np.copy(surface)
    # surface[~make_visible_mask(surface, angle)] = np.nan
    # return surface


def do_normalise(array):
    array = np.float32(array)
    return array/255

    # info = np.iinfo(array.dtype)
    # return im.astype(np.float64) / info.max
    # return -np.log(1/((1 + array)/257) - 1)

def img2array(filename):
    img = Image.open( filename ).convert('L')
    array = np.array(img, np.uint8)
    return do_normalise(array)

# SVG convertion
# 
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

def shadeImg( svg_surface, filename, texture_angle=0, camera_angle=1.0, texture_resolution=None, presicion=1.0, threshold=None, mask=None, texture=None):

    img = img2array( filename )
    img = remove_hidden_parts(img, camera_angle)
    if threshold != None:
        img = remove_threshold(img, threshold)

    if isinstance(mask, basestring) or isinstance(mask, str):
        mask_img = img2array(mask)
        img = remove_image(img, mask_img > 0.5 )
    elif isinstance(mask, (np.ndarray, np.generic) ):
        img = remove_image(img, mask)

    height, width = img.shape[:2]

    if texture_resolution == None:
        texture_resolution = min(width, height) * 0.5

    if texture == None:
        texture = make_joy_texture(texture_resolution, min(width, height) * presicion)
        # texture = make_grid_texture(100, 100, 200)

    if texture_angle != 0:
        texture = rotate_texture(texture, texture_angle)

    # texture = fit_texture(texture)

    plot = texture_plot(texture, img, camera_angle)
    flipped_plot = [(x * svg_surface.width, -y * svg_surface.height) for x, y in [plot]]

    root = svg_surface.body.add( svgwrite.container.Group(id=filename, fill='none', stroke='black', stroke_width=STROKE_WIDTH ) )
    for layer in flipped_plot:
        root.add( svgwrite.path.Path(d=layer_to_path(layer)) )