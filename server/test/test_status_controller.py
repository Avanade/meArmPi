# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from server.models.point import Point  # noqa: E501
from server.models.status import Status  # noqa: E501
from server.test import BaseTestCase


class TestStatusController(BaseTestCase):
    """StatusController integration test stubs"""

    def test_get_arm(self):
        """Test case for get_arm

        
        """
        response = self.client.open(
            '/thor-schueler/Avanade.meArm1/1.0.0/arm',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_position(self):
        """Test case for get_position

        
        """
        response = self.client.open(
            '/thor-schueler/Avanade.meArm1/1.0.0/arm/position',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
