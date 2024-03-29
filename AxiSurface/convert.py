#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict
from .textures_generators import *

from .Path import Path
from .Polygon import Polygon
from .Image import Image
from .Texture import *
from .tools import transform

def ImageContourToPath(filename, threshold=0.5, scale=1.0):
    try:
        import cv2 as cv
    except ImportError:
        cv = None

    if cv is None:
        raise Exception('AxiSurface.fromThreshold() requires OpenCV')

    path = []    

    if isinstance(filename, Image):
        filename = filename.filename
    im = cv.imread( filename )
    blur = cv.GaussianBlur(im, (3, 3),0)
    imgray = cv.cvtColor( blur, cv.COLOR_BGR2GRAY )
    ret, thresh = cv.threshold(imgray, int(threshold * 255), 255, cv.THRESH_BINARY)
    image, contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # height, width = im.shape[:2]
    # scale = [ (1.0 / width) * size[0], (1.0 / height) * size[1] ]

    for contour in contours:
        points = []
        for point in contour:
            # points.append( (point[0][0] * scale[0], point[0][1] * scale[1]) )
            points.append( (point[0][0] * scale, point[0][1] * scale) )
        
        # if len(points) > 2:
        #     points.append( points[0] )
            
        path.append( points )

    return Path( path )


def ImageThresholdToPolygons(filename, threshold=0.5, min_area=10.0, scale=1.0, rotate=0, translate=[0.0, 0.0]):
    try:
        import cv2 as cv
    except ImportError:
        cv = None

    if cv is None:
        raise Exception('AxiSurface.fromThreshold() requires OpenCV')

    polygons = []    

    if isinstance(filename, Image):
        filename = filename.filename
    im = cv.imread( filename )
    blur = cv.GaussianBlur(im, (3, 3),0)
    imgray = cv.cvtColor( blur, cv.COLOR_BGR2GRAY )
    ret, thresh = cv.threshold(imgray, int(threshold * 255), 255, cv.THRESH_BINARY)
    image, contours, hierarchy = cv.findContours(thresh, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)

    if not contours:
        return polygons

    # now messy stuff to associate parent and child contours
    cnt_children = defaultdict(list)
    child_contours = set()
    assert hierarchy.shape[0] == 1
    # http://docs.opencv.org/3.1.0/d9/d8b/tutorial_py_contours_hierarchy.html
    for idx, (_, _, _, parent_idx) in enumerate(hierarchy[0]):
        if parent_idx != -1:
            child_contours.add(idx)
            cnt_children[parent_idx].append(contours[idx])
    # create actual polygons filtering by area (removes artifacts)

    def trans(points):
        result = []
        for point in points:
            result.append( transform([point[0], point[1]], translate=translate, scale=scale, rotate=rotate ))
        return result

    for idx, cnt in enumerate(contours):
        if idx not in child_contours and cv.contourArea(cnt) >= min_area:
            assert cnt.shape[1] == 1
            poly = Polygon( trans(cnt[:, 0, :]) )

            for c in cnt_children.get(idx, []):
                if cv.contourArea(c) >= min_area:
                    poly.addHole( trans(c[:, 0, :]) )
            polygons.append(poly)

    return polygons


def GrayscaleToTexture(filename, **kwargs):
    grayscale = Image( filename )

    threshold = float(kwargs.pop('threshold', 0.5))
    invert = kwargs.pop('invert', False)
    texture = kwargs.pop('texture', None)
    texture_angle = float(kwargs.pop('texture_angle', 0.0))
    mask = kwargs.pop('mask', None)

    # Make surface to carve from (copy from gradient to get same dinesions)
    surface = grayscale.copy()
    surface.fill(1.0)

    # Make gradient into dither mask
    grayscale.dither(threshold=threshold, invert=invert)
    surface = surface - grayscale

    # Load and remove Mask
    if isinstance(mask, str) or isinstance(mask, str):
        mask = Image(mask)
        mask = mask.threshold()
    surface = surface - mask

    # Create texture
    if texture is None:
        texture_resolution = kwargs.pop('texture_resolution', min(grayscale.width, grayscale.height) * 0.5)
        texture_presicion = float(kwargs.pop('texture_presicion', 1.0))
        texture_offset = float(kwargs.pop('texture_offset', 0.0)) 
        texture = Texture( stripes_texture(texture_resolution, min(grayscale.width, grayscale.height) * texture_presicion, texture_offset), **kwargs)
    elif not isinstance(texture, Texture):
        texture = Texture( texture, **kwargs  )

    if texture_angle > 0:
        texture.turn(texture_angle)

    # Project texture on surface 
    texture.project(surface)

    return texture


def HeightmapToTexture(filename, **kwargs):
    grayscale = kwargs.pop('grayscale', None)
    camera_angle = float(kwargs.pop('camera_angle', 10.0))

    threshold = float(kwargs.pop('threshold', 0.5))
    invert = kwargs.pop('invert', False)
    texture = kwargs.pop('texture', None)
    texture_angle = float(kwargs.pop('texture_angle', 0.0))
    mask = kwargs.pop('mask', None)

    # Load heightmap
    heightmap = Image(filename)
    heightmap.occlude(camera_angle)

    # load and remove mask
    if isinstance(mask, str) or isinstance(mask, str):
        mask = Image(mask)
        mask = mask.threshold()
    heightmap = heightmap - mask

    # Load gradient into dither mask
    if grayscale != None:
        gradientmap = Image( grayscale )
        heightmap = heightmap - gradientmap.dither(threshold=threshold, invert=invert)

    # Create texture
    if texture is None:
        texture_resolution = kwargs.pop('texture_resolution', min(heightmap.width, heightmap.height) * 0.5)
        texture_presicion = float(kwargs.pop('texture_presicion', 1.0))
        texture_offset = float(kwargs.pop('texture_offset', 0.0)) 
        texture = Texture( stripes_texture(num_lines=texture_resolution, resolution=min(heightmap.width, heightmap.height) * texture_presicion, offset=texture_offset), **kwargs )
    elif not isinstance(texture, Texture):
        texture = Texture( texture, **kwargs )

    if texture_angle > 0:
        texture.turn(texture_angle)

    texture.project(heightmap, camera_angle)

    return texture
