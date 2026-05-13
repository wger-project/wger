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

# wger
from wger.core.tests.api_base_test import ApiBaseResourceTestCase
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.dataclasses import WorkoutDayData
from wger.manager.models import (
    Day,
    Label,
    WorkoutSession,
)
from wger.manager.models.routine import Routine


class RoutineTestCase(WgerTestCase):
    """
    Test the different day and date functions
    """

    maxDiff = None
    """Show full diff on assert failures"""

    routine: Routine
    day1: Day
    day2: Day
    day3: Day

    def setUp(self):
        super().setUp()

        self.routine = Routine(
            user_id=1,
            name='A routine',
            description='A routine',
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 10),
        )
        self.routine.save()

        self.day1 = Day(routine=self.routine, description='day 1', order=1)
        self.day1.save()

        self.day2 = Day(
            routine=self.routine,
            description='day 2',
            order=2,
            is_rest=True,
        )
        self.day2.save()

        self.day3 = Day(routine=self.routine, description='day 3', order=3)
        self.day3.save()

        Label(routine=self.routine, start_offset=0, end_offset=3, label='First label').save()
        Label(routine=self.routine, start_offset=4, end_offset=5, label='Second label').save()

    def test_labels(self):
        """
        Test that the labels are correctly assigned to their dates
        """

        self.assertEqual(
            self.routine.label_dict,
            {
                datetime.date(2024, 1, 1): 'First label',
                datetime.date(2024, 1, 2): 'First label',
                datetime.date(2024, 1, 3): 'First label',
                datetime.date(2024, 1, 4): 'First label',
                datetime.date(2024, 1, 5): 'Second label',
                datetime.date(2024, 1, 6): 'Second label',
            },
        )

    def test_date_sequences(self):
        """
        Test that the days are correctly outputted in a sequence
        """

        self.assertListEqual(
            self.routine.date_sequence,
            [
                WorkoutDayData(
                    day=self.day1,
                    iteration=1,
                    date=datetime.date(2024, 1, 1),
                    label='First label',
                ),
                WorkoutDayData(
                    day=self.day2,
                    iteration=1,
                    date=datetime.date(2024, 1, 2),
                    label='First label',
                ),
                WorkoutDayData(
                    day=self.day3,
                    iteration=1,
                    date=datetime.date(2024, 1, 3),
                    label='First label',
                ),
                WorkoutDayData(
                    day=self.day1,
                    iteration=2,
                    date=datetime.date(2024, 1, 4),
                    label='First label',
                ),
                WorkoutDayData(
                    day=self.day2,
                    iteration=2,
                    date=datetime.date(2024, 1, 5),
                    label='Second label',
                ),
                WorkoutDayData(
                    day=self.day3,
                    iteration=2,
                    date=datetime.date(2024, 1, 6),
                    label='Second label',
                ),
                WorkoutDayData(
                    day=self.day1,
                    iteration=3,
                    date=datetime.date(2024, 1, 7),
                    label=None,
                ),
                WorkoutDayData(
                    day=self.day2,
                    iteration=3,
                    date=datetime.date(2024, 1, 8),
                    label=None,
                ),
                WorkoutDayData(
                    day=self.day3,
                    iteration=3,
                    date=datetime.date(2024, 1, 9),
                    label=None,
                ),
                WorkoutDayData(
                    day=self.day1,
                    iteration=4,
                    date=datetime.date(2024, 1, 10),
                    label=None,
                ),
            ],
        )

    def test_date_sequences_need_logs_to_advance_no_session(self):
        """
        Test that days do not advance if they have the need_logs_to_advance flag set
        and there are no logs
        """

        # Arrange
        today = datetime.date.today()
        start = today - datetime.timedelta(days=5)
        self.routine.start = start
        self.routine.end = today + datetime.timedelta(weeks=3)
        self.day1.need_logs_to_advance = True
        self.day1.save()
        WorkoutSession.objects.all().delete()
        Label.objects.all().delete()

        # Assert
        sequence = self.routine.date_sequence

        # The first day does not advance
        self.assertEqual(
            sequence[0],
            WorkoutDayData(
                day=self.day1,
                iteration=1,
                date=start,
            ),
        )
        self.assertEqual(
            sequence[1],
            WorkoutDayData(
                day=self.day1,
                iteration=1,
                date=start + datetime.timedelta(days=1),
            ),
        )
        self.assertEqual(
            sequence[2],
            WorkoutDayData(
                day=self.day1,
                iteration=1,
                date=start + datetime.timedelta(days=2),
            ),
        )
        self.assertEqual(
            sequence[3],
            WorkoutDayData(
                day=self.day1,
                iteration=1,
                date=start + datetime.timedelta(days=3),
            ),
        )
        self.assertEqual(
            sequence[4],
            WorkoutDayData(
                day=self.day1,
                iteration=1,
                date=start + datetime.timedelta(days=4),
            ),
        )
        self.assertEqual(
            sequence[5],
            WorkoutDayData(
                day=self.day1,
                iteration=1,
                date=start + datetime.timedelta(days=5),
            ),
        )

        # For dates in the future, the days always advance
        self.assertEqual(
            sequence[6],
            WorkoutDayData(
                day=self.day2,
                iteration=1,
                date=start + datetime.timedelta(days=6),
            ),
        )
        self.assertEqual(
            sequence[7],
            WorkoutDayData(
                day=self.day3,
                iteration=1,
                date=start + datetime.timedelta(days=7),
            ),
        )
        self.assertEqual(
            sequence[8],
            WorkoutDayData(
                day=self.day1,
                iteration=2,
                date=start + datetime.timedelta(days=8),
            ),
        )
        self.assertEqual(
            sequence[9],
            WorkoutDayData(
                day=self.day2,
                iteration=2,
                date=start + datetime.timedelta(days=9),
            ),
        )
        self.assertEqual(
            sequence[10],
            WorkoutDayData(
                day=self.day3,
                iteration=2,
                date=start + datetime.timedelta(days=10),
            ),
        )
        self.assertEqual(
            sequence[11],
            WorkoutDayData(
                day=self.day1,
                iteration=3,
                date=start + datetime.timedelta(days=11),
            ),
        )

    def test_date_sequences_need_logs_to_advance_session_available(self):
        """
        Test that days only advance if they have the need_logs_to_advance flag set
        and there are is a session
        """

        # Arrange
        today = datetime.date.today()
        start = today - datetime.timedelta(days=5)

        self.routine.start = start
        self.routine.end = today + datetime.timedelta(days=10)
        self.day1.need_logs_to_advance = True
        self.day1.save()

        Label.objects.all().delete()
        WorkoutSession.objects.all().delete()
        WorkoutSession.objects.create(
            day=self.day1,
            routine=self.routine,
            date=start + datetime.timedelta(days=2),
            user=self.routine.user,
        )

        # Assert
        sequence = self.routine.date_sequence
        self.assertEqual(
            sequence[0],
            WorkoutDayData(
                day=self.day1,
                iteration=1,
                date=start,
            ),
        )
        self.assertEqual(
            sequence[1],
            WorkoutDayData(
                day=self.day1,
                iteration=1,
                date=start + datetime.timedelta(days=1),
            ),
        )

        # Session saved on this day
        self.assertEqual(
            sequence[2],
            WorkoutDayData(
                day=self.day1,
                iteration=1,
                date=start + datetime.timedelta(days=2),
            ),
        )

        # Day can advance
        self.assertEqual(
            sequence[3],
            WorkoutDayData(
                day=self.day2,
                iteration=1,
                date=start + datetime.timedelta(days=3),
            ),
        )
        self.assertEqual(
            sequence[4],
            WorkoutDayData(
                day=self.day3,
                iteration=1,
                date=start + datetime.timedelta(days=4),
            ),
        )
        self.assertEqual(
            sequence[5],
            WorkoutDayData(
                day=self.day1,
                iteration=2,
                date=start + datetime.timedelta(days=5),
            ),
        )

        # For dates in the future, the days always advance
        self.assertEqual(
            sequence[6],
            WorkoutDayData(
                day=self.day2,
                iteration=2,
                date=start + datetime.timedelta(days=6),
            ),
        )
        self.assertEqual(
            sequence[7],
            WorkoutDayData(
                day=self.day3,
                iteration=2,
                date=start + datetime.timedelta(days=7),
            ),
        )
        self.assertEqual(
            sequence[8],
            WorkoutDayData(
                day=self.day1,
                iteration=3,
                date=start + datetime.timedelta(days=8),
            ),
        )
        self.assertEqual(
            sequence[9],
            WorkoutDayData(
                day=self.day2,
                iteration=3,
                date=start + datetime.timedelta(days=9),
            ),
        )

    def test_date_sequence_week_skip(self):
        """
        Test that the fit_in_week flag works
        """

        # Arrange
        self.routine.fit_in_week = True
        self.routine.end = datetime.date(2024, 1, 12)
        self.routine.save()

        # Assert
        self.assertListEqual(
            self.routine.date_sequence,
            [
                # Monday
                WorkoutDayData(
                    day=self.day1,
                    iteration=1,
                    date=datetime.date(2024, 1, 1),
                    label='First label',
                ),
                WorkoutDayData(
                    day=self.day2,
                    iteration=1,
                    date=datetime.date(2024, 1, 2),
                    label='First label',
                ),
                WorkoutDayData(
                    day=self.day3,
                    iteration=1,
                    date=datetime.date(2024, 1, 3),
                    label='First label',
                ),
                WorkoutDayData(
                    day=None,
                    iteration=1,
                    date=datetime.date(2024, 1, 4),
                    label='First label',
                ),
                WorkoutDayData(
                    day=None,
                    iteration=1,
                    date=datetime.date(2024, 1, 5),
                    label='Second label',
                ),
                WorkoutDayData(
                    day=None,
                    iteration=1,
                    date=datetime.date(2024, 1, 6),
                    label='Second label',
                ),
                WorkoutDayData(
                    day=None,
                    iteration=1,
                    date=datetime.date(2024, 1, 7),
                ),
                # Monday, start the cycle again
                WorkoutDayData(
                    day=self.day1,
                    iteration=2,
                    date=datetime.date(2024, 1, 8),
                ),
                WorkoutDayData(
                    day=self.day2,
                    iteration=2,
                    date=datetime.date(2024, 1, 9),
                ),
                WorkoutDayData(
                    day=self.day3,
                    iteration=2,
                    date=datetime.date(2024, 1, 10),
                ),
                WorkoutDayData(
                    day=None,
                    iteration=2,
                    date=datetime.date(2024, 1, 11),
                ),
                WorkoutDayData(
                    day=None,
                    iteration=2,
                    date=datetime.date(2024, 1, 12),
                ),
            ],
        )

    def test_date_sequences_current(self):
        """
        Test that the correct active day is returned
        """
        self.assertEqual(
            self.routine.data_for_day(datetime.date(2024, 1, 7)),
            WorkoutDayData(day=self.day1, iteration=3, date=datetime.date(2024, 1, 7)),
        )


