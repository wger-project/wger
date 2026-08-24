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
from importlib import import_module
from types import SimpleNamespace

# Django
from django.test import SimpleTestCase
from django.utils import timezone


migration = import_module('wger.manager.migrations.0029_alter_workoutsession_options_and_more')

DAY = datetime.date(2025, 3, 10)


def local(*args):
    return timezone.make_aware(datetime.datetime(*args))


def session(time_start=None, time_end=None, first_log=None, last_log=None, date=DAY):
    return SimpleNamespace(
        date=date,
        time_start=time_start,
        time_end=time_end,
        first_log=first_log,
        last_log=last_log,
    )


class BuildIntervalTestCase(SimpleTestCase):
    """
    Test how the data migration maps the old date/time triple onto the new fields
    """

    def test_both_times(self):
        start, end = migration.build_interval(session(datetime.time(10, 0), datetime.time(11, 30)))

        self.assertEqual(start, local(2025, 3, 10, 10, 0))
        self.assertEqual(end, local(2025, 3, 10, 11, 30))

    def test_end_before_start_lands_on_the_next_day(self):
        start, end = migration.build_interval(session(datetime.time(23, 0), datetime.time(1, 30)))

        self.assertEqual(start, local(2025, 3, 10, 23, 0))
        self.assertEqual(end, local(2025, 3, 11, 1, 30))

    def test_a_dst_gap_cannot_invert_the_interval(self):
        with timezone.override('Europe/Berlin'):
            start, end = migration.build_interval(
                session(
                    datetime.time(2, 30),
                    datetime.time(3, 0),
                    date=datetime.date(2025, 3, 30),
                )
            )

        self.assertGreaterEqual(end.timestamp(), start.timestamp())

    def test_only_a_start_stays_open(self):
        start, end = migration.build_interval(session(time_start=datetime.time(10, 0)))

        self.assertEqual(start, local(2025, 3, 10, 10, 0))
        self.assertIsNone(end)

    def test_only_an_end_starts_at_midnight(self):
        start, end = migration.build_interval(session(time_end=datetime.time(11, 30)))

        self.assertEqual(start, local(2025, 3, 10, 0, 0))
        self.assertEqual(end, local(2025, 3, 10, 11, 30))

    def test_no_times_uses_the_logs(self):
        start, end = migration.build_interval(
            session(first_log=local(2025, 3, 10, 18, 15), last_log=local(2025, 3, 10, 19, 40))
        )

        self.assertEqual(start, local(2025, 3, 10, 18, 15))
        self.assertEqual(end, local(2025, 3, 10, 19, 40))

    def test_a_single_log_leaves_the_session_open(self):
        moment = local(2025, 3, 10, 18, 15)
        start, end = migration.build_interval(session(first_log=moment, last_log=moment))

        self.assertEqual(start, moment)
        self.assertIsNone(end)

    def test_no_times_and_no_logs_keeps_only_the_day(self):
        start, end = migration.build_interval(session())

        self.assertEqual(start, local(2025, 3, 10, 0, 0))
        self.assertIsNone(end)
