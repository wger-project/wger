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

# Standard Library
import datetime
import logging

# Django
from django.urls import reverse

# wger
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.models import WorkoutLog


logger = logging.getLogger(__name__)


class WorkoutLogApiTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the workout log overview resource
    """

    # WorkoutLog has a UUIDField PK. Test fixtures use a recognisable
    # `aaaaaaaa-...-NNN` pattern so test UUIDs stand out from real data.
    pk = 'aaaaaaaa-aaaa-aaaa-aaaa-000000000005'
    resource = WorkoutLog
    private_resource = True
    data = {
        'exercise': 1,
        'routine': 3,
        'repetitions': 3,
        'repetitions_unit': 1,
        'weight_unit': 2,
        'weight': 2,
        'date': datetime.date.today(),
    }


class WorkoutLogValidationApiTestCase(WgerTestCase):
    """
    Tests that the model validation of a log answers with a 400
    """

    pk = 'aaaaaaaa-aaaa-aaaa-aaaa-000000000005'

    def setUp(self):
        super().setUp()
        self.user_login('test')

    def test_patch_weight_onto_log_without_weight_unit(self):
        WorkoutLog.objects.filter(pk=self.pk).update(weight=None, weight_unit=None)

        response = self.client.patch(
            reverse('workoutlog-detail', kwargs={'pk': self.pk}),
            data={'weight': 82.5},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIsNone(WorkoutLog.objects.get(pk=self.pk).weight)

    def test_patch_keeps_values_of_the_stored_log(self):
        response = self.client.patch(
            reverse('workoutlog-detail', kwargs={'pk': self.pk}),
            data={'weight': 82.5},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200, response.content)

    def test_create_with_weight_but_without_weight_unit(self):
        response = self.client.post(
            reverse('workoutlog-list'),
            data={
                'exercise': 1,
                'routine': 3,
                'repetitions': 3,
                'weight': 20,
                'weight_unit': None,
                'date': datetime.date.today().isoformat(),
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
