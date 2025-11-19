# -*- coding: utf-8 -*-

"""
mixvel.endpoint
~~~~~~~~~~~~~~
Provides internal functions for working with MixVel API endpoints.
"""


def is_login_endpoint(endpoint):
    """Determines if the given endpoint is the login endpoint.

    :param endpoint: endpoint
    :type endpoint: str
    :rtype: bool
    """
    return endpoint == "/api/Accounts/login"


