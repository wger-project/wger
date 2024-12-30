# Standard Library
from io import StringIO

# Django
from django.contrib.auth.models import User
from django.core.management import call_command
from django.urls import reverse

# Third Party
from rest_framework.authtoken.models import Token
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
)

# wger
from wger.core.tests.base_testcase import WgerTestCase


class CreateUserCommand(WgerTestCase):
    def setUp(self):
        super(CreateUserCommand, self).setUp()
        self.out = StringIO()

    def test_access_api_user_creation(self):
        """Tests giving permission to register users via API"""

        user = User.objects.get(username='admin')
        self.assertFalse(user.userprofile.can_add_user)

        call_command('add-user-rest', 'admin', stdout=self.out, no_color=True)
        self.assertEqual('admin is now ALLOWED to add users via the API\n', self.out.getvalue())

        user = User.objects.get(username='admin')
        self.assertTrue(user.userprofile.can_add_user)

    def test_revoke_access_api_user_creation(self):
        """Tests revoking permission to register users via API"""

        user = User.objects.get(username='test')
        self.assertTrue(user.userprofile.can_add_user)

        call_command('add-user-rest', 'test', disable=True, stdout=self.out, no_color=True)
        self.assertEqual(
            'test is now DISABLED from adding users via the API\n',
            self.out.getvalue(),
        )

        user = User.objects.get(username='test')
        self.assertFalse(user.userprofile.can_add_user)

    def test_access_get_api_users(self):
        """Tests listing created users via API"""

        call_command('list-users-api', stdout=self.out, no_color=True)
        self.assertIn('Users created by test:', self.out.getvalue())
        self.assertIn('- trainer1', self.out.getvalue())
        self.assertIn('- trainer2', self.out.getvalue())

    def test_post_valid_api_user_creation(self):
        """Successfully register a user via the REST API"""

        self.user_login('test')
        user = User.objects.get(username='test')
        token = Token.objects.get(user=user)
        count_before = User.objects.count()

        response = self.client.post(
            reverse('api_register'),
            {'username': 'restapi', 'email': 'abc@cde.fg', 'password': 'AekaiLe0ga'},
        )
        count_after = User.objects.count()
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        new_user = User.objects.get(username='restapi')
        token = Token.objects.get(user=new_user)
        self.assertEqual(response.data['message'], 'api user successfully registered')
        self.assertEqual(response.data['token'], token.key)
        self.assertEqual(count_after, count_before + 1)

    def test_post_valid_api_user_creation_no_email(self):
        """Successfully register a user via the REST API without providing an email"""

        self.user_login('test')
        user = User.objects.get(username='test')
        token = Token.objects.get(user=user)
        count_before = User.objects.count()

        response = self.client.post(
            reverse('api_register'),
            {'username': 'restapi', 'password': 'AekaiLe0ga'},
        )
        count_after = User.objects.count()
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        new_user = User.objects.get(username='restapi')
        token = Token.objects.get(user=new_user)
        self.assertEqual(response.data['message'], 'api user successfully registered')
        self.assertEqual(response.data['token'], token.key)
        self.assertEqual(count_after, count_before + 1)

    def test_post_unsuccessfully_registration_no_username(self):
        """Test unsuccessful registration (weak password)"""

        self.user_login('test')
        user = User.objects.get(username='test')
        token = Token.objects.get(user=user)

        response = self.client.post(
            reverse('api_register'),
            {'password': 'AekaiLe0ga'},
        )

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_post_unsuccessfully_registration_invalid_email(self):
        """Test unsuccessful registration (invalid email)"""

        self.user_login('test')
        user = User.objects.get(username='test')
        token = Token.objects.get(user=user)

        response = self.client.post(
            reverse('api_register'),
            {'username': 'restapi', 'email': 'example.com', 'password': 'AekaiLe0ga'},
        )

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_post_unsuccessfully_registration_invalid_email_2(self):
        """Test unsuccessful registration (email already exists)"""

        self.user_login('test')
        user = User.objects.get(username='test')
        token = Token.objects.get(user=user)

        response = self.client.post(
            reverse('api_register'),
            {'username': 'restapi', 'email': 'admin@example.com', 'password': 'AekaiLe0ga'},
        )

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
