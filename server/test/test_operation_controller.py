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
# coding: utf-8
"""Unit Tests for the meArm Operations controller."""
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
