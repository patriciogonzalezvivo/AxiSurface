#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import svgwrite

import numpy as np

# This code is adapted from Paul Butler great Surface Projection tutorial
# https://bitaesthetics.com/posts/surface-projection.html and PenKit https://github.com/paulgb/penkit/


# TEXTURES CONSTRUCTORS
# ------------------------------------------------------------------

def make_stripes_texture(num_lines=10, resolution=50, offset=0):
    x_min = 0.0
    x_max = 1.0
    y_min = 0.0
    y_max = 1.0
    
    resolution_unit = 1.0 / resolution
    resolution_offset = offset * resolution_unit
    x_min = x_min + resolution_offset
    x_max = (x_max-resolution_unit) + resolution_offset

    lines_unit = 1.0 / num_lines
    lines_offset = offset * lines_unit
    y_min = y_min + lines_offset
    y_max = (y_max-lines_unit) + lines_offset

    # np.meshgrid is a handy way to generate a grid of points. It
    # returns a pair of matrices, which we will flatten into arrays.
    # For the x-coordinates, we put a nan value at the end so that when
    # we flatten them there is a separater between each horizontal line.
    x, y = np.meshgrid(
        np.hstack( [np.linspace(x_min, x_max, resolution), np.nan] ),
        np.linspace(y_min, y_max, num_lines),
    )
    
    # For coordinates where the x value is nan, set the y value to nan
    # as well. nan coordinates represent breaks in the path, indicating
    # here that the pen should be raised between each horizontal line.
    y[np.isnan(x)] = np.nan
    return x.flatten(), y.flatten()

    
def make_grid_texture(num_h_lines=10, num_v_lines=10, resolution=50):
    x_h, y_h = make_stripes_texture(num_h_lines, resolution)
    y_v, x_v = make_stripes_texture(num_v_lines, resolution)
    return np.concatenate([x_h, x_v]), np.concatenate([y_h, y_v])


#  TEXTURE OPERATIONS
# ------------------------------------------------------------------

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
