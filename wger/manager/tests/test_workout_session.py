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
import zoneinfo

# Django
from django.contrib.auth.models import User
from django.db import (
    IntegrityError,
    transaction,
)
from django.test import override_settings
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


class WorkoutSessionDurationTestCase(WgerTestCase):
    """
    Test the maximum session length
    """

    SESSION = 'bbbbbbbb-bbbb-bbbb-bbbb-000000000005'
    ROUTINE = 3

    def setUp(self):
        super().setUp()
        self.user_login('test')

    def create_session(self, hours):
        return self.client.post(
            reverse('workoutsession-list'),
            data={
                'routine': self.ROUTINE,
                'impression': '2',
                'datetime_start': '2025-03-12T10:00:00Z',
                'datetime_end': f'2025-03-12T{10 + hours}:00:00Z',
            },
            content_type='application/json',
        )

    def test_session_within_the_limit(self):
        self.assertEqual(self.create_session(4).status_code, status.HTTP_201_CREATED)

    def test_session_over_the_limit_is_rejected(self):
        response = self.create_session(6)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('5 hours', response.json()['datetime_end'][0])

    @override_settings(WGER_MAX_SESSION_LENGTH_HOURS=8)
    def test_the_limit_is_configurable(self):
        self.assertEqual(self.create_session(6).status_code, status.HTTP_201_CREATED)

    def stretch_session(self):
        """Make the fixture session longer than the limit, bypassing the validation"""

        session = WorkoutSession.objects.get(pk=self.SESSION)
        WorkoutSession.objects.filter(pk=self.SESSION).update(
            datetime_end=session.datetime_start + datetime.timedelta(hours=8)
        )

    def test_session_over_the_limit_stays_editable(self):
        """Sessions from before the limit can still be edited as long as it stays untouched"""

        self.stretch_session()
        url = reverse('workoutsession-detail', kwargs={'pk': self.SESSION})
        stored = self.client.get(url).json()

        response = self.client.patch(
            url,
            data={
                'notes': 'Still editable',
                'datetime_start': stored['datetime_start'],
                'datetime_end': stored['datetime_end'],
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(WorkoutSession.objects.get(pk=self.SESSION).notes, 'Still editable')

    def test_stretching_a_session_further_is_rejected(self):
        """Editing the times of such a session does run into the limit"""

        self.stretch_session()

        response = self.client.patch(
            reverse('workoutsession-detail', kwargs={'pk': self.SESSION}),
            data={'time_end': '23:00'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class WorkoutSessionLocalDayTestCase(WgerTestCase):
    """
    Test in whose timezone the day of a session is derived
    """

    MEMBER1 = 14
    """Fixture user with time_zone Pacific/Auckland"""

    TEST_USER = 2
    """Fixture user without a reported zone"""

    @staticmethod
    def session_at(user_id, start):
        return WorkoutSession.objects.create(
            user_id=user_id,
            datetime_start=start,
        )

    def test_east_of_the_server_the_day_is_the_next_one(self):
        """14:00 UTC is already the following day in Auckland"""

        session = self.session_at(
            self.MEMBER1,
            datetime.datetime(2024, 6, 19, 14, 0, tzinfo=datetime.timezone.utc),
        )

        self.assertEqual(session.local_day, datetime.date(2024, 6, 20))

    def test_west_of_the_server_the_day_is_the_previous_one(self):
        """01:30 UTC is still the previous evening in Denver"""

        profile = User.objects.get(pk=self.TEST_USER).userprofile
        profile.time_zone = 'America/Denver'
        profile.save()

        session = self.session_at(
            self.TEST_USER,
            datetime.datetime(2024, 6, 19, 1, 30, tzinfo=datetime.timezone.utc),
        )

        self.assertEqual(session.local_day, datetime.date(2024, 6, 18))

    def test_the_viewers_zone_does_not_leak_in(self):
        """The day belongs to the session's user, not to whoever is asking"""

        session = self.session_at(
            self.MEMBER1,
            datetime.datetime(2024, 6, 19, 14, 0, tzinfo=datetime.timezone.utc),
        )

        with timezone.override(zoneinfo.ZoneInfo('America/Denver')):
            self.assertEqual(session.local_day, datetime.date(2024, 6, 20))

    def test_without_a_zone_the_instance_zone_decides(self):
        """23:30 UTC is the next day in Europe/Berlin, the instance zone"""

        session = self.session_at(
            self.TEST_USER,
            datetime.datetime(2024, 6, 19, 23, 30, tzinfo=datetime.timezone.utc),
        )

        self.assertEqual(session.local_day, datetime.date(2024, 6, 20))


class WorkoutSessionIntervalConstraintTestCase(WgerTestCase):
    """
    Test the database constraint on the session interval
    """

    START = timezone.make_aware(datetime.datetime(2025, 3, 10, 18, 0))

    def test_an_end_before_the_start_is_rejected(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            WorkoutSession.objects.create(
                user_id=1,
                datetime_start=self.START,
                datetime_end=self.START - datetime.timedelta(hours=1),
            )

    def test_a_session_without_an_end_is_allowed(self):
        session = WorkoutSession.objects.create(user_id=1, datetime_start=self.START)

        self.assertIsNone(session.datetime_end)


class WorkoutSessionLegacyFieldsTestCase(WgerTestCase):
    """
    Test that writes in the pre-2.7 shape still arrive
    """

    SESSION = 'bbbbbbbb-bbbb-bbbb-bbbb-000000000005'
    ROUTINE = 3

    def setUp(self):
        super().setUp()
        self.user_login('test')

    def test_the_deprecated_fields_are_not_returned(self):
        """They are accepted on write, but they are not part of the response"""

        response = self.client.get(reverse('workoutsession-detail', kwargs={'pk': self.SESSION}))

        self.assertNotIn('date', response.json())
        self.assertNotIn('time_start', response.json())
        self.assertNotIn('time_end', response.json())

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
            content_type='application/json',
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

    def test_the_triple_is_composed_in_the_owners_timezone(self):
        """A queued 07:00 is the owner's 07:00, not the zone the request runs in"""

        profile = User.objects.get(username='test').userprofile
        profile.time_zone = 'Pacific/Auckland'
        profile.save()

        response = self.client.post(
            reverse('workoutsession-list'),
            data={
                'routine': self.ROUTINE,
                'impression': '2',
                'date': '2025-03-12',
                'time_start': '07:00',
            },
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        session = WorkoutSession.objects.get(pk=response.json()['id'])
        self.assertEqual(
            session.datetime_start,
            datetime.datetime(2025, 3, 12, 7, 0, tzinfo=zoneinfo.ZoneInfo('Pacific/Auckland')),
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
            content_type='application/json',
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
            content_type='application/json',
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
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        session = WorkoutSession.objects.get(pk=response.json()['id'])
        self.assertEqual(
            session.datetime_start,
            datetime.datetime(2025, 3, 12, 10, 0, tzinfo=datetime.timezone.utc),
        )

    def test_filter_by_day(self):
        """The viewset has a filterset, so a day can be selected without an error"""

        session = WorkoutSession.objects.get(pk=self.SESSION)
        day = timezone.localtime(session.datetime_start).date()

        response = self.client.get(
            reverse('workoutsession-list'), {'datetime_start__date': day.isoformat()}
        )
        self.assertEqual([entry['id'] for entry in response.json()['results']], [self.SESSION])

        response = self.client.get(
            reverse('workoutsession-list'),
            {'datetime_start__date': (day + datetime.timedelta(days=1)).isoformat()},
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
