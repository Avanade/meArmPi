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
import uuid
import datetime
import connexion

from server.models.inline_response200 import InlineResponse200  # noqa: E501
from server.models.inline_response2001 import InlineResponse2001  # noqa: E501
from server.models.inline_response2002 import InlineResponse2002  # noqa: E501
from server.models.operations import Operations  # noqa: E501
from server.models.operation import Operation  # noqa: E501
from server.models.status import Status  # noqa: E501
from server import common

def checkin(): # noqa: E501
    # currently, header parameters will not be passed as arguments to controller
    # methods in connexion
    # http://connexion.readthedocs.io/en/latest/request.html#header-parameters
    """checkin

    Checks in the arm to complete the session and remove the lock # noqa: E501

    :param token: Session token. This token should be obtained using /arm/checkout.
    :type token: dict | bytes

    :rtype: InlineResponse2001
    """
    if connexion.request.headers['token'] is None:
        return 'Missing header value "token"', 400

    token = None
    try:
        token = uuid.UUID(connexion.request.headers['token'])
    except ValueError:
        return 'Invalid token format', 400

    if token != common.Token:
        return common.Status, 403

    ops = common.Status.movements_since_checkout
    duration = (datetime.datetime.now() - common.Status.checked_out_since).total_seconds()
    common.Status = Status(common.HOSTNAME, common.VERSION, False)
    common.Token = None
    return InlineResponse2001(False, duration, ops)


def checkout():  # noqa: E501
    """checkout

    Checks out the arm for a session. # noqa: E501


    :rtype: InlineResponse200
    """
    if common.Token is not None:
        return common.Status, 403

    common.Token = uuid.uuid4()
    common.Status = Status(
        common.Hostname,
        common.Version,
        True,
        datetime.datetime.now(),
        0,
        None)

    response = InlineResponse200(common.Token)
    return response

def operate(operations):  # noqa: E501
    # currently, header parameters will not be passed as arguments to controller
    # methods in connexion
    # http://connexion.readthedocs.io/en/latest/request.html#header-parameters
    """operate

    Operates the arm using a list of operations. # noqa: E501

    :param token: Session token. This token should be obtained using /arm/checkout.
    :type token: dict | bytes
    :param operations: A list of operations to be executed.
    :type operations: dict | bytes

    :rtype: InlineResponse2002
    """
    t_start = datetime.datetime.now()
    if connexion.request.headers['token'] is None:
        return 'Missing header value "token"', 400

    token = None
    try:
        token = uuid.UUID(connexion.request.headers['token'])
    except ValueError:
        return 'Invalid token format', 400

    if token != common.Token:
        return common.Status, 403

    count = 0
    try:
        if connexion.request.is_json:
            operations = Operations.from_dict(connexion.request.get_json())  # noqa: E501
            if len(operations) > 10:
                return 'Too many operations. Reduce the number of operations to 10 or less', 413
            for i, val in enumerate(operations):
                count += 1
                if val.type == 'moveTo':
                    # do nothing
                    print(val.type)
                elif val.type == 'grab':
                    # do nothing
                    print(val.type)
                elif val.type == 'release':
                    # do nothing
                    print(val.type)
                else:
                    raise ValueError(Operation)
    except ValueError:
        return 'Incorrect operation type. Only moveTo, grab and release are supported', 400

    return InlineResponse2002(
        count,
        (datetime.datetime.now() - t_start).total_seconds(),
        common.Status.position)
