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
"""Simple test for servo actuation"""
import math
from random import randint
from kinematics import Kinematics

random = True
kinematics = Kinematics(False)

def random_angle() -> float:
    """Returns a random angle betwee 89.5 and -89.5 degress
    :return: Random angle between 89.5 and -89.5 degrees.
    :rtype: float
    """
    a = randint(-89.5, 89.5) * 1.0
    return a

def random_test():
    """Performs kinematics and reerse kinematics test on random set of points.
    """
    count = 0
    while count < 100000:
        a = random_angle()
        b = random_angle()
        c = random_angle()
        x, y, z = kinematics.toCartesian(a, b, c)
        a1, b1, c1 = kinematics.fromCartesian(x, y, z)
        if not math.isclose(a1, a, abs_tol=0.00001) or \
           not math.isclose(b1, b, abs_tol=0.00001) or \
           not math.isclose(c1, c, abs_tol=0.00001):
            # counter resolve as we may have passed an inflection point
            x1, y1, z1 = kinematics.toCartesian(a1, b1, c1)
            if not math.isclose(x1, x, abs_tol=0.00001) or \
               not math.isclose(y1, y, abs_tol=0.00001) or \
               not math.isclose(z1, z, abs_tol=0.00001):
                print("failed to resolve (%f, %f, %f) ->\n                  (%f, %f, %f) ->\n                  (%f, %f, %f) ->\n                  (%f, %f, %f)" % (a, b, c, x, y, z, a1, b1, c1, x1, y1, z1))
        count += 1
    print("%d test completed" % count)

def test():
    """Linear test of reverse kinematics
    """
    x_start = 0
    y_start = 0
    z_start = -0
    x_end = 0
    y_end = 173
    z_end = 0
    increment = 5

    while x_start < x_end:
        hip, shoulder, elbow = kinematics.fromCartesian(x_start, y_start, z_start)
        x_start += increment
        print("(%f, %f, %f) -> (%f, %f, %f)" % (x_start, y_start, z_start, hip, shoulder, elbow))

    while y_start < y_end:
        hip, shoulder, elbow = kinematics.fromCartesian(x_start, y_start, z_start)
        y_start += increment
        print("(%f, %f, %f) -> (%f, %f, %f)" % (x_start, y_start, z_start, hip, shoulder, elbow))

    while z_start < z_end:
        hip, shoulder, elbow = kinematics.fromCartesian(x_start, y_start, z_start)
        z_start += increment
        print("(%f, %f, %f) -> (%f, %f, %f)" % (x_start, y_start, z_start, hip, shoulder, elbow))

    print("test completed")

if random:
    random_test()
else:
    test()