class RoutineApiTestCase(ApiBaseResourceTestCase):
    """
    Tests the routine api endpoint
    """

    pk = 2
    resource = Routine
    private_resource = True
    # special_endpoints = (
    #     'day-sequence',
    #     'date-sequence-gym',
    #     'current-day-display',
    #     'current-day-gym',
    #     'current-iteration-display',
    #     'current-iteration-gym',
    # )
    data = {
        'name': 'A new comment',
        'start': '2024-03-11',
        'end': '2024-06-20',
    }


class RoutineDateValidationTestCase(WgerTestCase):
    """
    The routine API must enforce sane date bounds:
    - ``end`` may not be before ``start``
    - the duration may not exceed ``Routine.MAX_DURATION_DAYS``, otherwise
      walking the ``date_sequence`` could be abused to consume server CPU.
    """

    def _post_routine(self, start, end):
        self.user_login('test')
        return self.client.post(
            reverse('routine-list'),
            data={
                'name': 'duration test',
                'start': start.isoformat(),
                'end': end.isoformat(),
            },
            content_type='application/json',
        )

    def test_rejects_routine_longer_than_limit(self):
        start = datetime.date(2024, 1, 1)
        end = start + datetime.timedelta(days=Routine.MAX_DURATION_DAYS + 1)
        response = self._post_routine(start, end)
        self.assertEqual(response.status_code, 400)

    def test_accepts_routine_at_limit(self):
        start = datetime.date(2024, 1, 1)
        end = start + datetime.timedelta(days=Routine.MAX_DURATION_DAYS)
        response = self._post_routine(start, end)
        self.assertEqual(response.status_code, 201)

    def test_rejects_end_before_start(self):
        start = datetime.date(2024, 6, 1)
        end = datetime.date(2024, 1, 1)
        response = self._post_routine(start, end)
        self.assertEqual(response.status_code, 400)


