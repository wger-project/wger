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
from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Any,
    Optional,
)

# Django
from django.contrib.auth.models import User


class BaseTrophyChecker(ABC):
    """
    Abstract base class for all trophy checkers.

    Each trophy type has a corresponding checker class that knows how to
    evaluate whether a user has earned that trophy.
    """

    def __init__(self, user: User, trophy: 'Trophy', params: dict):
        """
        Initialize the checker.

        Args:
            user: The user to check the trophy for
            trophy: The trophy being checked
            params: Parameters from the trophy's checker_params field
        """
        self.user = user
        self.trophy = trophy
        self.params = params
        self._statistics = None

    @property
    def statistics(self):
        """
        Lazy-load the user's statistics.
        """
        if self._statistics is None:
            from wger.trophies.models import UserStatistics
            self._statistics, _ = UserStatistics.objects.get_or_create(user=self.user)
        return self._statistics

    @abstractmethod
    def check(self) -> bool:
        """
        Check if the user has earned the trophy.

        Returns:
            True if the trophy has been earned, False otherwise
        """
        pass

    @abstractmethod
    def get_progress(self) -> float:
        """
        Get the user's progress towards earning the trophy.

        Returns:
            A float between 0 and 100 representing percentage progress
        """
        pass

    @abstractmethod
    def get_target_value(self) -> Any:
        """
        Get the target value the user needs to achieve.

        Returns:
            The target value (type depends on trophy type)
        """
        pass

    @abstractmethod
    def get_current_value(self) -> Any:
        """
        Get the user's current value towards the target.

        Returns:
            The current value (type depends on trophy type)
        """
        pass

    def get_progress_display(self) -> str:
        """
        Get a human-readable string describing the progress.

        Returns:
            A formatted string showing current/target progress
        """
        current = self.get_current_value()
        target = self.get_target_value()
        return f'{current} / {target}'

    def validate_params(self) -> bool:
        """
        Validate that the required parameters are present.

        Override this method in subclasses to add specific validation.

        Returns:
            True if parameters are valid, False otherwise
        """
        return True

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(user={self.user.username}, trophy={self.trophy.name})>'
