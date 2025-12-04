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
from decimal import Decimal
from typing import Optional

# Django
from django.contrib.auth.models import User
from django.db.models import Sum

# wger
from wger.manager.consts import WEIGHT_UNIT_LB
from wger.manager.models import (
    WorkoutLog,
    WorkoutSession,
)
from wger.trophies.models import UserStatistics
from wger.utils.units import AbstractWeight


logger = logging.getLogger(__name__)


class UserStatisticsService:
    """
    Service class for managing user trophy statistics.

    This service handles:
    - Full recalculation of statistics from workout history
    - Incremental updates when new workouts are logged
    - Weight unit normalization (all stored in kg)
    """

    @classmethod
    def get_or_create_statistics(cls, user: User) -> UserStatistics:
        """
        Get or create a UserStatistics record for the user.

        Args:
            user: The user to get/create statistics for

        Returns:
            The UserStatistics instance
        """
        stats, created = UserStatistics.objects.get_or_create(user=user)
        return stats

    @classmethod
    def update_statistics(cls, user: User) -> UserStatistics:
        """
        Perform a full recalculation of user statistics from workout history.

        This method recalculates all statistics from scratch by querying
        the user's complete workout history. Use this for:
        - Initial population of statistics
        - Recovery from data inconsistencies
        - After bulk data imports

        Args:
            user: The user to update statistics for

        Returns:
            The updated UserStatistics instance
        """
        stats = cls.get_or_create_statistics(user)

        # Get all workout logs for this user
        logs = WorkoutLog.objects.filter(user=user).select_related('weight_unit', 'session')

        # Calculate total weight lifted (normalized to kg)
        total_weight = cls._calculate_total_weight(logs)
        stats.total_weight_lifted = total_weight

        # Get all workout sessions
        sessions = WorkoutSession.objects.filter(user=user).order_by('date')
        stats.total_workouts = sessions.count()

        # Calculate streaks and other date-based stats
        workout_dates = list(sessions.values_list('date', flat=True).distinct().order_by('date'))
        current_streak, longest_streak = cls._calculate_streaks(workout_dates)
        stats.current_streak = current_streak
        stats.longest_streak = longest_streak

        # Set last workout date
        if workout_dates:
            stats.last_workout_date = workout_dates[-1]

        # Calculate earliest and latest workout times
        earliest, latest = cls._calculate_workout_times(sessions)
        stats.earliest_workout_time = earliest
        stats.latest_workout_time = latest

        # Calculate weekend workout streak
        weekend_streak, last_complete_weekend = cls._calculate_weekend_streak(workout_dates)
        stats.weekend_workout_streak = weekend_streak
        stats.last_complete_weekend_date = last_complete_weekend

        # Check if user worked out on January 1st
        stats.worked_out_jan_1 = cls._check_jan_1_workout(workout_dates)

        # Calculate last inactive date (for Phoenix trophy)
        stats.last_inactive_date = cls._calculate_last_inactive_date(workout_dates)

        stats.save()
        return stats

    @classmethod
    def increment_workout(
        cls,
        user: User,
        workout_log: Optional[WorkoutLog] = None,
        session: Optional[WorkoutSession] = None,
    ) -> UserStatistics:
        """
        Incrementally update statistics when a new workout is logged.

        This method performs efficient incremental updates rather than
        full recalculation. It's called by signal handlers when:
        - A new WorkoutLog is created
        - A WorkoutSession is created/updated

        Args:
            user: The user to update statistics for
            workout_log: The new workout log (if triggered by log creation)
            session: The workout session (if triggered by session creation)

        Returns:
            The updated UserStatistics instance
        """
        stats = cls.get_or_create_statistics(user)

        # Update total weight if a log was provided
        if workout_log and workout_log.weight is not None:
            weight_kg = cls._normalize_weight(workout_log.weight, workout_log.weight_unit_id)
            reps = workout_log.repetitions or Decimal('1')
            volume = weight_kg * reps
            stats.total_weight_lifted += volume

        # Get the session date
        session_date = None
        if session:
            session_date = session.date
        elif workout_log and workout_log.session:
            session_date = workout_log.session.date

        if session_date:
            # Convert datetime to date if needed for comparison
            if hasattr(session_date, 'date'):
                session_date = session_date.date()

            # Check if this is a new workout day
            is_new_day = stats.last_workout_date is None or session_date > stats.last_workout_date

            if is_new_day:
                # Update streak
                if stats.last_workout_date:
                    days_gap = (session_date - stats.last_workout_date).days
                    if days_gap == 1:
                        # Consecutive day - extend streak
                        stats.current_streak += 1
                    elif days_gap > 1:
                        # Gap in workouts - check for Phoenix trophy trigger
                        if days_gap >= 30:
                            stats.last_inactive_date = stats.last_workout_date
                        # Reset streak
                        stats.current_streak = 1
                else:
                    # First workout ever
                    stats.current_streak = 1

                # Update longest streak
                if stats.current_streak > stats.longest_streak:
                    stats.longest_streak = stats.current_streak

                # Update last workout date
                stats.last_workout_date = session_date

                # Check for Jan 1st workout
                if session_date.month == 1 and session_date.day == 1:
                    stats.worked_out_jan_1 = True

                # Update weekend streak
                cls._update_weekend_streak_incremental(stats, session_date)

        # Update workout times if session has time info
        if session and session.time_start:
            if stats.earliest_workout_time is None or session.time_start < stats.earliest_workout_time:
                stats.earliest_workout_time = session.time_start
            if stats.latest_workout_time is None or session.time_start > stats.latest_workout_time:
                stats.latest_workout_time = session.time_start

        # Count sessions for total workouts (recalculate to be accurate)
        stats.total_workouts = WorkoutSession.objects.filter(user=user).count()

        stats.save()
        return stats

    @classmethod
    def handle_workout_deletion(cls, user: User) -> UserStatistics:
        """
        Handle statistics update when a workout is deleted.

        Since deletion can affect streaks and totals in complex ways,
        we perform a full recalculation.

        Args:
            user: The user whose workout was deleted

        Returns:
            The updated UserStatistics instance
        """
        return cls.update_statistics(user)

    @classmethod
    def _normalize_weight(cls, weight: Decimal, weight_unit_id: Optional[int]) -> Decimal:
        """
        Convert weight to kg using AbstractWeight utility.

        Args:
            weight: The weight value
            weight_unit_id: The weight unit ID (1=kg, 2=lb)

        Returns:
            Weight in kg
        """
        if weight is None:
            return Decimal('0')

        mode = 'lb' if weight_unit_id == WEIGHT_UNIT_LB else 'kg'
        return AbstractWeight(weight, mode).kg

    @classmethod
    def _calculate_total_weight(cls, logs) -> Decimal:
        """
        Calculate total weight lifted from workout logs.

        Volume = weight * reps for each set, summed across all logs.
        All weights are normalized to kg.
        """
        total = Decimal('0')
        for log in logs:
            if log.weight is not None and log.repetitions is not None:
                weight_kg = cls._normalize_weight(log.weight, log.weight_unit_id)
                total += weight_kg * log.repetitions
        return total

    @classmethod
    def _calculate_streaks(cls, workout_dates: list) -> tuple:
        """
        Calculate current and longest workout streaks.

        A streak is consecutive days with at least one workout.

        Args:
            workout_dates: List of dates with workouts, sorted ascending

        Returns:
            Tuple of (current_streak, longest_streak)
        """
        if not workout_dates:
            return 0, 0

        # Remove duplicates and sort
        unique_dates = sorted(set(workout_dates))

        current_streak = 1
        longest_streak = 1
        streak = 1

        today = datetime.date.today()

        for i in range(1, len(unique_dates)):
            if (unique_dates[i] - unique_dates[i - 1]).days == 1:
                streak += 1
            else:
                streak = 1

            if streak > longest_streak:
                longest_streak = streak

        # Check if current streak is active (includes today or yesterday)
        if unique_dates:
            last_workout = unique_dates[-1]
            days_since_last = (today - last_workout).days
            if days_since_last <= 1:
                current_streak = streak
            else:
                current_streak = 0

        return current_streak, longest_streak

    @classmethod
    def _calculate_workout_times(cls, sessions) -> tuple:
        """
        Find earliest and latest workout start times.

        Args:
            sessions: QuerySet of WorkoutSession

        Returns:
            Tuple of (earliest_time, latest_time)
        """
        times = [s.time_start for s in sessions if s.time_start is not None]
        if not times:
            return None, None
        return min(times), max(times)

    @classmethod
    def _calculate_weekend_streak(cls, workout_dates: list) -> tuple:
        """
        Calculate consecutive weekends with workouts on both Saturday and Sunday.

        Args:
            workout_dates: List of workout dates

        Returns:
            Tuple of (weekend_streak, last_complete_weekend_date)
        """
        if not workout_dates:
            return 0, None

        date_set = set(workout_dates)

        # Find all complete weekends (both Sat and Sun)
        complete_weekends = []
        checked_saturdays = set()

        for d in sorted(date_set):
            # Saturday = 5, Sunday = 6 in Python's weekday()
            if d.weekday() == 5:  # Saturday
                sunday = d + datetime.timedelta(days=1)
                if sunday in date_set:
                    complete_weekends.append(d)
                    checked_saturdays.add(d)
            elif d.weekday() == 6:  # Sunday
                saturday = d - datetime.timedelta(days=1)
                if saturday in date_set and saturday not in checked_saturdays:
                    complete_weekends.append(saturday)
                    checked_saturdays.add(saturday)

        if not complete_weekends:
            return 0, None

        # Sort by date
        complete_weekends = sorted(set(complete_weekends))

        # Count consecutive weekends
        streak = 1
        max_streak = 1

        for i in range(1, len(complete_weekends)):
            # Check if this is the next weekend (7 days apart)
            if (complete_weekends[i] - complete_weekends[i - 1]).days == 7:
                streak += 1
                if streak > max_streak:
                    max_streak = streak
            else:
                streak = 1

        # Determine current streak
        today = datetime.date.today()
        last_complete = complete_weekends[-1]

        # Find the most recent Saturday
        days_since_saturday = (today.weekday() - 5) % 7
        last_saturday = today - datetime.timedelta(days=days_since_saturday)

        # Current streak is valid if last complete weekend was within 2 weeks
        days_since_last_complete = (last_saturday - last_complete).days
        if days_since_last_complete <= 7:
            current_streak = streak
        else:
            current_streak = 0

        return current_streak, last_complete

    @classmethod
    def _update_weekend_streak_incremental(cls, stats: UserStatistics, workout_date: datetime.date):
        """
        Incrementally update weekend streak when a workout is logged.

        Args:
            stats: The UserStatistics to update
            workout_date: The date of the workout
        """
        # Only process weekend days
        weekday = workout_date.weekday()
        if weekday not in (5, 6):  # Not Saturday or Sunday
            return

        # Determine the Saturday of this weekend
        if weekday == 5:  # Saturday
            saturday = workout_date
        else:  # Sunday
            saturday = workout_date - datetime.timedelta(days=1)

        sunday = saturday + datetime.timedelta(days=1)

        # Check if both days have workouts
        has_saturday = WorkoutSession.objects.filter(
            user=stats.user, date=saturday
        ).exists()
        has_sunday = WorkoutSession.objects.filter(
            user=stats.user, date=sunday
        ).exists()

        if has_saturday and has_sunday:
            # This weekend is complete
            if stats.last_complete_weekend_date:
                days_since_last = (saturday - stats.last_complete_weekend_date).days
                if days_since_last == 7:
                    # Consecutive weekend
                    stats.weekend_workout_streak += 1
                elif days_since_last > 7:
                    # Gap - reset streak
                    stats.weekend_workout_streak = 1
                # If days_since_last < 7, it's the same weekend - no change
            else:
                # First complete weekend
                stats.weekend_workout_streak = 1

            stats.last_complete_weekend_date = saturday

    @classmethod
    def _check_jan_1_workout(cls, workout_dates: list) -> bool:
        """
        Check if user has ever worked out on January 1st.

        Args:
            workout_dates: List of workout dates

        Returns:
            True if user has worked out on any January 1st
        """
        return any(d.month == 1 and d.day == 1 for d in workout_dates)

    @classmethod
    def _calculate_last_inactive_date(cls, workout_dates: list) -> Optional[datetime.date]:
        """
        Calculate the last inactive date (for Phoenix trophy).

        The last inactive date is the last workout date before a gap of 30+ days.

        Args:
            workout_dates: List of workout dates, sorted ascending

        Returns:
            The last inactive date, or None if no 30+ day gap exists
        """
        if not workout_dates:
            return None

        unique_dates = sorted(set(workout_dates))
        last_inactive = None

        for i in range(1, len(unique_dates)):
            gap = (unique_dates[i] - unique_dates[i - 1]).days
            if gap >= 30:
                last_inactive = unique_dates[i - 1]

        return last_inactive
