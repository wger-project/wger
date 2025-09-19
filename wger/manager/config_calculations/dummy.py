#  This file is part of wger Workout Manager <https://github.com/wger-project>.
#  Copyright (C) wger Team
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

# wger
from wger.manager.config_calculations.calculations import AbstractSetCalculations
from wger.manager.dataclasses import SetConfigData


class SetCalculations(AbstractSetCalculations):
    def calculate(self):
        if self.iteration == 1:
            return SetConfigData(
                exercise=1,
                sets=2,
                weight=24,
                repetitions=1,
                rir=2,
                rest=120,
            )
        else:
            return SetConfigData(
                exercise=2,
                sets=4,
                weight=42,
                repetitions=10,
                rir=1,
                rest=90,
            )
