# Copyright (c) 2018 Avanade
# Author: Thor Schueler
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# pylint: disable=C0103
"""
    Kinematics and reverse kinematics to determine cartesians from angles and vice versa
"""
import math


class Point(object):
    """Represents a point in space"""
    
    def __init(self):
        """Initializes the object"""
        self.x = 0
        self.y = 0
        self.z = 0
        self.r = 0
        self.lng = 0
        self.lat = 0

    @classmethod
    def fromCartesian(cls, x: float, y: float, z: float):
        """
            Generates a point based on cartesian coordinates
            Arguments:
                x   -   x - coordinate
                y   -   y - coordinate
                z   -   z - coordinate
        """
        p = cls()
        p.x = x
        p.y = y
        p.z = z
        p.r = math.sqrt(x*x + y*y + z*z)
        p.lat = math.acos(z / p.r)
        p.lng = math.acos(x / math.sqrt(x*x*1.0 +y*y*1.0))
        if y < 0: p.lng = -p.lng
        return p

    @classmethod
    def fromPolar(cls, r: float, lng: float, lat: float):
        """
            Generates a point based on polar coordinates
            Arguments:
                r   -   radius (magnitude)
                lng -   longitude (inclination)
                lat -   latitude (declination)
        """
        p = cls()
        p.r = r
        p.lng = lng
        p.lat = lat
        p.x = r * math.sin(lat) * math.cos(lng)
        p.y = r * math.sin(lat) * math.sin(lng)
        p.z = r * math.cos(lat)
        return p

    def distance(self, p) -> float:
        """ Returns the distance between this and another point"""
        dx = self.x - p.x
        dy = self.y - p.y
        dz = self.z - p.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)

    def toDict(self) -> {}:
        """Returns the object as a dictionary object"""
        r = {}
        r["lat"] = self.lat
        r["lng"] = self.lng
        r["r"] = self.r
        r["x"] = self.x
        r["y"] = self.y
        r["z"] = self.z
        return r

class Kinematics(object):
    """Determine cartesians from angles and vice versa."""

    def __init__(self, useRadians:bool = False, shoulderToElbow:float = 80.0, elbowToWrist:float = 80.0, wristToHand:float = 60.0):
        """
        Initializes the object for the desired geometry
            
        :param useRadians:      True to express angles in radians, false otherwise
        :type useRadias:        bool
        :param shoulderToElbow: Length from the shoulder joint to the elbow joint in mm
        :type sholderToElbow:   float
        :param elbowToWrist:    Lenght from eblow joint to wrist in mm
        :type elbowToWrist:     float 
        :param wristToHand:     Lenght from wrist to gripper in mm
        :type wristToHand:      float
        """
        self._useRadians = useRadians
        self._shoulderToElbow = shoulderToElbow
        self._elbowToWrist = elbowToWrist
        self._wristToHand = wristToHand

    def calculateAngle(self, leg1: float, leg2: float,  opp: float) -> float:
        """
        Calculates the angle between two legs based on trigonometry:
        c^2 = a^2 + b^2 - 2ab * cos(alpha) => alpha = acos((a^2 + b^2 - c^2)/2ab)
            
        :param leg1:    Length of leg one
        :type leg1:     float
        :param leg2:    Length of leg two
        :type leg2:     float
        :param opp:     Length of opposing side
        :type opp:      float
        :return:        The angle between the legs
        :rtype:         float
        """
        if leg1 == 0 or leg2 == 0: return 0
        c = ((leg1*leg1 + leg2*leg2 - opp*opp) * 1.0)/(2.0 * leg1 * leg2) 
        if c > 1 or c < -1:
            raise Exception("Arguments %f, %f and %f do not appear to constitute a valid triangle..." % (leg1, leg2, opp))
        alpha = math.acos(c)
        if self._useRadians == False:
            alpha = math.degrees(alpha)
        return alpha

    def cart2polar(self, x: float, y: float) -> (float, float):
        """
        Convert cartesian to polar coordinates
            
        :param x:   x coordinate in mm
        :type x:    float
        :param y:   y coordinate in mm
        :type y:    float
        :return:    Polar coordinates
        :rtype:     (float, float)        
        """
        r = math.hypot(x *1.0, y * 1.0)        # get the radius
        if(r == 0): return 0.0, 0.0
        
        c = x / r                              # r = x * cos(alpha)
        s = y / r                              # r = y * sin(alpha)
        alpha = math.acos(c)                   # angle between 0 and pi
        if s < 0: alpha = -alpha
        if self._useRadians == False:
            alpha = math.degrees(alpha) 
        return r, alpha

    def distance(self, p1: Point, p2: Point) -> float:
        """ 
        Returns the distance between two points in space 
        
        :param p1:  The firt point
        :type p1:   Point
        :param p2:  The second point
        :type p2:   Point
        :return:    The distance between p1 and p2
        :rtype:     float
        """
        return p2.distance(p1)

    def polar2cart(self, r:float, alpha:float) -> (float, float):
        """
        Converts polar coordinates to cartesians
        
        :param r:       Radius in mm (magnitude)
        :type r:        float
        :param alpha:   Angle in degrees or radians (depending on construction)(bearing)
        :type alpha:    float
        :return:        Cartesian coordinates
        :rtype:         (float, float)
        """
        alphaPrime = alpha
        if self._useRadians == False:
            alphaPrime = math.radians(alpha)
        x = r * math.cos(alphaPrime)
        y = r * math.sin(alphaPrime)
        return x, y

    def toCartesian(self, a0: float, a1: float, a2: float) -> (float, float, float):
        """
        Calculates the cartesian coordinates of the arm (claw point) based on the given servo angles
        
        :param a0:      Hip angle
        :type a0:       float
        :param a1:      Shoulder angle
        :type a1:       float
        :param a2:      Elbow angle
        :type a2:       float
        :return:        Cartesian coordinates of the arm based on the servo angles
        :rtype:         (float, float, float) 
        """

        # Calculate u,v coordinates for arm
        u01, v01 = self.polar2cart(self._shoulderToElbow, a1)
        u12, v12 = self.polar2cart(self._elbowToWrist, a2)
        
        # Add vectors
        u = u01 + u12 + self._wristToHand
        v = v01 + v12
        
        # Calculate in 3D space - note x/y reversal!
        y, x = self.polar2cart(u, a0)
        z = v
        return x, y, z

    def fromCartesian(self, x: float, y: float, z: float) -> (float, float, float):
        """
        Calculates the servo actuation angles requires to position the claw at a certain cartesian coordinate
        
        :param x:   x - coordiante to be achieved
        :type x:    float
        :param y:   y - coordinate to be achieved
        :type y:    float
        :param z:   z - coordinate to be achieved
        :type z:    float
        :return:    Servo actuation angles to achieve desired coordinates
        :rtype:     (float, float, float)
        """
        _pi = math.pi
        if self._useRadians == False:
                _pi = 180

        # Solve top-down view, hip servo
        r, a0 = self.cart2polar(y, x)

        # In arm plane, convert to polar
        r -= self._wristToHand               # Account for the wrist length
        r1, theta = self.cart2polar(r, z)
        
        # Solve arm inner angles as required
        b = self.calculateAngle(self._elbowToWrist, self._shoulderToElbow, r1)
        c = self.calculateAngle(r1, self._shoulderToElbow, self._elbowToWrist)
        
        # Solve for servo angles from horizontal
        a1 = theta + b
        a2 = c + a1 - _pi
        
        return a0, a1, a2   
