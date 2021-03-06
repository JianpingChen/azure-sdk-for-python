# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

import msrest.serialization


class StsTokenResponseMessage(msrest.serialization.Model):
    """Represents a token response message from the STS service.

    All required parameters must be populated in order to send to Azure.

    :param access_token: Required. An access token for the account.
    :type access_token: str
    """

    _validation = {
        'access_token': {'required': True},
    }

    _attribute_map = {
        'access_token': {'key': 'AccessToken', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(StsTokenResponseMessage, self).__init__(**kwargs)
        self.access_token = kwargs['access_token']


class TokenRequestOptions(msrest.serialization.Model):
    """Parameter group.

    :param client_request_id: The client request correlation vector, which should be set to a new
     value for each request. Useful when debugging with Microsoft.
    :type client_request_id: str
    """

    _attribute_map = {
        'client_request_id': {'key': 'clientRequestId', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(TokenRequestOptions, self).__init__(**kwargs)
        self.client_request_id = kwargs.get('client_request_id', None)
