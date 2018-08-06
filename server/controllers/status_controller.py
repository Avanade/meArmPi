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
"""Status controller for the RPI meArm REST interface."""
from server.models.point import Point as PointModel  # noqa: E501
from server import common
from arm import me_arm

def get_arm(id):  # noqa: E501
    """get_arm
    Gets the current status of the meArm. # noqa: E501

    :param id: The id of the meArm.
    :type id: str

    :rtype: Status
    """
    if id not in me_arm.get_names():
        return 'meArm with name %s is not known' % id, 400 

    status = common.status[id]
    return status.to_dict()

def get_position(id):  # noqa: E501
    """get_position
    Gets the current position of the meArm # noqa: E501

    :param id: The id of the meArm.
    :type id: str

    :rtype: Point
    """

    if id not in me_arm.get_names():
        return 'meArm with name %s is not known' % id, 400 

    status = common.status[id]
    if status.position is None:
        return PointModel(0, 0, 0, 0, 0, 0).to_dict()
    return status.position.to_dict()
