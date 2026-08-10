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
from django.core.cache import cache
from django.urls import reverse

# wger
from wger.core.tests.api_base_test import ApiBaseTestCase
from wger.core.tests.base_testcase import BaseTestCase
from wger.manager.models import (
    WorkoutLog,
    WorkoutSession,
)
from wger.utils.cache import CacheKeyMapper


class RoutineCacheInvalidationTestCase(BaseTestCase, ApiBaseTestCase):
    """
    Tests that log and session changes invalidate the routine caches

    Routine 1 belongs to the admin user (user 1). Log and session changes
    invalidate everything except the structure cache, which does not depend
    on them.
    """

    ROUTINE_ID = 1
    USER_ID = 1

    @property
    def volatile_keys(self):
        return (
            CacheKeyMapper.routine_date_sequence_key(self.ROUTINE_ID),
            CacheKeyMapper.routine_api_date_sequence_display_key(self.ROUTINE_ID, self.USER_ID),
            CacheKeyMapper.routine_api_date_sequence_gym_key(self.ROUTINE_ID, self.USER_ID),
            CacheKeyMapper.routine_api_logs(self.ROUTINE_ID, self.USER_ID),
            CacheKeyMapper.routine_api_stats(self.ROUTINE_ID, self.USER_ID),
        )

    @property
    def structure_key(self):
        return CacheKeyMapper.routine_api_structure_key(self.ROUTINE_ID, self.USER_ID)

    def prime_caches(self):
        """
        Populate all routine caches through the API, like the apps do
        """
        self.authenticate('admin')
        for url_name in (
            'routine-date-sequence-display-mode',
            'routine-date-sequence-gym-mode',
            'routine-structure',
            'routine-logs',
            'routine-stats',
        ):
            response = self.client.get(reverse(url_name, kwargs={'pk': self.ROUTINE_ID}))
            self.assertEqual(response.status_code, 200)

        for key in self.volatile_keys:
            self.assertIsNotNone(cache.get(key), f'Cache key {key} was not primed')
        self.assertIsNotNone(cache.get(self.structure_key))

    def assert_volatile_caches_cleared(self):
        for key in self.volatile_keys:
            self.assertIsNone(cache.get(key), f'Cache key {key} was not invalidated')

        # The structure does not depend on logs or sessions
        self.assertIsNotNone(cache.get(self.structure_key))

    def test_saving_a_log_resets_the_cache(self):
        self.prime_caches()

        WorkoutLog(
            user_id=self.USER_ID,
            exercise_id=1,
            routine_id=self.ROUTINE_ID,
            weight=80,
            repetitions=5,
        ).save()

        self.assert_volatile_caches_cleared()

    def test_saving_a_session_resets_the_cache(self):
        self.prime_caches()

        WorkoutSession(
            user_id=self.USER_ID,
            routine_id=self.ROUTINE_ID,
            date=datetime.date(2024, 5, 1),
        ).save()

        self.assert_volatile_caches_cleared()

    def test_log_without_routine_keeps_the_cache(self):
        self.prime_caches()

        WorkoutLog(user_id=self.USER_ID, exercise_id=1, weight=80, repetitions=5).save()

        for key in self.volatile_keys:
            self.assertIsNotNone(cache.get(key))
