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
import datetime

# Django
from django.urls import reverse

# Third Party
from rest_framework import status

# wger
from wger.core.tests.api_base_test import ApiBaseTestCase
from wger.core.tests.base_testcase import BaseTestCase
from wger.manager.models import (
    Routine,
    SetsConfig,
    Slot,
    SlotEntry,
)


URL_NAMES = (
    'routine-date-sequence-display-mode',
    'routine-date-sequence-gym-mode',
    'routine-structure',
)


class RoutineDetailEndpointsApiTestCase(BaseTestCase, ApiBaseTestCase):
    """
    Tests the detail endpoints used by the mobile and web apps

    Routine 1 belongs to admin, has three days and is not public.
    """

    def test_anonymous(self):
        for url_name in URL_NAMES:
            response = self.client.get(reverse(url_name, kwargs={'pk': 1}))
            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
                f'{url_name} did not return 403 for anonymous users',
            )

    def test_other_user(self):
        self.authenticate('test')
        for url_name in URL_NAMES:
            response = self.client.get(reverse(url_name, kwargs={'pk': 1}))
            self.assertEqual(
                response.status_code,
                status.HTTP_404_NOT_FOUND,
                f'{url_name} leaked a foreign routine',
            )

    def test_date_sequence_display(self):
        self.authenticate('admin')
        response = self.client.get(reverse('routine-date-sequence-display-mode', kwargs={'pk': 1}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data)

        first_day = data[0]
        self.assertIn('iteration', first_day)
        self.assertIn('date', first_day)
        self.assertIn('day', first_day)
        self.assertIn('slots', first_day)

    def test_date_sequence_gym(self):
        self.authenticate('admin')
        response = self.client.get(reverse('routine-date-sequence-gym-mode', kwargs={'pk': 1}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data)
        self.assertIn('day', data[0])

    def test_structure(self):
        self.authenticate('admin')
        response = self.client.get(reverse('routine-structure', kwargs={'pk': 1}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['id'], 1)
        self.assertEqual(len(data['days']), 3)
        self.assertTrue(any(day['slots'] for day in data['days']))


class RoutineCopyEndpointApiTestCase(BaseTestCase, ApiBaseTestCase):
    """
    Tests the endpoint that copies a routine

    Routine 1 belongs to admin and has three days, routine 3 belongs to the
    user "test" and has no days. Neither of them is a template.
    """

    def copy_url(self, pk: int = 1) -> str:
        return reverse('routine-copy', kwargs={'pk': pk})

    def test_anonymous(self):
        count = Routine.objects.count()
        response = self.client.post(self.copy_url())

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Routine.objects.count(), count)

    def test_wrong_method(self):
        self.authenticate('admin')
        response = self.client.get(self.copy_url())

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_copy_own_routine(self):
        original = Routine.objects.get(pk=1)
        self.assertTrue(original.days.count())
        self.assertTrue(SetsConfig.objects.filter(slot_entry__slot__day__routine=original).exists())
        count = Routine.objects.count()

        self.authenticate('admin')
        response = self.client.post(self.copy_url())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Routine.objects.count(), count + 1)

        data = response.json()
        self.assertNotEqual(data['id'], original.pk)
        self.assertEqual(data['name'], original.name)
        self.assertEqual(data['description'], original.description)
        self.assertEqual(data['start'], str(datetime.date.today()))
        self.assertEqual(data['end'], str(datetime.date.today() + original.duration))
        self.assertFalse(data['is_template'])
        self.assertFalse(data['is_public'])

        routine_copy = Routine.objects.get(pk=data['id'])
        self.assertEqual(routine_copy.user.username, 'admin')
        self.assertEqual(routine_copy.days.count(), original.days.count())
        self.assertEqual(
            Slot.objects.filter(day__routine=routine_copy).count(),
            Slot.objects.filter(day__routine=original).count(),
        )
        self.assertEqual(
            SlotEntry.objects.filter(slot__day__routine=routine_copy).count(),
            SlotEntry.objects.filter(slot__day__routine=original).count(),
        )
        self.assertEqual(
            SetsConfig.objects.filter(slot_entry__slot__day__routine=routine_copy).count(),
            SetsConfig.objects.filter(slot_entry__slot__day__routine=original).count(),
        )

        # The original is not touched
        original.refresh_from_db()
        self.assertEqual(original.user.username, 'admin')
        self.assertEqual(original.days.count(), routine_copy.days.count())

    def test_copy_other_private_routine(self):
        count = Routine.objects.count()

        self.authenticate('test')
        response = self.client.post(self.copy_url(1))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Routine.objects.count(), count)

    def test_copy_other_template_not_public(self):
        Routine.objects.filter(pk=1).update(is_template=True, is_public=False)
        count = Routine.objects.count()

        self.authenticate('test')
        response = self.client.post(self.copy_url(1))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Routine.objects.count(), count)

    def test_copy_public_template(self):
        Routine.objects.filter(pk=1).update(is_template=True, is_public=True)
        count = Routine.objects.count()

        self.authenticate('test')
        response = self.client.post(self.copy_url(1))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Routine.objects.count(), count + 1)

        routine_copy = Routine.objects.get(pk=response.json()['id'])
        self.assertEqual(routine_copy.user.username, 'test')
        self.assertFalse(routine_copy.is_template)
        self.assertFalse(routine_copy.is_public)
        self.assertEqual(routine_copy.days.count(), 3)

        # The template stays as it was
        template = Routine.objects.get(pk=1)
        self.assertEqual(template.user.username, 'admin')
        self.assertTrue(template.is_template)
        self.assertTrue(template.is_public)

    def test_copy_public_template_cannot_be_modified(self):
        """Being allowed to copy a public template does not allow changing it"""
        Routine.objects.filter(pk=1).update(is_template=True, is_public=True)

        self.authenticate('test')
        response = self.client.patch(
            reverse('routine-detail', kwargs={'pk': 1}),
            {'name': 'changed'},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(Routine.objects.get(pk=1).name, 'changed')
