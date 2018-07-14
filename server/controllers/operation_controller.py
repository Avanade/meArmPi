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
"""Operations controller for the RPI meArm REST interface."""
import connexion
import six
import uuid
import datetime

from flask import make_response
from server.models.inline_response200 import InlineResponse200  # noqa: E501
from server.models.inline_response2001 import InlineResponse2001  # noqa: E501
from server.models.inline_response2002 import InlineResponse2002  # noqa: E501
from server.models.operations import Operations  # noqa: E501
from server.models.status import Status  # noqa: E501
from server import util
from server import common

def checkin(token):  # noqa: E501
    """checkin

    Checks in the arm to complete the session and remove the lock # noqa: E501

    :param token: Session token. This token should be obtained using /arm/checkout.
    :type token: dict | bytes

    :rtype: InlineResponse2001
    """
    #if connexion.request.is_json:
    #    token = .from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def checkout():  # noqa: E501
    """checkout

    Checks out the arm for a session. # noqa: E501


    :rtype: InlineResponse200
    """
    if common.Token is not None:
        return common.Status, 403

    common.Token = uuid.UUID()
    common.Status = Status(
        common.Hostname,
        common.Version,
        True,
        datetime.datetime.now(),
        0,
        None)

    response = InlineResponse200(common.Token)
    return response

def operate(token, operations):  # noqa: E501
    """operate

    Operates the arm using a list of operations. # noqa: E501

    :param token: Session token. This token should be obtained using /arm/checkout.
    :type token: dict | bytes
    :param operations: A list of operations to be executed.
    :type operations: dict | bytes

    :rtype: InlineResponse2002
    """
    #if connexion.request.is_json:
    #    token = .from_dict(connexion.request.get_json())  # noqa: E501
    if connexion.request.is_json:
        operations = Operations.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
