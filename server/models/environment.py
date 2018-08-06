# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from server.models.base_model_ import Model
from server import util


class Environment(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(self, number_of_controllers: float=None, number_of_arms: float=None, arms: List[str]=None):  # noqa: E501
        """Environment - a model defined in Swagger

        :param number_of_controllers: The number_of_controllers of this Environment.  # noqa: E501
        :type number_of_controllers: float
        :param number_of_arms: The number_of_arms of this Environment.  # noqa: E501
        :type number_of_arms: float
        :param arms: The arms of this Environment.  # noqa: E501
        :type arms: List[str]
        """
        self.swagger_types = {
            'number_of_controllers': float,
            'number_of_arms': float,
            'arms': List[str]
        }

        self.attribute_map = {
            'number_of_controllers': 'numberOfControllers',
            'number_of_arms': 'numberOfArms',
            'arms': 'arms'
        }

        self._number_of_controllers = number_of_controllers
        self._number_of_arms = number_of_arms
        self._arms = arms

    @classmethod
    def from_dict(cls, dikt) -> 'Environment':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Environment of this Environment.  # noqa: E501
        :rtype: Environment
        """
        return util.deserialize_model(dikt, cls)

    @property
    def number_of_controllers(self) -> float:
        """Gets the number_of_controllers of this Environment.

        The number of controllers driving meArms.  # noqa: E501

        :return: The number_of_controllers of this Environment.
        :rtype: float
        """
        return self._number_of_controllers

    @number_of_controllers.setter
    def number_of_controllers(self, number_of_controllers: float):
        """Sets the number_of_controllers of this Environment.

        The number of controllers driving meArms.  # noqa: E501

        :param number_of_controllers: The number_of_controllers of this Environment.
        :type number_of_controllers: float
        """

        self._number_of_controllers = number_of_controllers

    @property
    def number_of_arms(self) -> float:
        """Gets the number_of_arms of this Environment.

        The number of meArms in the environement.  # noqa: E501

        :return: The number_of_arms of this Environment.
        :rtype: float
        """
        return self._number_of_arms

    @number_of_arms.setter
    def number_of_arms(self, number_of_arms: float):
        """Sets the number_of_arms of this Environment.

        The number of meArms in the environement.  # noqa: E501

        :param number_of_arms: The number_of_arms of this Environment.
        :type number_of_arms: float
        """

        self._number_of_arms = number_of_arms

    @property
    def arms(self) -> List[str]:
        """Gets the arms of this Environment.


        :return: The arms of this Environment.
        :rtype: List[str]
        """
        return self._arms

    @arms.setter
    def arms(self, arms: List[str]):
        """Sets the arms of this Environment.


        :param arms: The arms of this Environment.
        :type arms: List[str]
        """

        self._arms = arms