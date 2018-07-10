import connexion
import six

from server.models.inline_response200 import InlineResponse200  # noqa: E501
from server.models.inline_response2001 import InlineResponse2001  # noqa: E501
from server.models.inline_response2002 import InlineResponse2002  # noqa: E501
from server.models.operations import Operations  # noqa: E501
from server.models.status import Status  # noqa: E501
from server import util


def checkin(token):  # noqa: E501
    """checkin

    Checks in the arm to complete the session and remove the lock # noqa: E501

    :param token: Session token. This token should be obtained using /arm/checkout.
    :type token: dict | bytes

    :rtype: InlineResponse2001
    """
    if connexion.request.is_json:
        token = .from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def checkout():  # noqa: E501
    """checkout

    Checks out the arm for a session. # noqa: E501


    :rtype: InlineResponse200
    """
    return 'do some magic!'


def operate(token, operations):  # noqa: E501
    """operate

    Operates the arm using a list of operations. # noqa: E501

    :param token: Session token. This token should be obtained using /arm/checkout.
    :type token: dict | bytes
    :param operations: A list of operations to be executed.
    :type operations: dict | bytes

    :rtype: InlineResponse2002
    """
    if connexion.request.is_json:
        token = .from_dict(connexion.request.get_json())  # noqa: E501
    if connexion.request.is_json:
        operations = Operations.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
