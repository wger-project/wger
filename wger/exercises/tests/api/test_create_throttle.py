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
from unittest import mock

# Django
from django.urls import reverse

# Third Party
from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.test import APIRequestFactory

# wger
from wger.core.tests.api_base_test import ApiBaseTestCase
from wger.core.tests.base_testcase import BaseTestCase
from wger.exercises.api.throttling import CreateScopedRateThrottle
from wger.exercises.api.views import (
    ExerciseSubmissionViewSet,
    ExerciseTranslationViewSet,
    ExerciseViewSet,
)


class ExerciseCreateThrottleTestCase(BaseTestCase, ApiBaseTestCase):
    """
    Tests the write-only create throttle shared by the exercise create endpoints.
    """

    @staticmethod
    def get_payload():
        return {
            'category': 3,
            'license': 5,
            'license_author': 'tester',
            'translations': [
                {
                    'name': 'Throttle Test Exercise',
                    'description_source': (
                        'A sufficiently long English description so the language '
                        'detector recognises it and the minimum length passes.'
                    ),
                    'language': 2,
                    'license_author': 'tester',
                },
            ],
        }

    def test_create_endpoints_use_throttle_scope(self):
        """All create endpoints share the throttle scope and class."""
        for view in (ExerciseViewSet, ExerciseTranslationViewSet, ExerciseSubmissionViewSet):
            self.assertEqual(view.throttle_scope, 'exercise_create')
            self.assertIn(CreateScopedRateThrottle, view.throttle_classes)

    def test_throttle_skips_non_post_requests(self):
        """Only POST is throttled; reads and edits always pass through."""
        throttle = CreateScopedRateThrottle()
        factory = APIRequestFactory()
        view = ExerciseViewSet()
        view.throttle_scope = 'exercise_create'

        for method in ('get', 'put', 'patch', 'delete', 'options', 'head'):
            request = getattr(factory, method)('/api/v2/exercise/')
            self.assertTrue(throttle.allow_request(request, view))

    def test_post_is_throttled(self):
        """A second create within the window is rejected with 429."""
        url = reverse('exercise-submission')
        # trainer1 is a trustworthy contributor without the add_exercise
        # permission, so the throttle applies to them.
        self.authenticate('trainer1')

        with mock.patch.dict(api_settings.DEFAULT_THROTTLE_RATES, {'exercise_create': '1/min'}):
            first = self.client.post(url, data=self.get_payload())
            second = self.client.post(url, data=self.get_payload())

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_add_exercise_permission_is_exempt(self):
        """Users with the add_exercise permission (admins/editors) aren't throttled."""
        url = reverse('exercise-submission')
        self.authenticate('admin')

        with mock.patch.dict(api_settings.DEFAULT_THROTTLE_RATES, {'exercise_create': '1/min'}):
            first = self.client.post(url, data=self.get_payload())
            second = self.client.post(url, data=self.get_payload())

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_201_CREATED)
