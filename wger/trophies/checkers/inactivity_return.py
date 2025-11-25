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
from typing import Any

# Local
from .base import BaseTrophyChecker


class InactivityReturnChecker(BaseTrophyChecker):
    """
    Checker for inactivity return trophies (Phoenix trophy).

    Used for trophies that reward users for returning to training after
    being inactive for a certain period.

    Expected params:
        inactive_days (int): The minimum number of inactive days before returning

    Example:
        Phoenix trophy: params={'inactive_days': 30}
    """

    def validate_params(self) -> bool:
        """Validate that inactive_days parameter is present and valid."""
        inactive_days = self.params.get('inactive_days')
        return inactive_days is not None and isinstance(inactive_days, int) and inactive_days > 0

    def check(self) -> bool:
        """
        Check if user has returned to training after being inactive.

        The user earns this trophy if:
        1. They have a last_inactive_date recorded (meaning they were inactive)
        2. They have a last_workout_date after the inactive period
        3. The gap between last_inactive_date and the workout before that was >= inactive_days
        """
        if not self.validate_params():
            return False

        last_inactive_date = self.statistics.last_inactive_date
        last_workout_date = self.statistics.last_workout_date

        # If no inactive date recorded, user hasn't had a qualifying gap yet
        if last_inactive_date is None:
            return False

        # If no workout after the inactive period, haven't returned yet
        if last_workout_date is None:
            return False

        # Check if they've worked out after the inactive date
        # The statistics service sets last_inactive_date when it detects
        # a gap of >= inactive_days before a new workout
        return last_workout_date > last_inactive_date

    def get_progress(self) -> float:
        """
        Get progress towards the trophy.

        This is a special trophy - progress shows how close to earning it after returning.
        If they haven't been inactive long enough, shows 0.
        If they've returned after inactivity, shows 100.
        """
        return 100.0 if self.check() else 0.0

    def get_target_value(self) -> int:
        """Get the required number of inactive days."""
        return self.params.get('inactive_days', 0)

    def get_current_value(self) -> str:
        """Get the current status."""
        if self.check():
            return 'Returned after inactivity'

        last_workout = self.statistics.last_workout_date
        if last_workout is None:
            return 'No workouts yet'

        # Calculate days since last workout
        today = datetime.date.today()
        days_inactive = (today - last_workout).days

        return f'{days_inactive} days since last workout'

    def get_progress_display(self) -> str:
        """Get human-readable progress string."""
        if self.check():
            return 'Achieved! Welcome back!'

        target_days = self.get_target_value()
        last_workout = self.statistics.last_workout_date

        if last_workout is None:
            return f'Complete a workout, then return after {target_days}+ days of rest'

        today = datetime.date.today()
        days_inactive = (today - last_workout).days

        if days_inactive >= target_days:
            return 'Return to training to earn this trophy!'

        return f'{days_inactive} / {target_days} days inactive'
