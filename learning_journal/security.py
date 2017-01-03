"""Security for pyramid app."""

import os

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Authenticated, Allow, Everyone
from passlib.apps import custom_app_context as pwd_context


class NewRoot(object):
    """Takes in a http request and add access control route."""

    def __init__(self, request):
        """Initiate object with request."""
        self.request = request

    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, Authenticated, 'add'),
    ]


def check_credentials(username, password):
    """Check username and password and return true if correct."""
    if username and password:
        if username == os.environ["AUTH_USERNAME"]:
            return pwd_context.verify(password, os.environ["AUTH_PASSWORD"])
    return False


def includeme(config):
    """Security-related configuration."""
    auth_secret = os.environ.get('AUTH_SECRET', 's00perseekrit')
    authn_policy = AuthTktAuthenticationPolicy(
        secret=auth_secret,
        hashalg='sha512'
    )
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.set_default_permission('view')
    config.set_root_factory(NewRoot)
