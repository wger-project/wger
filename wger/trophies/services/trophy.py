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
from datetime import timedelta
from typing import (
    Dict,
    List,
    Optional,
)

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone

# wger
from wger.trophies.checkers.registry import CheckerRegistry
from wger.trophies.models import (
    Trophy,
    UserTrophy,
)


logger = logging.getLogger(__name__)

# Trophy settings from WGER_SETTINGS (defined in settings_global.py)
TROPHIES_ENABLED = settings.WGER_SETTINGS['TROPHIES_ENABLED']
TROPHIES_INACTIVE_USER_DAYS = settings.WGER_SETTINGS['TROPHIES_INACTIVE_USER_DAYS']


class TrophyService:
    """
    Service class for trophy evaluation and management.

    This service handles:
    - Evaluating whether users have earned trophies
    - Awarding trophies to users
    - Retrieving trophy progress and status
    """

    @classmethod
    def evaluate_all_trophies(cls, user: User) -> List[UserTrophy]:
        """
        Evaluate all unearned trophies for a user.

        Checks each active trophy the user hasn't earned yet using the
        appropriate checker class. Awards trophies where criteria are met.

        Args:
            user: The user to evaluate trophies for

        Returns:
            List of newly awarded UserTrophy instances
        """
        if cls.should_skip_user(user):
            return []

        # Get all active trophies the user hasn't earned
        earned_trophy_ids = UserTrophy.objects.filter(user=user).values_list('trophy_id', flat=True)
        unevaluated_trophies = Trophy.objects.filter(is_active=True).exclude(id__in=earned_trophy_ids)

        awarded = []
        for trophy in unevaluated_trophies:
            user_trophy = cls.evaluate_trophy(user, trophy)
            if user_trophy:
                awarded.append(user_trophy)

        return awarded

    @classmethod
    def evaluate_trophy(cls, user: User, trophy: Trophy) -> Optional[UserTrophy]:
        """
        Evaluate a single trophy for a user.

        Creates a checker instance and checks if the user has met the
        trophy criteria. Awards the trophy if earned.

        Args:
            user: The user to evaluate the trophy for
            trophy: The trophy to evaluate

        Returns:
            UserTrophy if earned, None otherwise
        """
        if not trophy.is_active:
            return None

        # Check if already earned
        if UserTrophy.objects.filter(user=user, trophy=trophy).exists():
            return None

        # Get the checker for this trophy
        checker = CheckerRegistry.create_checker(user, trophy)
        if checker is None:
            logger.warning(f'No checker found for trophy: {trophy.name}')
            return None

        try:
            if checker.check():
                return cls.award_trophy(user, trophy, progress=100.0)
        except Exception as e:
            logger.error(f'Error checking trophy {trophy.name} for user {user.id}: {e}', exc_info=True)

        return None

    @classmethod
    def award_trophy(cls, user: User, trophy: Trophy, progress: float = 100.0) -> UserTrophy:
        """
        Award a trophy to a user.

        Creates a UserTrophy record marking the trophy as earned.

        Args:
            user: The user to award the trophy to
            trophy: The trophy to award
            progress: The progress value (default 100 for earned)

        Returns:
            The created UserTrophy instance
        """
        user_trophy, created = UserTrophy.objects.get_or_create(
            user=user,
            trophy=trophy,
            defaults={'progress': progress},
        )

        if created:
            logger.info(f'Awarded trophy "{trophy.name}" to user {user.username}')

        return user_trophy

    @classmethod
    def get_user_trophies(cls, user: User) -> List[UserTrophy]:
        """
        Get all earned trophies for a user.

        Args:
            user: The user to get trophies for

        Returns:
            List of UserTrophy instances
        """
        return list(
            UserTrophy.objects.filter(user=user)
            .select_related('trophy')
            .order_by('-earned_at')
        )

    @classmethod
    def get_all_trophy_progress(cls, user: User, include_hidden: bool = False) -> List[Dict]:
        """
        Get all trophies with progress information for a user.

        Returns both earned and unearned trophies with their current progress.
        For progressive trophies, calculates progress on-the-fly.

        Args:
            user: The user to get trophy progress for
            include_hidden: If True, include hidden trophies even if not earned

        Returns:
            List of dicts with trophy info and progress
        """
        result = []

        # Get all active trophies
        trophies = Trophy.objects.filter(is_active=True).order_by('order', 'name')

        # Get user's earned trophies
        earned = {
            ut.trophy_id: ut
            for ut in UserTrophy.objects.filter(user=user).select_related('trophy')
        }

        for trophy in trophies:
            user_trophy = earned.get(trophy.id)
            is_earned = user_trophy is not None

            # Skip hidden trophies unless earned or explicitly included
            if trophy.is_hidden and not is_earned and not include_hidden:
                continue

            progress_data = {
                'trophy': trophy,
                'is_earned': is_earned,
                'earned_at': user_trophy.earned_at if is_earned else None,
                'progress': 100.0 if is_earned else 0.0,
                'current_value': None,
                'target_value': None,
                'progress_display': None,
            }

            # Calculate progress for progressive trophies that aren't earned
            if trophy.is_progressive and not is_earned:
                checker = CheckerRegistry.create_checker(user, trophy)
                if checker:
                    try:
                        progress_data['progress'] = checker.get_progress()
                        progress_data['current_value'] = checker.get_current_value()
                        progress_data['target_value'] = checker.get_target_value()

                        # Create display string (e.g., "5000/100000 kg")
                        current = progress_data['current_value']
                        target = progress_data['target_value']
                        if current is not None and target is not None:
                            progress_data['progress_display'] = f'{current}/{target}'
                    except Exception as e:
                        logger.error(f'Error getting progress for trophy {trophy.name}: {e}')

            result.append(progress_data)

        return result

    @classmethod
    def should_skip_user(cls, user: User) -> bool:
        """
        Check if a user should be skipped for trophy evaluation.

        Users are skipped if:
        - The trophy system is globally disabled (WGER_SETTINGS['TROPHIES_ENABLED'])
        - They have disabled trophies in their profile (userprofile.trophies_enabled)
        - They haven't logged in for more than TROPHIES_INACTIVE_USER_DAYS

        Args:
            user: The user to check

        Returns:
            True if user should be skipped
        """
        # Check if trophy system is globally disabled
        if not TROPHIES_ENABLED:
            return True

        # Check if user has disabled trophies (if profile has this field)
        if hasattr(user, 'userprofile'):
            profile = user.userprofile
            if hasattr(profile, 'trophies_enabled') and not profile.trophies_enabled:
                return True

        # Check for inactivity
        if user.last_login:
            inactive_threshold = timezone.now() - timedelta(days=TROPHIES_INACTIVE_USER_DAYS)
            if user.last_login < inactive_threshold:
                return True

        return False

    @classmethod
    def reevaluate_trophies(
        cls,
        trophy_ids: Optional[List[int]] = None,
        user_ids: Optional[List[int]] = None,
    ) -> Dict[str, int]:
        """
        Re-evaluate trophies for users (admin function).

        Can be used when trophy criteria change or to fix data inconsistencies.
        This will check if any users now qualify for trophies they didn't before.

        Args:
            trophy_ids: List of trophy IDs to re-evaluate (None = all)
            user_ids: List of user IDs to re-evaluate (None = all active)

        Returns:
            Dict with counts: {'users_checked': N, 'trophies_awarded': M}
        """
        # Get trophies to evaluate
        trophy_qs = Trophy.objects.filter(is_active=True)
        if trophy_ids:
            trophy_qs = trophy_qs.filter(id__in=trophy_ids)
        trophies = list(trophy_qs)

        # Get users to evaluate
        if user_ids:
            users = User.objects.filter(id__in=user_ids)
        else:
            # Get active users only
            inactive_threshold = timezone.now() - timedelta(days=TROPHIES_INACTIVE_USER_DAYS)
            users = User.objects.filter(last_login__gte=inactive_threshold)

        users_checked = 0
        trophies_awarded = 0

        for user in users:
            if cls.should_skip_user(user):
                continue

            users_checked += 1

            for trophy in trophies:
                # Don't skip already earned - this is a re-evaluation
                user_trophy = cls.evaluate_trophy(user, trophy)
                if user_trophy:
                    trophies_awarded += 1

        return {
            'users_checked': users_checked,
            'trophies_awarded': trophies_awarded,
        }
