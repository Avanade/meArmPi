# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from server.models.inline_response200 import InlineResponse200  # noqa: E501
from server.models.inline_response2001 import InlineResponse2001  # noqa: E501
from server.models.inline_response2002 import InlineResponse2002  # noqa: E501
from server.models.operations import Operations  # noqa: E501
from server.models.status import Status  # noqa: E501
from server.test import BaseTestCase


class TestOperationController(BaseTestCase):
    """OperationController integration test stubs"""

    def test_checkin(self):
        """Test case for checkin

        
        """
        headers = [('token', 'token_example')]
        response = self.client.open(
            '/thor-schueler/Avanade.meArm1/1.0.0/arm/checkin',
            method='POST',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_checkout(self):
        """Test case for checkout

        
        """
        response = self.client.open(
            '/thor-schueler/Avanade.meArm1/1.0.0/arm/checkout',
            method='POST')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_operate(self):
        """Test case for operate

        
        """
        operations = Operations()
        headers = [('token', 'token_example')]
        response = self.client.open(
            '/thor-schueler/Avanade.meArm1/1.0.0/arm/operate',
            method='POST',
            data=json.dumps(operations),
            content_type='application/json',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
