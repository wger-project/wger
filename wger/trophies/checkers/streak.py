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


class StreakChecker(BaseTrophyChecker):
    """
    Checker for streak-based trophies.

    Used for trophies that require working out for consecutive days.

    Expected params:
        days (int): The number of consecutive days required

    Example:
        Unstoppable trophy: params={'days': 30}
    """

    def validate_params(self) -> bool:
        """Validate that days parameter is present and valid."""
        days = self.params.get('days')
        return days is not None and isinstance(days, int) and days > 0

    def check(self) -> bool:
        """Check if user has achieved the required streak."""
        if not self.validate_params():
            return False
        # Check both current streak and longest streak (in case they achieved it before)
        target = self.get_target_value()
        return (
            self.statistics.current_streak >= target
            or self.statistics.longest_streak >= target
        )

    def get_progress(self) -> float:
        """Get progress as percentage of streak achieved."""
        if not self.validate_params():
            return 0.0
        target = self.get_target_value()
        if target <= 0:
            return 0.0
        # Use the maximum of current or longest streak for progress
        current = self.get_current_value()
        progress = (current / target) * 100
        return min(progress, 100.0)

    def get_target_value(self) -> int:
        """Get the target streak length in days."""
        return self.params.get('days', 0)

    def get_current_value(self) -> int:
        """Get the user's best streak (max of current and longest)."""
        return max(self.statistics.current_streak, self.statistics.longest_streak)

    def get_progress_display(self) -> str:
        """Get human-readable progress string."""
        current = self.get_current_value()
        target = self.get_target_value()
        return f'{current} / {target} days'
