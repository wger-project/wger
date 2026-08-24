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
from django.utils import timezone

# Third Party
from rest_framework import status

# wger
from wger.core.models import UserProfile
from wger.core.tests import powersync_base_test
from wger.manager.models import (
    Routine,
    WorkoutLog,
    WorkoutSession,
)


# Pinned in test-routine-data.json
ROUTINE_OWNED = 2  # user 'test'
ROUTINE_OTHER = 1  # user 'admin'

# Pinned in test-workout-session.json (owned by 'test', linked to ROUTINE_OWNED's user)
SESSION_OWNED = 'bbbbbbbb-bbbb-bbbb-bbbb-000000000005'
SESSION_OTHER = 'bbbbbbbb-bbbb-bbbb-bbbb-000000000001'  # owned by 'admin'

# Pinned in test-workout-log-data.json (owned by 'test')
LOG_OWNED = 'aaaaaaaa-aaaa-aaaa-aaaa-000000000005'

EXERCISE_PUBLIC = 2  # any base exercise; 'test' is allowed to reference it


class WorkoutLogPowerSyncTestCase(powersync_base_test.PowerSyncResourceTestCase):
    """
    PowerSync handlers for manager.WorkoutLog. The handler runs
    check_fk_ownership against (Routine, 'routine') and (WorkoutSession, 'session').
    """

    table = 'manager_workoutlog'
    resource = WorkoutLog

    pk_owned = LOG_OWNED

    create_payload = {
        'id': 'aaaaaaaa-aaaa-aaaa-aaaa-000000000099',
        'date': '2030-01-15T10:00:00Z',
        'routine': ROUTINE_OWNED,
        'session': SESSION_OWNED,
        'exercise': EXERCISE_PUBLIC,
        'weight': '40.0',
        'repetitions': 10,
    }
    update_payload = {
        'id': pk_owned,
        'weight': '42.5',
    }

    fk_ownership = (
        ('routine', ROUTINE_OTHER),
        ('session', SESSION_OTHER),
    )


class WorkoutSessionPowerSyncTestCase(powersync_base_test.PowerSyncResourceTestCase):
    """
    PowerSync handlers for manager.WorkoutSession. The handler runs
    check_fk_ownership against (Routine, 'routine').
    """

    table = 'manager_workoutsession'
    resource = WorkoutSession

    pk_owned = SESSION_OWNED

    create_payload = {
        'id': 'bbbbbbbb-bbbb-bbbb-bbbb-000000000099',
        'date': '2030-01-15',
        'routine': ROUTINE_OWNED,
        'impression': '2',
        'notes': 'created via PowerSync',
    }
    update_payload = {
        'id': pk_owned,
        'notes': 'edited via PowerSync',
    }

    fk_ownership = (('routine', ROUTINE_OTHER),)

    def test_create_with_deprecated_fields(self):
        """
        A push queued by an app version that predates 2.7 still lands on the day
        and time it was recorded on
        """

        self.authenticate()
        response = self.push(
            'PUT',
            {
                'id': 'bbbbbbbb-bbbb-bbbb-bbbb-000000000098',
                'date': '2030-01-15',
                'time_start': '23:00:00',
                'time_end': '01:30:00',
                'routine': ROUTINE_OWNED,
                'impression': '2',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        session = WorkoutSession.objects.get(pk='bbbbbbbb-bbbb-bbbb-bbbb-000000000098')
        self.assertEqual(
            session.datetime_start,
            timezone.make_aware(datetime.datetime(2030, 1, 15, 23, 0)),
        )
        self.assertEqual(
            session.datetime_end,
            timezone.make_aware(datetime.datetime(2030, 1, 16, 1, 30)),
        )

    def test_deprecated_fields_resolve_in_the_owners_timezone(self):
        """The queued wall time is the user's, not the zone the request runs in"""

        profile = UserProfile.objects.get(user__username=self.user_access)
        profile.time_zone = 'Pacific/Auckland'
        profile.save()

        self.authenticate()
        response = self.push(
            'PUT',
            {
                'id': 'bbbbbbbb-bbbb-bbbb-bbbb-000000000097',
                'date': '2030-01-15',
                'time_start': '07:00:00',
                'routine': ROUTINE_OWNED,
                'impression': '2',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        session = WorkoutSession.objects.get(pk='bbbbbbbb-bbbb-bbbb-bbbb-000000000097')
        self.assertEqual(
            session.datetime_start,
            datetime.datetime(2030, 1, 15, 7, 0, tzinfo=zoneinfo.ZoneInfo('Pacific/Auckland')),
        )


class RoutinePowerSyncTestCase(
    powersync_base_test.PowerSyncBaseTestCase,
    powersync_base_test.PowerSyncCreateNotAllowedTestCase,
    powersync_base_test.PowerSyncUpdateTestCase,
    powersync_base_test.PowerSyncDeleteTestCase,
):
    """
    PowerSync handlers for manager.Routine. Creation is explicitly rejected
    by the dispatcher (must go through REST), so only PATCH/DELETE are tested.
    """

    table = 'manager_routine'
    resource = Routine

    pk_owned = ROUTINE_OWNED

    update_payload = {
        'id': pk_owned,
        'name': 'Renamed via PowerSync',
    }

    # Anything sent via PUT must be rejected; the body content doesn't matter.
    create_payload = {'id': 9999, 'name': 'should not be created'}
