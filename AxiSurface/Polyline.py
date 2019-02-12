#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
import numpy as np

from .AxiElement import AxiElement
from .tools import pointInside, linesIntersection, lerp, distance, remap

class Polyline(AxiElement):
    def __init__( self, points=None, **kwargs):
        AxiElement.__init__(self, **kwargs);

        # TODO:
        #   Polyline < > Polygon
        #   Resolve width
        #   resolve fill

        if isinstance(points, Polyline):
            points = points.points

        if points == None:
            points = []

        self.points = points
        self.lengths = []
        self.isClosed = kwargs.pop('isClosed', False) 
        self._updateCache()

    def __setitem__(self, index, value):
        if type(index) is int:
            self.points[index] = value


    def __getitem__(self, index):
        if type(index) is int:
            return self.points[ index ]
        else:
            return None

    def _updateCache(self):
        # Clean
        self.lengths = []
        N = len(self.points)

        # Check
        if N == 0:
            return 

        # Process
        length = 0
        for i in range( N - 1 ):
            self.lengths.append(length)
            p1 = self.points[i]
            p2 = self.points[i+1]
            length += distance(p1, p2)

        if self.isClosed:
            self.lengths.append(length);


    def lineTo( self, pos ):
        self.points.append( pos )
        self._updateCache()


    def bezierTo(self, pos, cpos1, curveResolution = 20):
    # 	# if, and only if poly vertices has points, we can make a bezier
    # 	# from the last point
    # 	curveVertices.clear();
        
    # the resolultion with which we computer this bezier
    # is arbitrary, can we possibly make it dynamic?
        
        if self.size() > 0:
    		x0 = points[-1][0]
    		y0 = points[-1][1]
            
    # 		  ax, bx, cx;
    # 		  ay, by, cy;
    # 		  az, bz, cz;
    # 		  t, t2, t3;
    # 		  x, y, z;
            
    # 		// polynomial coefficients
    # 		cx = 3.0f * (cp1.x - x0);
    # 		bx = 3.0f * (cp2.x - cp1.x) - cx;
    # 		ax = to.x - x0 - cx - bx;
            
    # 		cy = 3.0f * (cp1.y - y0);
    # 		by = 3.0f * (cp2.y - cp1.y) - cy;
    # 		ay = to.y - y0 - cy - by;
            
    # 		cz = 3.0f * (cp1.z - z0);
    # 		bz = 3.0f * (cp2.z - cp1.z) - cz;
    # 		az = to.z - z0 - cz - bz;
            
    # 		for (int i = 1; i <= curveResolution; i++){
    # 			t 	=  (float)i / (float)(curveResolution);
    # 			t2 = t * t;
    # 			t3 = t2 * t;
    # 			x = (ax * t3) + (bx * t2) + (cx * t) + x0;
    # 			y = (ay * t3) + (by * t2) + (cy * t) + y0;
    # 			z = (az * t3) + (bz * t2) + (cz * t) + z0;
    # 			points.emplace_back(x,y,z);
    # 		}
    # 	}
    #     flagHasChanged();
    # }

    # //----------------------------------------------------------
    # template<class T>
    # void ofPolyline_<T>::quadBezierTo(float x1, float y1, float z1, float x2, float y2, float z2, float x3, float y3, float z3, int curveResolution){
    # 	curveVertices.clear();
    # 	for(int i=0; i <= curveResolution; i++){
    # 		double t = (double)i / (double)(curveResolution);
    # 		double a = (1.0 - t)*(1.0 - t);
    # 		double b = 2.0 * t * (1.0 - t);
    # 		double c = t*t;
    # 		double x = a * x1 + b * x2 + c * x3;
    # 		double y = a * y1 + b * y2 + c * y3;
    # 		double z = a * z1 + b * z2 + c * z3;
    # 		points.emplace_back(x, y, z);
    # 	}
    #     flagHasChanged();
    # }

    # //----------------------------------------------------------
    # template<class T>
    # void ofPolyline_<T>::curveTo( const T & to, int curveResolution ){
        
    # 	curveVertices.push_back(to);
        
    # 	if (curveVertices.size() == 4){
            
    # 		float x0 = curveVertices[0].x;
    # 		float y0 = curveVertices[0].y;
    # 		float z0 = curveVertices[0].z;
    # 		float x1 = curveVertices[1].x;
    # 		float y1 = curveVertices[1].y;
    # 		float z1 = curveVertices[1].z;
    # 		float x2 = curveVertices[2].x;
    # 		float y2 = curveVertices[2].y;
    # 		float z2 = curveVertices[2].z;
    # 		float x3 = curveVertices[3].x;
    # 		float y3 = curveVertices[3].y;
    # 		float z3 = curveVertices[3].z;
            
    # 		float t,t2,t3;
    # 		float x,y,z;
            
    # 		for (int i = 1; i <= curveResolution; i++){
                
    # 			t 	=  (float)i / (float)(curveResolution);
    # 			t2 	= t * t;
    # 			t3 	= t2 * t;
                
    # 			x = 0.5f * ( ( 2.0f * x1 ) +
    #                         ( -x0 + x2 ) * t +
    #                         ( 2.0f * x0 - 5.0f * x1 + 4 * x2 - x3 ) * t2 +
    #                         ( -x0 + 3.0f * x1 - 3.0f * x2 + x3 ) * t3 );
                
    # 			y = 0.5f * ( ( 2.0f * y1 ) +
    #                         ( -y0 + y2 ) * t +
    #                         ( 2.0f * y0 - 5.0f * y1 + 4 * y2 - y3 ) * t2 +
    #                         ( -y0 + 3.0f * y1 - 3.0f * y2 + y3 ) * t3 );
                
    # 			z = 0.5f * ( ( 2.0f * z1 ) +
    #                         ( -z0 + z2 ) * t +
    #                         ( 2.0f * z0 - 5.0f * z1 + 4 * z2 - z3 ) * t2 +
    #                         ( -z0 + 3.0f * z1 - 3.0f * z2 + z3 ) * t3 );
                
    # 			points.emplace_back(x,y,z);
    # 		}
    # 		curveVertices.pop_front();
    # 	}
    #     flagHasChanged();
    # }

    # //----------------------------------------------------------
    # template<class T>
    # void ofPolyline_<T>::arc(const T & center, float radiusX, float radiusY, float angleBegin, float angleEnd, bool clockwise, int circleResolution){
        
    #     if(circleResolution<=1) circleResolution=2;
    #     setCircleResolution(circleResolution);
    #     points.reserve(points.size()+circleResolution);

    #     const float epsilon = 0.0001f;
        
    #     const size_t nCirclePoints = circlePoints.size();
    #     float segmentArcSize  = M_TWO_PI / (float)nCirclePoints;
        
    #     // convert angles to radians and wrap them into the range 0-M_TWO_PI and
    #     float angleBeginRad = wrapAngle(ofDegToRad(angleBegin));
    #     float angleEndRad =   wrapAngle(ofDegToRad(angleEnd));
        
    #     while(angleBeginRad >= angleEndRad) angleEndRad += M_TWO_PI;
        
    #     // determine the directional angle delta
    #     float d = clockwise ? angleEndRad - angleBeginRad : angleBeginRad - angleEndRad;
    #     // find the shortest angle delta, clockwise delta direction yeilds POSITIVE values
    #     float deltaAngle = atan2(sin(d),cos(d));
        
    #     // establish the remaining angle that we have to work through
    #     float remainingAngle = deltaAngle;
        
    #     // if the delta angle is in the CCW direction OR the start and stop angles are
    #     // effectively the same adjust the remaining angle to be a be a full rotation
    #     if(deltaAngle < 0 || std::abs(deltaAngle) < epsilon) remainingAngle += M_TWO_PI;
        
    # 	T radii(radiusX, radiusY, 0.f);
    # 	T point;
        
    #     int currentLUTIndex = 0;
    #     bool isFirstPoint = true; // special case for the first point
        
    #     while(remainingAngle > 0) {
    #         if(isFirstPoint) {
    #             // TODO: should this be the exact point on the circle or
    #             // should it be an intersecting point on the line that connects two
    #             // surrounding LUT points?
    #             //
    #             // get the EXACT first point requested (for points that
    #             // don't fall precisely on a LUT entry)
    # 			point = T(cos(angleBeginRad), sin(angleBeginRad), 0.f);
    #             // set up the get any in between points from the LUT
    #             float ratio = angleBeginRad / M_TWO_PI * (float)nCirclePoints;
    #             currentLUTIndex = clockwise ? (int)ceil(ratio) : (int)floor(ratio);
    #             float lutAngleAtIndex = currentLUTIndex * segmentArcSize;
    #             // the angle between the beginning angle and the next angle in the LUT table
    #             float d = clockwise ? (lutAngleAtIndex - angleBeginRad) : (angleBeginRad - lutAngleAtIndex);
    #             float firstPointDelta = atan2(sin(d),cos(d)); // negative is in the clockwise direction
                
    #             // if the are "equal", get the next one CCW
    #             if(std::abs(firstPointDelta) < epsilon) {
    #                 currentLUTIndex = clockwise ? (currentLUTIndex + 1) : (currentLUTIndex - 1);
    #                 firstPointDelta = segmentArcSize; // we start at the next lut point
    #             }
                
    #             // start counting from the offset
    #             remainingAngle -= firstPointDelta;
    #             isFirstPoint = false;
    #         } else {
    # 			point = T(circlePoints[currentLUTIndex].x, circlePoints[currentLUTIndex].y, 0.f);
    #             if(clockwise) {
    #                 currentLUTIndex++; // go to the next LUT point
    #                 remainingAngle -= segmentArcSize; // account for next point
    #                 // if the angle overshoots, then the while loop will fail next time
    #             } else {
    #                 currentLUTIndex--; // go to the next LUT point
    #                 remainingAngle -= segmentArcSize; // account for next point
    #                 // if the angle overshoots, then the while loop will fail next time
    #             }
    #         }
            
    #         // keep the current lut index in range
    #         if(clockwise) {
    #             currentLUTIndex = currentLUTIndex % nCirclePoints;
    #         } else {
    #             if(currentLUTIndex < 0) currentLUTIndex = nCirclePoints + currentLUTIndex;
    #         }
            
    #         // add the point to the poly line
    #         point = point * radii + center;
    #         points.push_back(point);
            
    #         // if the next LUT point moves us past the end angle then
    #         // add a a point a the exact end angle and call it finished
    #         if(remainingAngle < epsilon) {
    # 			point = T(cos(angleEndRad), sin(angleEndRad), 0.f);
    #             point = point * radii + center;
    #             points.push_back(point);
    #             remainingAngle = 0; // call it finished, the next while loop test will fail
    #         }
    #     }
    #     flagHasChanged();
    # }

    def setClose(self, close):
        self.isClosed = close
        self._updateCache()


    def size(self):
        return len(self.points)


    def inside( self, pos ):
        return pointInside( pos, self.points )


    def getPerimeter(self):
        if len(self.lengths) < 1:
            return 0
        return self.lengths[-1]


    def getPointAtLength(self, length):
        return self.getPointAtIndexInterpolated( self.getIndexAtLength( length ) )


    def getIndexAtLength(self, length):
        totalLength = self.getPerimeter()
        length = max(min(length, totalLength), 0)
    
        lastPointIndex =  (len(self.points) - 1, len(self.points))[self.isClosed]

        i1 = max(min(int(math.floor(length / totalLength * lastPointIndex)), len(self.lengths)-2), 0) # start approximation here
        leftLimit = 0
        rightLimit = lastPointIndex
        
        distAt1 = 0.0
        distAt2 = 0.0
        for iterations in range(32):
            i1 = max(min(int(i1), len(self.lengths)-1), 0)
            distAt1 = self.lengths[i1]

            if distAt1 <= length:         # if Length at i1 is less than desired Length (this is good)
                distAt2 = self.lengths[i1+1]
                if distAt2 >= length:
                    t = remap(length, distAt1, distAt2, 0.0, 1.0)
                    return i1 + t
                else:
                    leftLimit = i1
            else:
                rightLimit = i1
            i1 = (leftLimit + rightLimit) / 2

        return 0


    def getPointAtIndexInterpolated(self, findex):
        i1, i2, t = self.getInterpolationParams(findex)
        return lerp(self.points[i1], self.points[i2], t)


    def getInterpolationParams(self, findex):
        i1 = math.floor(findex)
        t = findex - i1
        i1 = self.getWrappedIndex(i1)
        i2 = self.getWrappedIndex(i1 + 1)
        return i1, i2, t


    def getWrappedIndex(self, index):
        if len(self.points) == 0:
            return 0
    
        if index < 0: 
            return  (0, int(index + len(self.points)) % int(len(self.points) - 1) )[self.isClosed]

        if index > len(self.points)-1:
            return  (len(self.points) - 1, int(index) % len(self.points))[self.isClosed]

        return int(index)


    def getResampledBySpacing(self, spacing):
        if spacing==0 or (self.points) == 0:
            return self

        poly = Polyline()
        totalLength = self.getPerimeter()
        f = 0.0
        while f < totalLength:
            poly.lineTo( self.getPointAtLength(f) )
            f += spacing

        if not self.isClosed:
            if poly.size() > 0:
                poly.points[-1] = self.points[-1];
                self.isClosed = False
            else:
                self.isClosed = True
        
        return poly


    def getResampledByCount(self, count):
        if count < 2:
            return None

        perimeter = self.getPerimeter()
        return self.getResampledBySpacing( perimeter / (count-1) )


    def getTexture(self, width, height, resolution=1000):
        x = np.zeros(resolution+1)
        y = np.zeros(resolution+1)
        x.fill(np.nan)
        y.fill(np.nan)

        poly = self.getResampledByCount(resolution)

        for i in range(poly.size()):
            p = poly[i]

            x[i] = p[0] / float(width)
            y[i] = p[1] / float(height)

        x[resolution] = np.nan
        y[resolution] = np.nan

        from .Texture import Texture
        return Texture( (x.flatten('F'), y.flatten('F')) )


    def getPathString(self):
        points = self.points[:]
        if self.isClosed:
            points.append(self.points[0])

        d = 'M' + 'L'.join('{0} {1}'.format(x,y) for x,y in points)

        return d



