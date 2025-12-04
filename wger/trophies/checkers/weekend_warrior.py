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


class WeekendWarriorChecker(BaseTrophyChecker):
    """
    Checker for Weekend Warrior trophy.

    Used for trophies that require working out on both Saturday and Sunday
    for consecutive weekends.

    Expected params:
        weekends (int): The number of consecutive complete weekends required

    Example:
        Weekend Warrior trophy: params={'weekends': 4}
    """

    def validate_params(self) -> bool:
        """Validate that weekends parameter is present and valid."""
        weekends = self.params.get('weekends')
        return weekends is not None and isinstance(weekends, int) and weekends > 0

    def check(self) -> bool:
        """Check if user has completed workouts on required consecutive weekends."""
        if not self.validate_params():
            return False
        return self.get_current_value() >= self.get_target_value()

    def get_progress(self) -> float:
        """Get progress as percentage of weekend streak achieved."""
        if not self.validate_params():
            return 0.0
        target = self.get_target_value()
        if target <= 0:
            return 0.0
        current = self.get_current_value()
        progress = (current / target) * 100
        return min(progress, 100.0)

    def get_target_value(self) -> int:
        """Get the target number of consecutive complete weekends."""
        return self.params.get('weekends', 0)

    def get_current_value(self) -> int:
        """Get the user's current weekend workout streak."""
        return self.statistics.weekend_workout_streak

    def get_progress_display(self) -> str:
        """Get human-readable progress string."""
        current = self.get_current_value()
        target = self.get_target_value()
        return f'{current} / {target} weekends'
