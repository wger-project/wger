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

# Django
from django.urls import reverse
from django.utils import timezone

# Third Party
from rest_framework import status

# wger
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.models import WorkoutSession


class WorkoutSessionApiTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the workout overview resource
    """

    pk = 'bbbbbbbb-bbbb-bbbb-bbbb-000000000005'
    resource = WorkoutSession
    private_resource = True
    data = {
        'routine': 3,
        'notes': 'My new insights',
        'impression': '3',
        'datetime_start': timezone.make_aware(datetime.datetime(2014, 1, 25, 10, 0)),
        'datetime_end': timezone.make_aware(datetime.datetime(2014, 1, 25, 13, 0)),
    }


class WorkoutSessionLegacyFieldsTestCase(WgerTestCase):
    """
    Test the deprecated date/time_start/time_end fields of the session API
    """

    SESSION = 'bbbbbbbb-bbbb-bbbb-bbbb-000000000005'
    ROUTINE = 3

    def setUp(self):
        super().setUp()
        self.user_login('test')

    def test_read_derives_the_deprecated_triple(self):
        """The deprecated fields are derived from the new ones, in local time"""

        session = WorkoutSession.objects.get(pk=self.SESSION)
        start = timezone.localtime(session.datetime_start)
        end = timezone.localtime(session.datetime_end)

        response = self.client.get(reverse('workoutsession-detail', kwargs={'pk': self.SESSION}))

        self.assertEqual(response.json()['date'], start.date().isoformat())
        self.assertEqual(response.json()['time_start'], start.time().isoformat())
        self.assertEqual(response.json()['time_end'], end.time().isoformat())

    def test_create_with_the_deprecated_triple(self):
        """The deprecated fields are composed into datetime_start/datetime_end"""

        response = self.client.post(
            reverse('workoutsession-list'),
            data={
                'routine': self.ROUTINE,
                'impression': '2',
                'date': '2025-03-12',
                'time_start': '10:00',
                'time_end': '11:30',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        session = WorkoutSession.objects.get(pk=response.json()['id'])
        self.assertEqual(
            session.datetime_start,
            timezone.make_aware(datetime.datetime(2025, 3, 12, 10, 0)),
        )
        self.assertEqual(
            session.datetime_end,
            timezone.make_aware(datetime.datetime(2025, 3, 12, 11, 30)),
        )

    def test_create_over_midnight_ends_on_the_next_day(self):
        """An end time before the start time means the session ended the day after"""

        response = self.client.post(
            reverse('workoutsession-list'),
            data={
                'routine': self.ROUTINE,
                'impression': '2',
                'date': '2025-03-10',
                'time_start': '23:00',
                'time_end': '01:30',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        session = WorkoutSession.objects.get(pk=response.json()['id'])
        self.assertEqual(
            session.datetime_start,
            timezone.make_aware(datetime.datetime(2025, 3, 10, 23, 0)),
        )
        self.assertEqual(
            session.datetime_end,
            timezone.make_aware(datetime.datetime(2025, 3, 11, 1, 30)),
        )

    def test_create_without_a_start_time_starts_at_midnight(self):
        """A session without times covers the day it was logged on"""

        response = self.client.post(
            reverse('workoutsession-list'),
            data={'routine': self.ROUTINE, 'impression': '2', 'date': '2025-03-12'},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        session = WorkoutSession.objects.get(pk=response.json()['id'])
        self.assertEqual(
            session.datetime_start,
            timezone.make_aware(datetime.datetime(2025, 3, 12, 0, 0)),
        )
        self.assertIsNone(session.datetime_end)

    def test_patch_time_end_keeps_day_and_start(self):
        """Closing a session takes the day and start time from the stored session"""

        session = WorkoutSession.objects.get(pk=self.SESSION)
        start = session.datetime_start

        response = self.client.patch(
            reverse('workoutsession-detail', kwargs={'pk': self.SESSION}),
            data={'time_end': '12:30'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        session.refresh_from_db()
        self.assertEqual(session.datetime_start, start)
        self.assertEqual(
            timezone.localtime(session.datetime_end),
            timezone.make_aware(
                datetime.datetime.combine(
                    timezone.localtime(start).date(),
                    datetime.time(12, 30),
                )
            ),
        )

    def test_the_new_fields_win(self):
        """A request that sends both formats is not overwritten by the deprecated one"""

        response = self.client.post(
            reverse('workoutsession-list'),
            data={
                'routine': self.ROUTINE,
                'impression': '2',
                'date': '2020-01-01',
                'time_start': '08:00',
                'datetime_start': '2025-03-12T10:00:00Z',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        session = WorkoutSession.objects.get(pk=response.json()['id'])
        self.assertEqual(
            session.datetime_start,
            datetime.datetime(2025, 3, 12, 10, 0, tzinfo=datetime.timezone.utc),
        )

    def test_filter_by_date(self):
        """The deprecated date filter matches on the local day of datetime_start"""

        session = WorkoutSession.objects.get(pk=self.SESSION)
        day = timezone.localtime(session.datetime_start).date()

        response = self.client.get(reverse('workoutsession-list'), {'date': day.isoformat()})
        self.assertEqual([entry['id'] for entry in response.json()['results']], [self.SESSION])

        response = self.client.get(
            reverse('workoutsession-list'),
            {'date': (day + datetime.timedelta(days=1)).isoformat()},
        )
        self.assertEqual(response.json()['results'], [])

    def test_untouched_when_no_deprecated_field_is_sent(self):
        """A request without the deprecated fields leaves the timestamps alone"""

        session = WorkoutSession.objects.get(pk=self.SESSION)

        response = self.client.patch(
            reverse('workoutsession-detail', kwargs={'pk': self.SESSION}),
            data={'notes': 'Only the notes change'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        session.refresh_from_db()
        self.assertEqual(session.notes, 'Only the notes change')
        self.assertEqual(
            session.datetime_start,
            datetime.datetime(2025, 11, 1, 10, 0, tzinfo=datetime.timezone.utc),
        )
        self.assertEqual(
            session.datetime_end,
            datetime.datetime(2025, 11, 1, 10, 15, tzinfo=datetime.timezone.utc),
        )
