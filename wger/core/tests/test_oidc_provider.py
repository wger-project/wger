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

# Standard Library
import base64
import hashlib
import secrets
from io import StringIO
from urllib.parse import (
    parse_qs,
    urlparse,
)

# Django
from django.conf import settings
from django.core.management import call_command
from django.test import (
    SimpleTestCase,
    override_settings,
)
from django.urls import reverse
from django.utils.http import urlencode

# Third Party
import jwt
from allauth.idp.oidc.models import Client
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# wger
from wger.core.tests.base_testcase import WgerTestCase


REDIRECT_URI = 'https://client.example.com/callback'


def generate_private_key() -> str:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()


def generate_pkce_pair() -> tuple[str, str]:
    """
    Returns a code verifier and its S256 challenge
    """
    verifier = secrets.token_urlsafe(96)
    digest = hashlib.sha256(verifier.encode('ascii')).digest()
    return verifier, base64.urlsafe_b64encode(digest).rstrip(b'=').decode()


class GenerateOidcKeyTestCase(SimpleTestCase):
    """
    Test the generate-oidc-key management command
    """

    def test_output_is_a_usable_env_value(self):
        out = StringIO()
        call_command('generate-oidc-key', '--key-size', '1024', stdout=out)

        name, _, value = out.getvalue().splitlines()[-1].partition('=')
        self.assertEqual(name, 'IDP_OIDC_PRIVATE_KEY')
        self.assertNotIn('\n', value)

        # The escaped newlines are what django-environ turns back into a PEM
        pem = value.replace('\\n', '\n')
        key = serialization.load_pem_private_key(pem.encode(), password=None)
        self.assertEqual(key.key_size, 1024)


class OidcProviderTestCase(WgerTestCase):
    """
    End-to-end test for the OAuth2/OIDC provider (allauth.idp.oidc)
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.private_key = generate_private_key()

    def setUp(self):
        super().setUp()
        self.oidc_client = Client(type=Client.Type.PUBLIC, name='Test client')
        self.oidc_client.set_redirect_uris([REDIRECT_URI])
        self.oidc_client.set_scopes(['openid', 'profile', 'email'])
        self.oidc_client.set_grant_types(
            [Client.GrantType.AUTHORIZATION_CODE, Client.GrantType.REFRESH_TOKEN]
        )
        self.oidc_client.set_response_types([Client.ResponseType.CODE])
        self.oidc_client.save()

    def request_authorization(self, challenge: str, scope: str = 'openid profile'):
        """
        Opens the consent screen, returns its response
        """
        query = urlencode(
            {
                'client_id': self.oidc_client.id,
                'redirect_uri': REDIRECT_URI,
                'response_type': 'code',
                'scope': scope,
                'state': 'some-state',
                'code_challenge': challenge,
                'code_challenge_method': 'S256',
            }
        )
        return self.client.get(f'{reverse("idp:oidc:authorization")}?{query}')

    def grant_authorization(self, challenge: str, scope: str = 'openid profile') -> str:
        """
        Runs the browser part of the flow, returns the authorization code
        """
        response = self.request_authorization(challenge, scope)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'idp/oidc/authorization_form.html')

        response = self.client.post(
            reverse('idp:oidc:authorization'),
            {
                'request': response.context['form']['request'].value(),
                'scopes': scope.split(' '),
                'action': 'grant',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['location'].startswith(REDIRECT_URI))

        params = parse_qs(urlparse(response['location']).query)
        self.assertEqual(params['state'][0], 'some-state')
        return params['code'][0]

    def test_discovery_without_signing_key(self):
        """
        Discovery answers without a signing key configured, the key set is empty
        """
        response = self.client.get(reverse('idp:oidc:configuration'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['issuer'], 'http://testserver')
        self.assertEqual(
            data['authorization_endpoint'],
            f'http://testserver{reverse("idp:oidc:authorization")}',
        )
        self.assertEqual(data['token_endpoint'], f'http://testserver{reverse("idp:oidc:token")}')
        self.assertIn('S256', data['code_challenge_methods_supported'])

        # Both need an explicit opt-in
        self.assertNotIn('registration_endpoint', data)
        self.assertNotIn('introspection_endpoint', data)

        response = self.client.get(reverse('idp:oidc:jwks'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['keys'], [])

    def test_jwks_publishes_the_signing_key(self):
        with override_settings(IDP_OIDC_PRIVATE_KEY=self.private_key):
            response = self.client.get(reverse('idp:oidc:jwks'))

        self.assertEqual(response.status_code, 200)
        keys = response.json()['keys']
        self.assertEqual(len(keys), 1)
        self.assertEqual(keys[0]['kty'], 'RSA')
        self.assertEqual(keys[0]['key_ops'], ['verify'])
        self.assertIn('n', keys[0])

    def test_authorization_code_flow(self):
        """
        Authorization code flow with PKCE, the access token acts as the user
        """
        self.user_login('test')
        verifier, challenge = generate_pkce_pair()

        with override_settings(IDP_OIDC_PRIVATE_KEY=self.private_key):
            code = self.grant_authorization(challenge)

            response = self.client.post(
                reverse('idp:oidc:token'),
                {
                    'grant_type': 'authorization_code',
                    'code': code,
                    'client_id': self.oidc_client.id,
                    'redirect_uri': REDIRECT_URI,
                    'code_verifier': verifier,
                },
            )
            self.assertEqual(response.status_code, 200, response.content)
            token = response.json()

            id_token = jwt.decode(
                token['id_token'],
                options={'verify_signature': False},
                audience=self.oidc_client.id,
            )

        self.assertEqual(token['token_type'], 'Bearer')
        self.assertEqual(token['scope'], 'openid profile')
        self.assertEqual(id_token['preferred_username'], 'test')

        # The access token authenticates a regular API request as the user that
        # granted it. Log out first, otherwise SessionAuthentication answers.
        self.client.logout()
        response = self.client.get(
            reverse('userprofile-list'),
            HTTP_AUTHORIZATION=f'Bearer {token["access_token"]}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['username'], 'test')

    def test_code_is_rejected_without_the_verifier(self):
        self.user_login('test')
        _, challenge = generate_pkce_pair()

        with override_settings(IDP_OIDC_PRIVATE_KEY=self.private_key):
            code = self.grant_authorization(challenge)
            response = self.client.post(
                reverse('idp:oidc:token'),
                {
                    'grant_type': 'authorization_code',
                    'code': code,
                    'client_id': self.oidc_client.id,
                    'redirect_uri': REDIRECT_URI,
                },
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'invalid_request')

    def test_cancelled_authorization_issues_no_code(self):
        self.user_login('test')
        _, challenge = generate_pkce_pair()

        response = self.request_authorization(challenge)
        response = self.client.post(
            reverse('idp:oidc:authorization'),
            {'request': response.context['form']['request'].value()},
        )

        self.assertEqual(response.status_code, 302)
        params = parse_qs(urlparse(response['location']).query)
        self.assertEqual(params['error'], ['access_denied'])
        self.assertNotIn('code', params)

    def test_anonymous_authorization_redirects_to_login(self):
        _, challenge = generate_pkce_pair()

        response = self.request_authorization(challenge)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['location'].startswith(f'{settings.LOGIN_URL}?next='))
