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

# Local
from .base import BaseTrophyChecker
from .count_based import CountBasedChecker
from .date_based import DateBasedChecker
from .inactivity_return import InactivityReturnChecker
from .registry import CheckerRegistry
from .streak import StreakChecker
from .time_based import TimeBasedChecker
from .volume import VolumeChecker
from .weekend_warrior import WeekendWarriorChecker
