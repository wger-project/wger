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

"""
Celery tasks for trophy evaluation and statistics updates.
"""

# Standard Library
import logging
from datetime import timedelta

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

# wger
from wger.celery_configuration import app
from wger.trophies.services import (
    TrophyService,
    UserStatisticsService,
)


logger = logging.getLogger(__name__)

# Trophy settings from WGER_SETTINGS (defined in settings_global.py)
TROPHIES_INACTIVE_USER_DAYS = settings.WGER_SETTINGS['TROPHIES_INACTIVE_USER_DAYS']


@app.task
def evaluate_user_trophies_task(user_id: int):
    """
    Evaluate all trophies for a single user.

    This task is typically called after a workout is logged.

    Args:
        user_id: The ID of the user to evaluate
    """
    try:
        user = User.objects.get(id=user_id)
        awarded = TrophyService.evaluate_all_trophies(user)
        if awarded:
            logger.info(f'Awarded {len(awarded)} trophies to user {user.username}')
    except User.DoesNotExist:
        logger.warning(f'User {user_id} not found for trophy evaluation')
    except Exception as e:
        logger.error(f'Error evaluating trophies for user {user_id}: {e}', exc_info=True)


@app.task
def evaluate_all_users_trophies_task():
    """
    Evaluate trophies for all active users.

    This task can be run periodically (e.g., daily) to catch any
    missed trophy awards or re-evaluate after criteria changes.

    Only processes users who have logged in within TROPHIES_INACTIVE_USER_DAYS.
    """
    inactive_threshold = timezone.now() - timedelta(days=TROPHIES_INACTIVE_USER_DAYS)
    users = User.objects.filter(last_login__gte=inactive_threshold)

    total_awarded = 0
    users_processed = 0

    for user in users.iterator():
        try:
            awarded = TrophyService.evaluate_all_trophies(user)
            if awarded:
                total_awarded += len(awarded)
            users_processed += 1
        except Exception as e:
            logger.error(f'Error evaluating trophies for user {user.id}: {e}', exc_info=True)

    logger.info(
        f'Trophy evaluation complete: processed {users_processed} users, '
        f'awarded {total_awarded} trophies'
    )


@app.task
def update_user_statistics_task(user_id: int):
    """
    Perform a full statistics recalculation for a user.

    This task is useful for:
    - Initial statistics population
    - Recovery from data inconsistencies
    - After bulk data imports

    Args:
        user_id: The ID of the user to update
    """
    try:
        user = User.objects.get(id=user_id)
        UserStatisticsService.update_statistics(user)
        logger.info(f'Updated statistics for user {user.username}')
    except User.DoesNotExist:
        logger.warning(f'User {user_id} not found for statistics update')
    except Exception as e:
        logger.error(f'Error updating statistics for user {user_id}: {e}', exc_info=True)


@app.task
def recalculate_all_statistics_task():
    """
    Recalculate statistics for all active users.

    This task can be used for data recovery or after major changes.
    Only processes users who have logged in recently.
    """
    inactive_threshold = timezone.now() - timedelta(days=TROPHIES_INACTIVE_USER_DAYS)
    users = User.objects.filter(last_login__gte=inactive_threshold)

    users_processed = 0

    for user in users.iterator():
        try:
            UserStatisticsService.update_statistics(user)
            users_processed += 1
        except Exception as e:
            logger.error(f'Error updating statistics for user {user.id}: {e}', exc_info=True)

    logger.info(f'Statistics recalculation complete: processed {users_processed} users')
