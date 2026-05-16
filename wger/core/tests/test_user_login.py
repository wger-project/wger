# Standard Library
from unittest import mock

# Django
from django.contrib.auth.models import User
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.core.views.user import trainer_login


def _build_mock_request(user):
    request = mock.Mock()
    request.session = dict()
    request.GET = dict()
    request.POST = dict()
    request.method = 'POST'
    request.user = user
    return request


def _build_mock_user(gym_name, is_trainer=False):
    user = mock.Mock()
    user.userprofile.gym = gym_name
    user.userprofile.gym_id = gym_name

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


class WebLoginViewTestCase(WgerTestCase):
    """
    The web login view (core:user:login) is allauth's LoginView, with one wger
    carve-out: temporary (guest) users may still reach the login page.
    """

    def test_login_page_renders(self):
        response = self.client.get(reverse('core:user:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')

    def test_login_via_view_succeeds(self):
        response = self.client.post(
            reverse('core:user:login'),
            {'login': 'test', 'password': 'testtest'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), 2)

    def test_authenticated_user_is_redirected_away(self):
        self.user_login('test')
        response = self.client.get(reverse('core:user:login'))
        self.assertEqual(response.status_code, 302)

    def test_temporary_user_can_reach_login_page(self):
        user = User.objects.get(username='test')
        user.userprofile.is_temporary = True
        user.userprofile.save()
        self.user_login('test')

        response = self.client.get(reverse('core:user:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_shows_passkey_button(self):
        """
        With MFA_PASSKEY_LOGIN_ENABLED the login page offers passwordless
        sign-in via a passkey.
        """
        response = self.client.get(reverse('core:user:login'))
        self.assertContains(response, 'id="passkey_login"')
