# -*- coding: utf-8 -*-

# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

# Django
from django.conf import settings
from django.http import Http404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# Third Party
from allauth.idp.oidc.adapter import DefaultOIDCAdapter
from allauth.idp.oidc.contrib.rest_framework.authentication import TokenAuthentication
from allauth.idp.oidc.views import authorization
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import SAFE_METHODS

# wger
from wger.utils.url import make_absolute_url


SCOPE_READ = 'api:read'
SCOPE_WRITE = 'api:write'

API_SCOPES = {
    SCOPE_READ: _('View your training, nutrition and body data'),
    SCOPE_WRITE: _('Add and change your training, nutrition and body data'),
}


def is_provider_configured() -> bool:
    """
    Whether this installation acts as an OAuth2/OIDC provider
    """
    return bool(settings.IDP_OIDC_PRIVATE_KEY or getattr(settings, 'IDP_OIDC_PRIVATE_KEYS', None))


def authorization_view(request, *args, **kwargs):
    """
    allauth's authorization view, but only if the provider is set up.

    Without a signing key the flow would run all the way through the consent
    screen and only fail afterwards, when the token endpoint tries to sign an
    ID token. Users would grant access to something that cannot work.
    """
    if not is_provider_configured():
        raise Http404('The OAuth2 provider is not configured')

    return authorization(request, *args, **kwargs)


class OidcTokenAuthentication(TokenAuthentication):
    """
    Access tokens of the OAuth2/OIDC provider, restricted by scope.

    The check happens here and not in a permission class because a good two
    dozen viewsets set ``permission_classes`` themselves and would silently
    skip a default one. Reads need ``api:read``, everything else ``api:write``,
    so no endpoint can be forgotten and new ones are covered as they are added.
    """

    def authenticate(self, request):
        # Checked first so that installations without the provider don't pay for
        # the token lookup, which every request with a bearer token would
        # otherwise trigger.
        if not is_provider_configured():
            return None

        result = super().authenticate(request)
        if result is None:
            return None

        user, token = result
        scope = SCOPE_READ if request.method in SAFE_METHODS else SCOPE_WRITE
        if token is None or scope not in token.get_scopes():
            raise PermissionDenied(
                f'The access token is missing the "{scope}" scope.',
                code='insufficient_scope',
            )

        return user, token


class WgerOIDCAdapter(DefaultOIDCAdapter):
    """
    Teaches allauth about the API scopes.

    ``scope_display`` provides the labels on the consent screen, without it the
    users are asked to grant a raw "api:write". The metadata hook adds them to
    the discovery document, which only knows the identity scopes.
    """

    scope_display = {
        **DefaultOIDCAdapter.scope_display,
        **API_SCOPES,
    }

    def populate_server_metadata(self, data: dict) -> None:
        super().populate_server_metadata(data)
        data['scopes_supported'] = sorted({*data['scopes_supported'], *API_SCOPES})


class OidcTokenScheme(OpenApiAuthenticationExtension):
    """
    Schema entry for the OIDC access tokens.

    Without this, drf-spectacular can't resolve the authentication class and
    leaves the endpoints without the security scheme.
    """

    target_class = 'wger.utils.oidc_auth.OidcTokenAuthentication'
    name = 'oidcAuth'

    def get_security_definition(self, auto_schema):
        # OpenAPI 3.0 wants absolute URLs here, a relative path makes code
        # generators build a broken one. Without SITE_URL the paths stay
        # relative: a degraded schema beats one that can't be generated.
        return {
            'type': 'oauth2',
            'description': 'Access token issued by the OAuth2/OIDC provider',
            'flows': {
                'authorizationCode': {
                    'authorizationUrl': make_absolute_url(reverse('idp:oidc:authorization')),
                    'tokenUrl': make_absolute_url(reverse('idp:oidc:token')),
                    'scopes': {str(name): str(label) for name, label in API_SCOPES.items()},
                }
            },
        }