class RoutineLogsAndStatsScopeTestCase(WgerTestCase):
    """
    The /logs/ and /stats/ actions of a routine return the owner's
    private workout history. They must never be accessible to anyone but
    the routine owner, even when the routine is a public template.
    """

    PUBLIC_TEMPLATE_PK = 5
    # owned by trainer2 (user 5), is_template + is_public

    @property
    def logs_url(self):
        return reverse('routine-logs', kwargs={'pk': self.PUBLIC_TEMPLATE_PK})

    @property
    def stats_url(self):
        return reverse('routine-stats', kwargs={'pk': self.PUBLIC_TEMPLATE_PK})

    @property
    def detail_url(self):
        return reverse('routine-detail', kwargs={'pk': self.PUBLIC_TEMPLATE_PK})

    def test_non_owner_cannot_read_template_logs(self):
        self.user_login('test')
        response = self.client.get(self.logs_url)
        self.assertEqual(response.status_code, 403)

    def test_non_owner_cannot_read_template_stats(self):
        self.user_login('test')
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, 403)

    def test_owner_can_read_own_template_logs(self):
        self.user_login('trainer2')
        response = self.client.get(self.logs_url)
        self.assertEqual(response.status_code, 200)

    def test_owner_can_read_own_template_stats(self):
        self.user_login('trainer2')
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, 200)

    def test_template_structure_remains_publicly_readable(self):
        """
        The template's exercise structure is the public part of the
        feature — only logs/stats need to be restricted.
        """
        self.user_login('test')
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
