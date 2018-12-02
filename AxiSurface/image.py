
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np
from PIL import Image
from numba import prange, jit


def normalise(im):
    """Normalize an image matrix from 0 - 255 to 0.0 - 1.0f range at 64bit  
    """
    return np.clip(np.float64(im) / 255, 0, None)


def compute_normals(elevation):
    """Generate a 3-channel normal map from a height map.
    The normal components are in the range [-1,+1] and the size of the
    normal map is (width-1, height-1) due to forward differencing.
    """
    height, width = elevation.shape
    normals = np.empty([height, width, 3])
    _compute_normals(elevation, normals)
    return normals


@jit(nopython=True, fastmath=True, cache=True)
def _compute_normals(el, normals):
    h, w = normals.shape[:2]
    for row in range(h):
        for col in range(w):
            p =  np.float64((col / w, row / h, el[row][col]))
            dx = np.float64(((col+1) / w, row / h, el[row][col+1]))
            dy = np.float64((col / w, (row+1) / h, el[row+1][col]))
            v1 = dx - p
            v2 = dy - p
            n = np.float64((
                    (v1[1] * v2[2]) - (v1[2] * v2[1]),
                    (v1[2] * v2[0]) - (v1[0] * v2[2]),
                    (v1[0] * v2[1]) - (v1[1] * v2[0])))
            isq = 1 / np.linalg.norm(n)
            normals[row][col] = n * isq


def extract_rgb(image):
    """Extract the RGB planes from an RGBA image.
    
    Note that this returns a copy. If you wish to obtain a view that
    allows mutating pixels, simply use slicing instead. For
    example, to invert the colors of an image while leaving alpha
    intact, you can do:
    <code>myimage[:,:,:3] = 1.0 - myimage[:,:,:3]</code>.
    """
    assert len(image.shape) == 3 and image.shape[2] >= 3
    planes = np.dsplit(image, image.shape[2])
    return np.dstack(planes[:3])


def reshape(image):
    """Add a trailing dimension to single-channel 2D images.
    See also <a href="#unshape">unshape</a>.
    """
    if len(image.shape) == 2:
        image = np.reshape(image, image.shape + (1,))
    return image


def load_image_rgb(filename):
    """Load a Image in a RGB 64bit floating point matrix
    """
    img = Image.open( filename ).convert('RGB')
    array = np.array(img, np.uint8)
    array = extract_rgb(array)
    array = normalise(array)
    return array


def load_grayscale(filename):
    """Load a Image in a GRAYSCALE 64bit floating point matrix
    """
    img = Image.open( filename ).convert('L')
    array = np.array(img, np.uint8)
    array = normalise(array)
    return array 


def load_normalmap(filename):
    return load_image_rgb(filename) * 2.0 - 1.0


def remove_mask(surface, image):
    surface = np.copy(surface)
    surface[np.invert(image)] = np.nan
    return surface


def remove_threshold(surface, threshold):
    mask = np.copy(surface)
    return remove_mask(surface, mask > threshold)