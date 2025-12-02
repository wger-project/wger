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
import logging
from typing import (
    Dict,
    Optional,
    Type,
)

# Django
from django.contrib.auth.models import User

# Local
from .base import BaseTrophyChecker
from .count_based import CountBasedChecker
from .date_based import DateBasedChecker
from .inactivity_return import InactivityReturnChecker
from .streak import StreakChecker
from .time_based import TimeBasedChecker
from .volume import VolumeChecker
from .weekend_warrior import WeekendWarriorChecker


logger = logging.getLogger(__name__)


class CheckerRegistry:
    """
    Registry for trophy checker classes.

    Maps checker class names (as stored in Trophy.checker_class) to their
    actual Python classes.
    """

    # Registry mapping simple keys to checker classes
    # Using simple keys instead of full Python paths to avoid breakage if module structure changes
    _registry: Dict[str, Type[BaseTrophyChecker]] = {
        'count_based': CountBasedChecker,
        'streak': StreakChecker,
        'weekend_warrior': WeekendWarriorChecker,
        'volume': VolumeChecker,
        'time_based': TimeBasedChecker,
        'date_based': DateBasedChecker,
        'inactivity_return': InactivityReturnChecker,
    }

    @classmethod
    def register(cls, class_path: str, checker_class: Type[BaseTrophyChecker]) -> None:
        """
        Register a new checker class.

        Args:
            class_path: The path string to use in Trophy.checker_class
            checker_class: The checker class to register
        """
        if not issubclass(checker_class, BaseTrophyChecker):
            raise ValueError(f'{checker_class} must be a subclass of BaseTrophyChecker')
        cls._registry[class_path] = checker_class

    @classmethod
    def unregister(cls, class_path: str) -> None:
        """
        Unregister a checker class.

        Args:
            class_path: The path string to remove
        """
        cls._registry.pop(class_path, None)

    @classmethod
    def get_checker_class(cls, class_path: str) -> Optional[Type[BaseTrophyChecker]]:
        """
        Get a checker class by its path.

        Args:
            class_path: The path string from Trophy.checker_class

        Returns:
            The checker class, or None if not found
        """
        return cls._registry.get(class_path)

    @classmethod
    def get_all_checkers(cls) -> Dict[str, Type[BaseTrophyChecker]]:
        """
        Get all registered checker classes.

        Returns:
            A copy of the registry dictionary
        """
        return cls._registry.copy()

    @classmethod
    def create_checker(
        cls,
        user: User,
        trophy: 'Trophy',
    ) -> Optional[BaseTrophyChecker]:
        """
        Factory method to create a checker instance for a trophy.

        Args:
            user: The user to check the trophy for
            trophy: The trophy to check

        Returns:
            An instance of the appropriate checker class, or None if the
            checker class is not found in the registry
        """
        checker_class = cls.get_checker_class(trophy.checker_class)

        if checker_class is None:
            logger.warning(
                f'Checker class not found in registry: {trophy.checker_class} '
                f'for trophy: {trophy.name}'
            )
            return None

        try:
            return checker_class(
                user=user,
                trophy=trophy,
                params=trophy.checker_params or {},
            )
        except Exception as e:
            logger.error(
                f'Error creating checker for trophy {trophy.name}: {e}',
                exc_info=True,
            )
            return None


def get_checker_for_trophy(user: User, trophy: 'Trophy') -> Optional[BaseTrophyChecker]:
    """
    Convenience function to get a checker instance for a trophy.

    Args:
        user: The user to check the trophy for
        trophy: The trophy to check

    Returns:
        An instance of the appropriate checker class, or None if not found
    """
    return CheckerRegistry.create_checker(user, trophy)
