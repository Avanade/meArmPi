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
from kinematics import Kinematics

kinematics = Kinematics(False)
increment = 5.0
hip = 0.0
shoulder = 82.0
elbow = -45.0

# run a loop through the elbow angles and reverse
elbow = -135.0
while elbow < 30.0:
    x, y, z = kinematics.toCartesian(hip, shoulder, elbow)
    a, b, c = kinematics.fromCartesian(x, y, z)
    print ("(%f, %f, %f) -> (%f, %f, %f) -> (%f, %f, %f)\n" % (hip, shoulder, elbow, x, y, z, a, b, c))
    elbow += increment

