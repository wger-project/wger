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

# Standard Library
from abc import (
    ABC,
    abstractmethod,
)

# wger
from wger.manager.dataclasses import SetConfigData
from wger.manager.models import (
    AbstractChangeConfig,
    WorkoutLog,
)


class AbstractSetCalculations(ABC):
    iteration: int
    sets_configs: list[AbstractChangeConfig]
    weight_configs: list[AbstractChangeConfig]
    reps_configs: list[AbstractChangeConfig]
    rir_configs: list[AbstractChangeConfig]
    rest_configs: list[AbstractChangeConfig]
    logs: list[WorkoutLog]

    def __init__(
        self,
        iteration: int,
        sets_configs: list[AbstractChangeConfig],
        weight_configs: list[AbstractChangeConfig],
        reps_configs: list[AbstractChangeConfig],
        rir_configs: list[AbstractChangeConfig],
        rest_configs: list[AbstractChangeConfig],
        logs: list[WorkoutLog],
    ):
        self.iteration = iteration
        self.sets_configs = sets_configs
        self.weight_configs = weight_configs
        self.reps_configs = reps_configs
        self.rir_configs = rir_configs
        self.rest_configs = rest_configs
        self.logs = logs

    @abstractmethod
    def calculate(self) -> SetConfigData:
        raise NotImplementedError()
