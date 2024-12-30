# Standard Library
from unittest import mock

# Third Party
from rest_framework import status
from rest_framework.exceptions import ErrorDetail

# wger
from wger.core.tests.api_base_test import ApiBaseTestCase
from wger.core.tests.base_testcase import (
    BaseTestCase,
    WgerTestCase,
)
from wger.core.views.user import trainer_login


def _build_mock_request(user):
    request = mock.Mock()
    request.session = dict()
    request.GET = dict()
    request.user = user
    return request


def _build_mock_user(gym_name, is_trainer=False):
    user = mock.Mock()
    user.userprofile.gym = gym_name

    def request_has_perm(perm):
        if perm in ['gym.gym_trainer', 'gym.manage_gym', 'gym.manage_gyms']:
            return is_trainer
        return True  # Don't care about other permissions for these tests

    user.has_perm.side_effect = request_has_perm
    return user


@mock.patch('wger.core.views.user.django_login')
class TrainerLoginTestCase(WgerTestCase):
    def test_trainer_is_allowed_to_login_to_non_trainer_in_same_gym(self, _):
        request_user = _build_mock_user('same-gym', is_trainer=True)
        request = _build_mock_request(request_user)
        user_from_db_lookup = _build_mock_user('same-gym', is_trainer=False)

        with mock.patch('wger.core.views.user.get_object_or_404', return_value=user_from_db_lookup):
            resp = trainer_login(request, 'primary-key-not-needed-because-get-object-is-mocked')

        self.assertEqual(302, resp.status_code)

    def test_trainer_is_denied_from_login_to_trainer_in_same_gym(self, _):
        request_user = _build_mock_user('same-gym', is_trainer=True)
        request = _build_mock_request(request_user)
        user_from_db_lookup = _build_mock_user('same-gym', is_trainer=True)

        with mock.patch('wger.core.views.user.get_object_or_404', return_value=user_from_db_lookup):
            resp = trainer_login(request, 'primary-key-not-needed-because-of-mock')

        self.assertEqual(403, resp.status_code)

    def test_trainer_is_denied_from_login_to_trainer_at_different_gym(self, _):
        request_user = _build_mock_user('trainer-gym', is_trainer=True)
        request = _build_mock_request(request_user)
        user_from_db_lookup = _build_mock_user('other-trainer-gym', is_trainer=True)

        with mock.patch('wger.core.views.user.get_object_or_404', return_value=user_from_db_lookup):
            resp = trainer_login(request, 'primary-key-not-needed-because-of-mock')

        self.assertEqual(403, resp.status_code)

    def test_trainer_gets_404_when_trying_to_login_to_non_trainer_in_different_gym(self, _):
        request_user = _build_mock_user('trainer-gym', is_trainer=True)
        request = _build_mock_request(request_user)
        user_from_db_lookup = _build_mock_user('user-gym', is_trainer=False)

        with mock.patch('wger.core.views.user.get_object_or_404', return_value=user_from_db_lookup):
            resp = trainer_login(request, 'primary-key-not-needed-because-of-mock')

        self.assertEqual(404, resp.status_code)


class UserApiLoginApiTestCase(BaseTestCase, ApiBaseTestCase):
    url = '/api/v2/login/'

    def test_access_logged_out(self):
        """
        Logged-out users are also allowed to use the search
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_username_success(self):
        response = self.client.post(
            self.url,
            {'username': 'admin', 'password': 'adminadmin'},
        )
        result = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result, {'token': 'apikey-admin'})

    def test_login_username_fail(self):
        response = self.client.post(self.url, {'username': 'admin', 'password': 'adminadmin123'})
        result = response.data

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            result['non_field_errors'],
            [ErrorDetail(string='Username or password unknown', code='invalid')],
        )

    def test_login_email_success(self):
        response = self.client.post(
            self.url,
            {'email': 'admin@example.com', 'password': 'adminadmin'},
        )
        result = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result, {'token': 'apikey-admin'})

    def test_login_email_fail(self):
        response = self.client.post(
            self.url, {'email': 'admin@example.com', 'password': 'adminadmin123'}
        )
        result = response.data

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            result['non_field_errors'],
            [ErrorDetail(string='Username or password unknown', code='invalid')],
        )

    def test_no_parameters(self):
        response = self.client.post(self.url, {'foo': 'bar', 'password': 'adminadmin123'})
        result = response.data

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            result['non_field_errors'],
            [ErrorDetail(string='Please provide an "email" or a "username"', code='invalid')],
        )
