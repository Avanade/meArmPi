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
    def fromCartesian(cls, x: float, y: float, z: float) -> cls:
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
        p.r = p.distance(Point())
        p.lat = math.acos(z / p.r)
        p.lng = math.acos(x / math.sqrt(x*x*1.0 +y*y*1.0))
        if y < 0: p.lng = -p.lng
        return p

    @classmethod
    def fromPolar(cls, r: float, lng: float, lat: float) -> cls:
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

    def distance(self, p: Point) -> float:
        """ Returns the distance between this and another point"""
        dx = self.x - p.x
        dy = self.y - p.y
        dz = self.z - p.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)

class Kinematics(object):
    """Determine cartesians from angles and vice versa."""

    def __init__(self, shoulderToElbow=80, elbowToWrist=80, wristToHand=60):
        """
            Initializes the object for the desired geometry
            Arguments:
                shoulderToElbow:    length from the shoulder joint to the elbow joint in mm
                elbowToWrist:       lenght from eblow joint to wrist in mm
                wristToHand:        lenght from wrist to gripper in mm
        """
        self.shoulderToElbow = shoulderToElbow
        self.elbowToWrist = elbowToWrist
        self.wristToHand = wristToHand

    def calculateAngle(self, leg1: float, leg2: float,  opp: float) -> float:
        """
            Calculates the angle between two legs based on trigonometry:
            c^2 = a^2 + b^2 - 2ab * cos(alpha) => alpha = acos((c^2 - a^2 - b^2)/2ab)
            Arguments:
                leg1:   length of leg one
                leg2:   length of leg two
                opp:    length of opposing side
        """
        if leg1 == 0 or leg2 == 0: return 0
        c = ((opp*opp + leg1*leg1 - leg2*leg2) * 1.0)/(2 * leg1 * leg2 * 1.0) 
        if c > 1 or c < -1:
            raise Exception("Arguments %f, %f and %f do not appear to constitute a valid triangle..." % (leg1, leg2, opp))
        alpha = math.acos(c)
        return alpha

    def cart2polar(self, x: float, y: float) -> (float, float):
        """
            Convert cartesian to polar coordinates
            Arguments:
                x:  x coordinate in mm
                y:  y coordinate in mm        
        """
        r = math.hypot(x *1.0, y * 1.0)        # get the radius
        if(r == 0): return 0.0, 0.0
        
        c = x / r                              # r = x * cos(alpha)
        s = y / r                              # r = y * sin(alpha)
        alpha = math.acos(c)                   # angle between 0 and pi
        if s < 0: alpha = -alpha
        return r, alpha

    def distance(self, p1: Point, p2: Point) -> float:
        """ Returns the distance between two points in space """
        return p2.distance(p1)

    def polar2cart(self, r:float, alpha:float) -> (float, float):
        """
            Converts polar coordinates to cartesians
            Arguments:
                r:      Radius in mm (magnitude)
                alpha:  Angle in degrees (bearing)

        """
        x = r * math.cos(alpha)
        y = r * math.sin(alpha)
        return x, y

    def toCartesian(self, a0: float, a1: float, a2: float) -> (float, float, float):
        """
            Calculates the cartesian coordinates of the arm (claw point) based on the given servo angles
            Argumants:
                a0:     Hip angle
                a1:     Shoulder angle
                a2:     Elbow angle 
        """
        # Calculate u,v coordinates for arm
        u01, v01 = self.polar2cart(self.shoulderToElbow, a1)
        u12, v12 = self.polar2cart(self.elbowToWrist, a2)
        
        # Add vectors
        u = u01 + u12 + self.wristToHand
        v = v01 + v12
        
        # Calculate in 3D space - note x/y reversal!
        y, x = self.polar2cart(u, a0)
        z = v
        return x, y, z

    def fromCartesian(self, x: float, y: float, z: float) -> (float, float, float):
        """
            Calculates the servo actuation angles requires to position the claw at a certain cartesian coordinate
            Argumants:
                x:     x - coordiante to be achieved
                y:     y - coordinate to be achieved
                z:     z - coordinate to be achieved
        """
        # Solve top-down view, hip servo
        r, a0 = self.cart2polar(y, x)

        # In arm plane, convert to polar
        r -= self.wristToHand               # Account for the wrist length
        r1, theta = self.cart2polar(r, z)
        
        # Solve arm inner angles as required
        b = self.calculateAngle(self.elbowToWrist, self.shoulderToElbow, r1)
        c = self.calculateAngle(r1, self.shoulderToElbow, self.elbowToWrist)
        
        # Solve for servo angles from horizontal
        a1 = theta + b
        a2 = c + a1 - math.pi
        
        return a0, a1, a2   
