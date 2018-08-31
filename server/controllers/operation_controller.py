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

from server.models.token import Token  # noqa: E501
from server.models.session_status import SessionStatus  # noqa: E501
from server.models.operations_status import OperationStatus  # noqa: E501
from server.models.operations import Operations  # noqa: E501
from server.models.operation import Operation  # noqa: E501
from server.models.status import Status  # noqa: E501
from server import common
from arm import me_arm
from kinematics import Point

def checkin(id): # noqa: E501
    # currently, header parameters will not be passed as arguments to controller
    # methods in connexion
    # http://connexion.readthedocs.io/en/latest/request.html#header-parameters
    """checkin

    Checks in the arm to complete the session and remove the lock # noqa: E501

    :param id: The id of the meArm.
    :type id: str
    :param token: Session token. This token should be obtained using /arm/checkout.
    :type token: dict | bytes

    :rtype: SessionStatus
    """
    if id not in me_arm.get_names():
        return 'meArm with name %s is not known' % id, 400 

    if connexion.request.headers['token'] is None:
        return 'Missing header value "token"', 400

    token = None
    try:
        token = uuid.UUID(connexion.request.headers['token'])
    except ValueError:
        return 'Invalid token format', 400

    if token != common.token[id]:
        return common.status[id], 403

    status= common.status[id]
    ops = status.movements_since_checkout
    duration = (datetime.datetime.now() - status.checked_out_since).total_seconds()
    common.status[id] = Status(common.HOSTNAME, common.VERSION, False)
    common.token[id] = None
    arm = me_arm.get(id)
    arm.reset()

    #if no other arms on the controller are checked out, reset the controller....
    shouldShutdown = all(v is None for v in common.token.values())
    if shouldShutdown: me_arm.shutdown(False)

    return SessionStatus(False, duration, ops)

def checkout(id):  # noqa: E501
    """checkout

    Checks out the arm for a session. # noqa: E501

    :param id: The id of the meArm.
    :type id: str

    :rtype: Token
    """
    if id not in me_arm.get_names():
        return 'meArm with name %s is not known' % id, 400 

    if common.token[id] is not None:
        return common.status[id], 403

    common.token[id] = uuid.uuid4()
    common.status[id] = Status(
        common.HOSTNAME,
        common.VERSION,
        True,
        datetime.datetime.now(),
        0,
        None)

    response = Token(common.token[id])
    return response

def operate(id, operations):  # noqa: E501
    # currently, header parameters will not be passed as arguments to controller
    # methods in connexion
    # http://connexion.readthedocs.io/en/latest/request.html#header-parameters
    """operate

    Operates the arm using a list of operations. # noqa: E501

    :param id: The id of the meArm.
    :type id: str
    :param token: Session token. This token should be obtained using /arm/checkout.
    :type token: dict | bytes
    :param operations: A list of operations to be executed.
    :type operations: dict | bytes

    :rtype: OperationStatus
    """
    t_start = datetime.datetime.now()

    if id not in me_arm.get_names():
        return 'meArm with name %s is not known' % id, 400 

    if connexion.request.headers['token'] is None:
        return 'Missing header value "token"', 400

    token = None
    try:
        token = uuid.UUID(connexion.request.headers['token'])
    except ValueError:
        return 'Invalid token format', 400

    if token != common.token[id]:
        return common.status[id], 403

    count = 0
    try:
        if connexion.request.is_json:
            operations = Operations.from_dict(connexion.request.get_json())  # noqa: E501
            if len(operations) > 25:
                return 'Too many operations. Reduce the number of operations to 10 or less', 413
            arm = me_arm.get(id)
            num_ops = 0
            for dummy, val in enumerate(operations):
                count += 1
                if val.type == 'moveTo':
                    if val.target.x is None or val.target.y is None or val.target.z is None:
                        target = Point.fromPolar(val.target.r, val.target.lat, val.target.lng)
                    else:
                        target = Point.fromCartesian(val.target.x, val.target.y, val.target.z)
                    num_ops += arm.go_to_point(target, 2.5, False)
                elif val.type == 'grab':
                    arm.close()
                    num_ops += 1
                elif val.type == 'release':
                    arm.open()
                    num_ops += 1
                elif val.type == 'test':
                    num_ops += arm.test(False)
                else:
                    raise ValueError(Operation)
    except ValueError:
        return 'Incorrect operation type. Only moveTo, grab and release are supported', 400

    return OperationStatus(
        count,
        (datetime.datetime.now() - t_start).total_seconds(),
        common.status[id].position)
