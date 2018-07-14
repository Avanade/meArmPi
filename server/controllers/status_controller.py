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
import connexion
import six

from server.models.point import Point as PointModel  # noqa: E501
from server.models.status import Status  # noqa: E501
from server import util
from server import common


def get_arm():  # noqa: E501
    """get_arm

    Gets the current status of the meArm. # noqa: E501


    :rtype: Status
    """
    return common.Status


def get_position():  # noqa: E501
    """get_position

    Gets hte current position of the meArm # noqa: E501


    :rtype: Point
    """
    if common.Status.position is None:
        return PointModel(0, 0, 0, 0, 0, 0)
    return common.Status.position
