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
import re
import secrets
from datetime import timedelta
from io import StringIO
from urllib.parse import (
    parse_qs,
    urlparse,
)

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import (
    Client as TestClient,
    SimpleTestCase,
    override_settings,
)
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode

# Third Party
import jwt
from allauth.idp.oidc.adapter import get_adapter
from allauth.idp.oidc.models import (
    Client,
    Token,
)
from allauth.mfa.totp.internal.auth import (
    TOTP,
    format_hotp_value,
    generate_totp_secret,
    hotp_value,
    yield_hotp_counters_from_time,
)
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# wger
from wger.core.tasks import flush_expired_oidc_tokens_task
from wger.core.tests.base_testcase import WgerTestCase
from wger.utils.oidc_auth import (
    SCOPE_READ,
    SCOPE_WRITE,
)


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
        self.enterContext(override_settings(IDP_OIDC_PRIVATE_KEY=self.private_key))

        self.oidc_client = Client(type=Client.Type.PUBLIC, name='Test client')
        self.oidc_client.set_redirect_uris([REDIRECT_URI])
        self.oidc_client.set_scopes(['openid', 'profile', 'email', SCOPE_READ, SCOPE_WRITE])
        self.oidc_client.set_grant_types(
            [Client.GrantType.AUTHORIZATION_CODE, Client.GrantType.REFRESH_TOKEN]
        )
        self.oidc_client.set_response_types([Client.ResponseType.CODE])
        self.oidc_client.save()

    def request_authorization(self, challenge: str, scope: str = f'openid profile {SCOPE_READ}'):
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

    def grant_authorization(
        self, challenge: str, scope: str = f'openid profile {SCOPE_READ}'
    ) -> str:
        """
        Runs the browser part of the flow, returns the authorization code
        """
        response = self.request_authorization(challenge, scope)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'idp/oidc/authorization_form.html')

        # allauth's own template renders no action attribute, so this also
        # asserts that wger's override is the one being used
        self.assertContains(response, f'action="{reverse("idp:oidc:authorization")}"')

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

    @override_settings(IDP_OIDC_PRIVATE_KEY='')
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
        response = self.client.get(reverse('idp:oidc:jwks'))

        self.assertEqual(response.status_code, 200)
        keys = response.json()['keys']
        self.assertEqual(len(keys), 1)
        self.assertEqual(keys[0]['kty'], 'RSA')
        self.assertEqual(keys[0]['key_ops'], ['verify'])
        self.assertIn('n', keys[0])

    def redeem_code(self, code: str, **overrides):
        """
        Exchanges an authorization code for tokens
        """
        payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.oidc_client.id,
            'redirect_uri': REDIRECT_URI,
        }
        payload.update(overrides)
        return self.client.post(reverse('idp:oidc:token'), payload)

    def test_authorization_code_flow(self):
        """
        Authorization code flow with PKCE, the access token acts as the user
        """
        self.user_login('test')
        verifier, challenge = generate_pkce_pair()

        code = self.grant_authorization(challenge)
        response = self.redeem_code(code, code_verifier=verifier)
        self.assertEqual(response.status_code, 200, response.content)
        token = response.json()

        # Verified against the published key set, a mismatch between the two
        # would break every relying party
        jwks = self.client.get(reverse('idp:oidc:jwks')).json()
        id_token = jwt.decode(
            token['id_token'],
            key=jwt.PyJWK.from_dict(jwks['keys'][0], algorithm='RS256').key,
            algorithms=['RS256'],
            audience=self.oidc_client.id,
        )

        self.assertEqual(token['token_type'], 'Bearer')
        self.assertEqual(token['scope'], f'openid profile {SCOPE_READ}')
        self.assertEqual(id_token['preferred_username'], 'test')

        # The access token authenticates a regular API request as the user that
        # granted it. Log out first, otherwise SessionAuthentication answers.
        self.client.logout()
        response = self.client.get(
            reverse('userprofile'),
            HTTP_AUTHORIZATION=f'Bearer {token["access_token"]}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['username'], 'test')

    def test_code_is_rejected_without_the_verifier(self):
        self.user_login('test')
        _, challenge = generate_pkce_pair()

        code = self.grant_authorization(challenge)
        response = self.redeem_code(code)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'invalid_request')

    def test_code_is_rejected_with_a_wrong_verifier(self):
        self.user_login('test')
        _, challenge = generate_pkce_pair()
        other_verifier, _ = generate_pkce_pair()

        code = self.grant_authorization(challenge)
        response = self.redeem_code(code, code_verifier=other_verifier)

        self.assertEqual(response.status_code, 400)

    def test_code_cannot_be_redeemed_twice(self):
        self.user_login('test')
        verifier, challenge = generate_pkce_pair()

        code = self.grant_authorization(challenge)
        self.assertEqual(self.redeem_code(code, code_verifier=verifier).status_code, 200)
        response = self.redeem_code(code, code_verifier=verifier)

        self.assertEqual(response.status_code, 400)

    def test_code_is_rejected_for_another_redirect_uri(self):
        self.user_login('test')
        verifier, challenge = generate_pkce_pair()

        code = self.grant_authorization(challenge)
        response = self.redeem_code(
            code,
            code_verifier=verifier,
            redirect_uri='https://attacker.example.com/callback',
        )

        self.assertEqual(response.status_code, 400)

    def test_unknown_redirect_uri_never_redirects(self):
        """
        An unregistered redirect URI has to fail on the provider, redirecting to
        it would hand the authorization code to whoever asked for it
        """
        self.user_login('test')
        _, challenge = generate_pkce_pair()
        query = urlencode(
            {
                'client_id': self.oidc_client.id,
                'redirect_uri': 'https://attacker.example.com/callback',
                'response_type': 'code',
                'scope': SCOPE_READ,
                'code_challenge': challenge,
                'code_challenge_method': 'S256',
            }
        )

        response = self.client.get(f'{reverse("idp:oidc:authorization")}?{query}')

        self.assertNotIn('Location', response.headers)
        self.assertTemplateUsed(response, 'idp/oidc/error.html')

    def test_client_cannot_request_a_scope_it_has_not_been_given(self):
        """
        The error goes back to the registered address, the user sees no consent
        """
        self.user_login('test')
        self.oidc_client.set_scopes(['openid', SCOPE_READ])
        self.oidc_client.save()
        _, challenge = generate_pkce_pair()

        response = self.request_authorization(challenge, scope=f'openid {SCOPE_WRITE}')

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['location'].startswith(REDIRECT_URI))
        params = parse_qs(urlparse(response['location']).query)
        self.assertEqual(params['error'], ['invalid_scope'])
        self.assertNotIn('code', params)

    def test_consent_cannot_grant_more_than_was_asked_for(self):
        """
        A tampered consent post cannot widen the scopes beyond the request
        """
        self.user_login('test')
        _, challenge = generate_pkce_pair()

        response = self.request_authorization(challenge, SCOPE_READ)
        response = self.client.post(
            reverse('idp:oidc:authorization'),
            {
                'request': response.context['form']['request'].value(),
                'scopes': [SCOPE_READ, SCOPE_WRITE],
                'action': 'grant',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('scopes', response.context['form'].errors)
        self.assertFalse(Token.objects.exists())

    def test_user_can_grant_less_than_the_application_asked_for(self):
        """
        Unchecking a permission on the consent screen limits the token
        """
        self.user_login('test')
        verifier, challenge = generate_pkce_pair()

        response = self.request_authorization(challenge, f'{SCOPE_READ} {SCOPE_WRITE}')
        response = self.client.post(
            reverse('idp:oidc:authorization'),
            {
                'request': response.context['form']['request'].value(),
                'scopes': [SCOPE_READ],
                'action': 'grant',
            },
        )
        code = parse_qs(urlparse(response['location']).query)['code'][0]
        token = self.redeem_code(code, code_verifier=verifier).json()

        self.assertEqual(token['scope'], SCOPE_READ)

        self.client.logout()
        response = self.client.post(
            reverse('measurement-category-list'),
            data={'name': 'Biceps', 'unit': 'cm'},
            HTTP_AUTHORIZATION=f'Bearer {token["access_token"]}',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)

    def test_consent_form_carries_a_csrf_token(self):
        """
        Without it a third party page could grant itself access in the
        background, using the session of a logged-in user
        """
        csrf_client = TestClient(enforce_csrf_checks=True)
        csrf_client.force_login(User.objects.get(username='test'))
        _, challenge = generate_pkce_pair()
        query = urlencode(
            {
                'client_id': self.oidc_client.id,
                'redirect_uri': REDIRECT_URI,
                'response_type': 'code',
                'scope': SCOPE_READ,
                'code_challenge': challenge,
                'code_challenge_method': 'S256',
            }
        )
        response = csrf_client.get(f'{reverse("idp:oidc:authorization")}?{query}')

        # Read the token out of the consent form itself, not out of the context
        # and not out of some other form on the page, so that this fails if the
        # form ever loses its {% csrf_token %}
        form = re.search(
            rf'<form[^>]*action="{reverse("idp:oidc:authorization")}".*?</form>',
            response.content.decode(),
            re.DOTALL,
        )
        self.assertIsNotNone(form)
        match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', form.group())
        self.assertIsNotNone(match)

        response = csrf_client.post(
            reverse('idp:oidc:authorization'),
            {
                'csrfmiddlewaretoken': match.group(1),
                'request': response.context['form']['request'].value(),
                'scopes': [SCOPE_READ],
                'action': 'grant',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('code', parse_qs(urlparse(response['location']).query))

    def test_code_cannot_be_redeemed_by_another_client(self):
        self.user_login('test')
        other_client = Client(type=Client.Type.PUBLIC, name='Other client')
        other_client.set_redirect_uris([REDIRECT_URI])
        other_client.set_scopes([SCOPE_READ])
        other_client.set_grant_types([Client.GrantType.AUTHORIZATION_CODE])
        other_client.set_response_types([Client.ResponseType.CODE])
        other_client.save()
        verifier, challenge = generate_pkce_pair()

        code = self.grant_authorization(challenge)
        response = self.redeem_code(code, code_verifier=verifier, client_id=other_client.id)

        self.assertEqual(response.status_code, 400)

    def test_client_cannot_use_a_grant_type_it_has_not_been_given(self):
        """
        client_credentials would act without any user behind it
        """
        response = self.client.post(
            reverse('idp:oidc:token'),
            {
                'grant_type': 'client_credentials',
                'client_id': self.oidc_client.id,
                'scope': SCOPE_READ,
            },
        )

        self.assertEqual(response.status_code, 401)
        self.assertNotIn('access_token', response.json())

    def test_refresh_token_grant_issues_a_usable_access_token(self):
        self.user_login('test')
        verifier, challenge = generate_pkce_pair()
        code = self.grant_authorization(challenge)
        refresh_token = self.redeem_code(code, code_verifier=verifier).json()['refresh_token']

        response = self.client.post(
            reverse('idp:oidc:token'),
            {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': self.oidc_client.id,
            },
        )
        self.assertEqual(response.status_code, 200, response.content)

        self.client.logout()
        self.assertEqual(self.read_profile(response.json()['access_token']).status_code, 200)

    def test_revoked_token_stops_working(self):
        self.user_login('test')
        verifier, challenge = generate_pkce_pair()
        code = self.grant_authorization(challenge)
        access_token = self.redeem_code(code, code_verifier=verifier).json()['access_token']
        self.client.logout()

        response = self.client.post(
            reverse('idp:oidc:revoke'),
            {'token': access_token, 'client_id': self.oidc_client.id},
        )
        self.assertEqual(response.status_code, 200, response.content)

        self.assertEqual(self.read_profile(access_token).status_code, 403)

    def create_access_token(
        self,
        scopes: list[str],
        token_type: str = Token.Type.ACCESS_TOKEN,
        expires_in: timedelta = timedelta(hours=1),
    ) -> str:
        """
        Mints a token directly, without running the whole flow
        """
        value = secrets.token_urlsafe(32)
        token = Token(
            type=token_type,
            user=User.objects.get(username='test'),
            client=self.oidc_client,
            hash=get_adapter().hash_token(value),
            expires_at=timezone.now() + expires_in,
        )
        token.set_scopes(scopes)
        token.save()
        return value

    def read_profile(self, token: str):
        return self.client.get(
            reverse('userprofile'),
            HTTP_AUTHORIZATION=f'Bearer {token}',
        )

    def test_expired_token_is_rejected(self):
        token = self.create_access_token([SCOPE_READ], expires_in=-timedelta(seconds=1))

        # The chain falls through to simplejwt, which answers, and
        # SessionAuthentication turns DRF's 401 into a 403
        self.assertIn(self.read_profile(token).status_code, (401, 403))

    def test_refresh_tokens_expire(self):
        """
        Only tokens with an expiry are ever cleaned up
        """
        self.user_login('test')
        verifier, challenge = generate_pkce_pair()
        code = self.grant_authorization(challenge)
        self.redeem_code(code, code_verifier=verifier)

        refresh_token = Token.objects.get(type=Token.Type.REFRESH_TOKEN)

        self.assertIsNotNone(refresh_token.expires_at)

    def test_token_of_a_deactivated_user_is_rejected(self):
        """
        Deactivating an account locks it out immediately, not at token expiry
        """
        token = self.create_access_token([SCOPE_READ])
        User.objects.filter(username='test').update(is_active=False)

        self.assertEqual(self.read_profile(token).status_code, 403)

    def test_refresh_token_is_not_accepted_as_a_bearer(self):
        token = self.create_access_token([SCOPE_READ], token_type=Token.Type.REFRESH_TOKEN)

        self.assertEqual(self.read_profile(token).status_code, 403)

    def test_read_scope_allows_reading(self):
        token = self.create_access_token([SCOPE_READ])

        response = self.client.get(
            reverse('userprofile'),
            HTTP_AUTHORIZATION=f'Bearer {token}',
        )

        self.assertEqual(response.status_code, 200)

    def test_read_scope_does_not_allow_writing(self):
        token = self.create_access_token([SCOPE_READ])

        response = self.client.post(
            reverse('measurement-category-list'),
            data={'name': 'Biceps', 'unit': 'cm'},
            HTTP_AUTHORIZATION=f'Bearer {token}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 403)
        self.assertIn(SCOPE_WRITE, response.json()['detail'])

    def test_write_scope_allows_writing(self):
        token = self.create_access_token([SCOPE_READ, SCOPE_WRITE])

        response = self.client.post(
            reverse('measurement-category-list'),
            data={'name': 'Biceps', 'unit': 'cm'},
            HTTP_AUTHORIZATION=f'Bearer {token}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)

    @override_settings(IDP_OIDC_PRIVATE_KEY='')
    def test_tokens_stop_working_without_a_signing_key(self):
        """
        No key means the provider is off, tokens it handed out are not accepted
        """
        token = self.create_access_token([SCOPE_READ])

        response = self.client.get(
            reverse('userprofile'),
            HTTP_AUTHORIZATION=f'Bearer {token}',
        )

        self.assertEqual(response.status_code, 403)

    @override_settings(IDP_OIDC_PRIVATE_KEY='')
    def test_the_flow_does_not_start_without_a_signing_key(self):
        """
        Otherwise users would consent to something that cannot be completed
        """
        self.user_login('test')
        _, challenge = generate_pkce_pair()

        response = self.request_authorization(challenge)

        self.assertEqual(response.status_code, 404)

    def test_identity_scopes_alone_grant_no_api_access(self):
        """
        openid and friends identify the user, they don't open the API
        """
        token = self.create_access_token(['openid', 'profile', 'email'])

        response = self.client.get(
            reverse('userprofile'),
            HTTP_AUTHORIZATION=f'Bearer {token}',
        )

        self.assertEqual(response.status_code, 403)

    def test_scopes_are_advertised(self):
        response = self.client.get(reverse('idp:oidc:configuration'))

        self.assertEqual(
            response.json()['scopes_supported'],
            [SCOPE_READ, SCOPE_WRITE, 'email', 'openid', 'profile'],
        )

    def test_flush_expired_oidc_tokens_task(self):
        """
        The periodic cleanup task deletes expired tokens and keeps valid ones
        """
        user = User.objects.get(username='test')
        expired = Token.objects.create(
            type=Token.Type.ACCESS_TOKEN,
            client=self.oidc_client,
            user=user,
            hash='expired',
            expires_at=timezone.now() - timedelta(days=1),
        )
        valid = Token.objects.create(
            type=Token.Type.ACCESS_TOKEN,
            client=self.oidc_client,
            user=user,
            hash='valid',
            expires_at=timezone.now() + timedelta(days=1),
        )

        flush_expired_oidc_tokens_task()

        self.assertFalse(Token.objects.filter(pk=expired.pk).exists())
        self.assertTrue(Token.objects.filter(pk=valid.pk).exists())

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

    def test_consent_is_only_reached_after_passing_mfa(self):
        """
        The browser flow runs through the regular login, two-factor included
        """
        user = User.objects.get(username='test')
        secret = generate_totp_secret()
        TOTP.activate(user, secret)
        _, challenge = generate_pkce_pair()

        response = self.request_authorization(challenge)
        self.assertEqual(response.status_code, 302)
        # LOGIN_URL carries no language prefix, posting to it would only yield
        # the redirect that adds one
        next_url = parse_qs(urlparse(response['location']).query)['next'][0]

        # Username and password alone stop at the second factor
        response = self.client.post(
            reverse('core:user:login'),
            {'login': 'test', 'password': 'testtest', 'next': next_url},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['location'].startswith(reverse('mfa_authenticate')))

        counters = list(yield_hotp_counters_from_time())
        code = format_hotp_value(hotp_value(secret, counters[len(counters) // 2]))
        response = self.client.post(response['location'], {'code': code}, follow=True)

        self.assertTemplateUsed(response, 'idp/oidc/authorization_form.html')

    def test_anonymous_authorization_redirects_to_login(self):
        _, challenge = generate_pkce_pair()

        response = self.request_authorization(challenge)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['location'].startswith(f'{settings.LOGIN_URL}?next='))
