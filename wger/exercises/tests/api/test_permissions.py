# Standard Library
from unittest import mock

# Django
from django.test import SimpleTestCase

# wger
from wger.exercises.api.permissions import CanContributeExercises


def build_request(method: str, *, is_authenticated: bool, trustworthy: bool = False, perms=()):
    request = mock.Mock()
    request.method = method
    request.user.is_authenticated = is_authenticated
    request.user.userprofile.is_trustworthy = trustworthy
    request.user.has_perm.side_effect = lambda perm: perm in perms
    return request


class CanContributeExercisesTestCase(SimpleTestCase):
    def setUp(self):
        self.permission = CanContributeExercises()

    def test_post_requires_add_permission(self):
        request = build_request(
            'POST',
            is_authenticated=True,
            perms={'exercises.change_exercise'},
        )

        self.assertFalse(self.permission.has_permission(request, None))

    def test_patch_accepts_change_permission(self):
        request = build_request(
            'PATCH',
            is_authenticated=True,
            perms={'exercises.change_exercise'},
        )

        self.assertTrue(self.permission.has_permission(request, None))

    def test_patch_rejects_user_without_change_permission(self):
        request = build_request('PATCH', is_authenticated=True)

        self.assertFalse(self.permission.has_permission(request, None))
