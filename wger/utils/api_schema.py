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

# Django
from django.urls import reverse

# Third Party
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework import serializers


class OidcTokenScheme(OpenApiAuthenticationExtension):
    """
    Schema entry for allauth's OIDC access tokens.

    Without this, drf-spectacular can't resolve the authentication class and
    leaves the endpoints without the security scheme.
    """

    target_class = 'allauth.idp.oidc.contrib.rest_framework.authentication.TokenAuthentication'
    name = 'oidcAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'oauth2',
            'description': 'Access token issued by the OAuth2/OIDC provider',
            'flows': {
                'authorizationCode': {
                    'authorizationUrl': reverse('idp:oidc:authorization'),
                    'tokenUrl': reverse('idp:oidc:token'),
                    'scopes': {
                        'openid': 'Identify the account',
                        'profile': 'Read the username',
                        'email': 'Read the email address',
                    },
                }
            },
        }


class ThumbnailsSerializer(serializers.Serializer):
    """
    Shape of the ``thumbnails`` field, used for schema generation only.

    The aliases are read from settings.THUMBNAIL_ALIASES and are the same for
    every thumbnailed image in the API. Without this, the generated schema falls
    back to a plain string for the dict the method fields return.
    """

    small = serializers.URLField()
    medium = serializers.URLField()
