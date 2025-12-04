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
from typing import Any

# Local
from .base import BaseTrophyChecker


class DateBasedChecker(BaseTrophyChecker):
    """
    Checker for date-based trophies.

    Used for trophies that require working out on a specific date (month/day).

    Expected params:
        month (int): The month (1-12) when the workout must occur
        day (int): The day of the month (1-31) when the workout must occur

    Example:
        New Year, New Me trophy: params={'month': 1, 'day': 1}
    """

    def validate_params(self) -> bool:
        """Validate that month and day parameters are present and valid."""
        month = self.params.get('month')
        day = self.params.get('day')

        if month is None or day is None:
            return False

        if not isinstance(month, int) or not isinstance(day, int):
            return False

        if month < 1 or month > 12:
            return False

        if day < 1 or day > 31:
            return False

        return True

    def check(self) -> bool:
        """Check if user has worked out on the specified date."""
        if not self.validate_params():
            return False

        month = self.params.get('month')
        day = self.params.get('day')

        # Special case for January 1st - we store this flag directly
        if month == 1 and day == 1:
            return self.statistics.worked_out_jan_1

        # For other dates, we need to query the workout sessions
        # This is done in the statistics service when updating
        from wger.manager.models import WorkoutSession
        return WorkoutSession.objects.filter(
            user=self.user,
            date__month=month,
            date__day=day,
        ).exists()

    def get_progress(self) -> float:
        """
        Get progress towards the trophy.

        For date-based trophies, progress is binary - either achieved (100%) or not (0%).
        """
        return 100.0 if self.check() else 0.0

    def get_target_value(self) -> str:
        """Get the target date as a string."""
        month = self.params.get('month')
        day = self.params.get('day')

        if month is None or day is None:
            return 'N/A'

        # Convert to month name
        import calendar
        month_name = calendar.month_name[month]
        return f'{month_name} {day}'

    def get_current_value(self) -> str:
        """Get whether the user has achieved this."""
        if self.check():
            return 'Achieved'
        return 'Not yet'

    def get_progress_display(self) -> str:
        """Get human-readable progress string."""
        if self.check():
            return 'Achieved!'
        return f'Work out on {self.get_target_value()}'
