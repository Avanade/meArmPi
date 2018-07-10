import connexion
import six

from server.models.point import Point  # noqa: E501
from server.models.status import Status  # noqa: E501
from server import util


def get_arm():  # noqa: E501
    """get_arm

    Gets the current status of the meArm. # noqa: E501


    :rtype: Status
    """
    return 'do some magic!'


def get_position():  # noqa: E501
    """get_position

    Gets hte current position of the meArm # noqa: E501


    :rtype: Point
    """
    return 'do some magic!'
