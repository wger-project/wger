#  This file is part of wger Workout Manager <https://github.com/wger-project>.
#  Copyright (C) 2013 - 2021 wger Team
#
#  wger Workout Manager is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  wger Workout Manager is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Standard Library
import datetime
import logging
from collections import (
    Counter,
    defaultdict,
)
from decimal import Decimal
from typing import List

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.db.models import Prefetch
from django.urls import reverse
from django.utils import timezone

# wger
from wger.exercises.models import Exercise
from wger.manager.dataclasses import (
    GroupedLogData,
    LogData,
    RoutineLogData,
    WorkoutDayData,
)
from wger.manager.managers import (
    PublicRoutineTemplateManager,
    RoutineManager,
    RoutineTemplateManager,
)
from wger.manager.models import (
    Day,
    WorkoutLog,
)
from wger.utils.cache import CacheKeyMapper


logger = logging.getLogger(__name__)


class Routine(models.Model):
    """
    Model for a routine
    """

    objects = RoutineManager()
    templates = RoutineTemplateManager()
    public = PublicRoutineTemplateManager()

    MAX_DURATION_DAYS = 120
    """
    Maximum duration of a routine in days (~4 months)
    """

    class Meta:
        ordering = [
            '-start',
            '-created',
        ]

    user = models.ForeignKey(
        User,
        verbose_name='User',
        on_delete=models.CASCADE,
    )

    name = models.CharField(
        verbose_name='Name',
        max_length=25,
        blank=True,
    )

    description = models.TextField(
        verbose_name='Description',
        max_length=1000,
        blank=True,
    )

    created = models.DateTimeField(
        verbose_name='Creation date',
        auto_now_add=True,
    )

    start = models.DateField(
        verbose_name='Start date',
    )

    end = models.DateField(
        verbose_name='End date',
    )

    is_template = models.BooleanField(
        verbose_name='Workout template',
        help_text='Marking a workout as a template will freeze it and allow you to make copies of it',
        default=False,
        null=False,
    )
    """Marking a workout as a template will freeze it and allow you to make copies of it"""

    is_public = models.BooleanField(
        verbose_name='Public template',
        help_text='A public template is available to other users',
        default=False,
        null=False,
    )
    """A public template is available to other users"""

    fit_in_week = models.BooleanField(
        default=False,
    )

    def get_absolute_url(self):
        """
        Returns the canonical URL to view a workout
        """
        return reverse(
            'manager:routine:view',
            kwargs={'pk': self.id},
        )

    def __str__(self):
        """
        Return a more human-readable representation
        """
        if self.name:
            return self.name
        else:
            return f'Routine {self.id} - {self.created}'

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self

    def save(self, *args, **kwargs):
        """The is_public flag cannot be set if the routine is not a template"""
        if self.is_public and not self.is_template:
            self.is_public = False

        super().save(*args, **kwargs)

    @property
    def duration(self) -> datetime.timedelta:
        return self.end - self.start

    @property
    def label_dict(self) -> dict[datetime.date, str]:
        out = defaultdict(str)
        for label in self.labels.all():
            for i in range(label.start_offset, label.end_offset + 1):
                out[self.start + datetime.timedelta(days=i)] = label.label

        return out

    @property
    def date_sequence(self) -> List[WorkoutDayData]:
        """
        Return a list with specific dates and routine days

        If a day needs logs to continue it will be repeated until the user adds one.
        """
        cache_key = CacheKeyMapper.routine_date_sequence_key(self.id)
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data

        # wger
        from wger.manager.models import (
            Slot,
            SlotEntry,
        )

        # Prefetch all config relationships to avoid N+1 queries
        days = (
            Day.objects.filter(routine=self)
            .prefetch_related(
                Prefetch(
                    'slots',
                    queryset=Slot.objects.prefetch_related(
                        Prefetch(
                            'entries',
                            queryset=SlotEntry.objects.prefetch_related(
                                'repetition_unit',
                                'weight_unit',
                                'weightconfig_set',
                                'maxweightconfig_set',
                                'repetitionsconfig_set',
                                'maxrepetitionsconfig_set',
                                'rirconfig_set',
                                'maxrirconfig_set',
                                'restconfig_set',
                                'maxrestconfig_set',
                                'setsconfig_set',
                                'maxsetsconfig_set',
                                # Prefetch logs with sessions
                                Prefetch(
                                    'workoutlog_set',
                                    queryset=WorkoutLog.objects.select_related('session'),
                                    # to_attr='prefetched_logs'
                                ),
                            ),
                            to_attr='prefetched_entries',
                        )
                    ),
                    to_attr='prefetched_slots',
                ),
                'workoutsession_set',
            )
            .order_by('order')
        )

        if not days:
            return []

        # Precompute session dates from prefetched logs
        workout_session_map = defaultdict(set)
        for day in days:
            for session in day.workoutsession_set.all():
                workout_session_map[day.id].add(session.date)

        # Main sequence generation logic
        labels = self.label_dict
        current_date = self.start
        days_list = list(days)
        nr_of_days = len(days_list)
        iteration_counter = Counter()
        sequence = []
        is_first = True
        day_index = 0

        for day in days:
            iteration_counter[day.id] = 1

        while current_date <= self.end:
            current_day = days_list[day_index]
            previous_date = current_date - datetime.timedelta(days=1)

            # Checks whether the user can proceed to the next day in the sequence
            #
            # This is possible if
            # - the day doesn't require logs
            # - the day requires logs, and they exist. Note that we check for logs on the previous
            #   day, since when a user logs a session for a day, the advancement should happen on
            #   the next day, not immediately.
            # - the date is in the future (used e.g. for calendars where we assume we will proceed)
            has_session = previous_date in workout_session_map[current_day.id]
            can_proceed = (
                not current_day.need_logs_to_advance
                or (current_day.need_logs_to_advance and has_session)
                or current_date > timezone.localdate()
            )

            if can_proceed and not is_first:
                iteration_counter[current_day.id] += 1
                day_index = (day_index + 1) % nr_of_days
                current_day = days_list[day_index]

            # If fit_in_week is set we need to fill the rest of the week with placeholders
            if self.fit_in_week and nr_of_days % 7 != 0 and day_index == 0 and not is_first:
                days_to_monday = 7 - current_date.weekday()
                for i in range(days_to_monday):
                    placeholder_date = current_date + datetime.timedelta(days=i)
                    if placeholder_date > self.end:
                        break
                    sequence.append(
                        WorkoutDayData(
                            date=placeholder_date,
                            day=None,
                            label=labels.get(placeholder_date),
                            # This is ugly, but we don't want to advance the iteration
                            iteration=iteration_counter[current_day.id] - 1,
                        )
                    )
                current_date += datetime.timedelta(days=days_to_monday)
                if current_date > self.end:
                    continue

            # Add day data and advance the date
            sequence.append(
                WorkoutDayData(
                    iteration=iteration_counter[current_day.id],
                    date=current_date,
                    day=current_day,
                    label=labels.get(current_date),
                )
            )
            current_date += datetime.timedelta(days=1)
            is_first = False

        cache.set(cache_key, sequence, settings.WGER_SETTINGS['ROUTINE_CACHE_TTL'])
        return sequence

    def data_for_day(self, date=None) -> WorkoutDayData | None:
        """
        Return the WorkoutDayData for the specified day. If no date is given, return
        the results for "today"
        """
        if date is None:
            date = timezone.localdate()

        for data in self.date_sequence:
            if data.date == date:
                return data

        return None

    def data_for_iteration(self, iteration: int | None = None) -> List[WorkoutDayData]:
        """
        Return the WorkoutDayData entries for the specified iteration. If no iteration
        is given, return the results for the one for "today". If none could be found,
        return the data for the first one
        """

        if iteration is None:
            for data in self.date_sequence:
                if data.date == timezone.localdate():
                    iteration = data.iteration
                    break

        if iteration is None:
            iteration = 1

        out = []

        for data in self.date_sequence:
            if data.iteration == iteration:
                out.append(data)

        return out

    def logs_display(self, date: datetime.date = None):
        """
        Returns all the logs for this routine, grouped by the session
        """
        out = []

        qs = self.sessions.all()
        if date:
            qs = qs.filter(date=date)

        for session in qs:
            out.append({'session': session, 'logs': session.logs.all()})

        return out

    def calculate_log_statistics(self) -> RoutineLogData:
        """
        Calculates various statistics for the routine based on the logged workouts.

        Returns:
            RoutineLogData: An object containing the calculated statistics.
        """
        # wger
        from wger.manager.helpers import brzycki_intensity

        result = RoutineLogData()
        intensity_counter = GroupedLogData()

        def update_grouped_log_data(
            entry: GroupedLogData,
            date: datetime.date,
            week_nr: int,
            iter: int,
            exercise: Exercise,
            value: Decimal | int | None,
        ):
            """
            Updates grouped log data

            This method just adds the value to the corresponding entries
            """
            if value is None:
                return

            muscles = exercise.muscles.all()

            entry.daily[date].exercises[exercise.id] += value
            entry.weekly[week_nr].exercises[exercise.id] += value
            entry.iteration[iter].exercises[exercise.id] += value
            entry.mesocycle.exercises[exercise.id] += value

            entry.daily[date].total += value
            entry.weekly[week_nr].total += value
            entry.iteration[iter].total += value
            entry.mesocycle.total += value

            for muscle in muscles:
                pk = muscle.id

                entry.daily[date].muscle[pk] += value
                entry.weekly[week_nr].muscle[pk] += value
                entry.iteration[iter].muscle[pk] += value
                entry.mesocycle.muscle[pk] += value

        def safe_divide(numerator, denominator):
            return numerator / denominator if denominator != 0 else numerator

        def avg_log_data(data: LogData, count: LogData) -> None:
            data.total = safe_divide(data.total, count.total)
            data.upper_body = safe_divide(data.upper_body, count.upper_body)
            data.lower_body = safe_divide(data.lower_body, count.lower_body)
            for k in data.muscle:
                data.muscle[k] = safe_divide(data.muscle[k], count.muscle[k])
            for k in data.exercises:
                data.exercises[k] = safe_divide(data.exercises[k], count.exercises[k])

        def calculate_average_intensity(result: GroupedLogData, counters: GroupedLogData) -> None:
            avg_log_data(result.mesocycle, counters.mesocycle)

            for res_group, cnt_group in (
                (result.daily, counters.daily),
                (result.weekly, counters.weekly),
                (result.iteration, counters.iteration),
            ):
                for key in res_group:
                    avg_log_data(res_group[key], cnt_group[key])

        # Iterate over each workout session associated with the routine
        for session in self.sessions.all():
            session_date = session.date
            week_number = session_date.isocalendar().week

            # TODO: filter for lb
            for log in session.logs.kg().reps():
                iteration = log.iteration
                exercise = log.exercise
                weight = log.weight
                reps = log.repetitions

                values_not_none = reps is not None and weight is not None
                exercise_volume = weight * reps if values_not_none else 0

                update_grouped_log_data(
                    entry=result.volume,
                    iter=iteration,
                    week_nr=week_number,
                    date=session_date,
                    exercise=exercise,
                    value=exercise_volume,
                )

                # Each log always corresponds to one set
                update_grouped_log_data(
                    entry=result.sets,
                    iter=iteration,
                    week_nr=week_number,
                    date=session_date,
                    exercise=exercise,
                    value=1,
                )

                if values_not_none:
                    update_grouped_log_data(
                        entry=intensity_counter,
                        iter=iteration,
                        week_nr=week_number,
                        date=session_date,
                        exercise=exercise,
                        value=1,
                    )

                    update_grouped_log_data(
                        entry=result.intensity,
                        iter=iteration,
                        week_nr=week_number,
                        date=session_date,
                        exercise=exercise,
                        value=brzycki_intensity(weight, reps),
                    )

        calculate_average_intensity(result.intensity, intensity_counter)

        return result
