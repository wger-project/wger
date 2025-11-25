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
from typing import (
    Any,
    Optional,
)

# Local
from .base import BaseTrophyChecker


class TimeBasedChecker(BaseTrophyChecker):
    """
    Checker for time-based trophies.

    Used for trophies that require working out before or after a certain time.

    Expected params:
        before (str, optional): Time string in HH:MM format - workout must be before this time
        after (str, optional): Time string in HH:MM format - workout must be after this time

    At least one of 'before' or 'after' must be provided.

    Example:
        Early Bird trophy: params={'before': '06:00'}
        Night Owl trophy: params={'after': '21:00'}
    """

    def _parse_time(self, time_str: str) -> Optional[datetime.time]:
        """Parse a time string in HH:MM format."""
        try:
            parts = time_str.split(':')
            hour = int(parts[0])
            minute = int(parts[1]) if len(parts) > 1 else 0
            return datetime.time(hour=hour, minute=minute)
        except (ValueError, IndexError, AttributeError):
            return None

    def validate_params(self) -> bool:
        """Validate that at least one of before/after is present and valid."""
        before = self.params.get('before')
        after = self.params.get('after')

        if before is None and after is None:
            return False

        if before is not None and self._parse_time(before) is None:
            return False

        if after is not None and self._parse_time(after) is None:
            return False

        return True

    def check(self) -> bool:
        """Check if user has worked out at the required time."""
        if not self.validate_params():
            return False

        before = self.params.get('before')
        after = self.params.get('after')

        if before is not None:
            # Check if user has ever worked out before the specified time
            target_time = self._parse_time(before)
            earliest = self.statistics.earliest_workout_time
            if earliest is not None and earliest < target_time:
                return True

        if after is not None:
            # Check if user has ever worked out after the specified time
            target_time = self._parse_time(after)
            latest = self.statistics.latest_workout_time
            if latest is not None and latest > target_time:
                return True

        return False

    def get_progress(self) -> float:
        """
        Get progress towards the trophy.

        For time-based trophies, progress is binary - either achieved (100%) or not (0%).
        """
        return 100.0 if self.check() else 0.0

    def get_target_value(self) -> str:
        """Get the target time as a string."""
        before = self.params.get('before')
        after = self.params.get('after')

        if before is not None:
            return f'Before {before}'
        if after is not None:
            return f'After {after}'
        return 'N/A'

    def get_current_value(self) -> str:
        """Get the user's relevant workout time."""
        before = self.params.get('before')

        if before is not None:
            earliest = self.statistics.earliest_workout_time
            if earliest is not None:
                return earliest.strftime('%H:%M')
            return 'No workouts yet'

        # For 'after' condition
        latest = self.statistics.latest_workout_time
        if latest is not None:
            return latest.strftime('%H:%M')
        return 'No workouts yet'

    def get_progress_display(self) -> str:
        """Get human-readable progress string."""
        if self.check():
            return 'Achieved!'

        before = self.params.get('before')
        if before is not None:
            earliest = self.statistics.earliest_workout_time
            if earliest is not None:
                return f'Earliest: {earliest.strftime("%H:%M")} (need before {before})'
            return f'Work out before {before}'

        after = self.params.get('after')
        if after is not None:
            latest = self.statistics.latest_workout_time
            if latest is not None:
                return f'Latest: {latest.strftime("%H:%M")} (need after {after})'
            return f'Work out after {after}'

        return 'N/A'
