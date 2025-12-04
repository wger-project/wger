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
Signal handlers for the trophies app.

These signals trigger statistics updates and trophy evaluations
when workouts are logged, edited, or deleted.
"""

# Standard Library
import logging

# Django
from django.db.models.signals import (
    post_delete,
    post_save,
)
from django.dispatch import receiver

# wger
from wger.manager.models import (
    WorkoutLog,
    WorkoutSession,
)
from wger.trophies.services import UserStatisticsService
from wger.trophies.tasks import evaluate_user_trophies_task


logger = logging.getLogger(__name__)


def _trigger_trophy_evaluation(user_id: int):
    """
    Trigger async trophy evaluation for a user.

    Uses Celery if available, otherwise evaluates synchronously.
    """
    try:
        evaluate_user_trophies_task.delay(user_id)
    except Exception:
        # Celery not available - evaluate synchronously
        from wger.trophies.services import TrophyService
        from django.contrib.auth.models import User

        try:
            user = User.objects.get(id=user_id)
            TrophyService.evaluate_all_trophies(user)
        except User.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f'Error evaluating trophies for user {user_id}: {e}')


@receiver(post_save, sender=WorkoutLog)
def workout_log_saved(sender, instance, created, **kwargs):
    """
    Handle WorkoutLog save events.

    Updates user statistics when a new workout log is created.
    For edits, triggers a full recalculation to ensure accuracy.
    Then triggers trophy evaluation.
    """
    if not instance.user_id:
        return

    try:
        if created:
            # New log - incremental update
            UserStatisticsService.increment_workout(
                user=instance.user,
                workout_log=instance,
            )
        else:
            # Edited log - full recalculation for accuracy
            UserStatisticsService.update_statistics(instance.user)

        # Trigger trophy evaluation
        _trigger_trophy_evaluation(instance.user_id)
    except Exception as e:
        logger.error(f'Error updating statistics for user {instance.user_id}: {e}', exc_info=True)


@receiver(post_delete, sender=WorkoutLog)
def workout_log_deleted(sender, instance, **kwargs):
    """
    Handle WorkoutLog delete events.

    Triggers full statistics recalculation when a log is deleted.
    """
    if not instance.user_id:
        return

    try:
        UserStatisticsService.handle_workout_deletion(instance.user)
    except Exception as e:
        logger.error(f'Error updating statistics after deletion for user {instance.user_id}: {e}', exc_info=True)


@receiver(post_save, sender=WorkoutSession)
def workout_session_saved(sender, instance, created, **kwargs):
    """
    Handle WorkoutSession save events.

    Updates user statistics when a workout session is created or updated.
    This captures session-level data like start/end times.
    Then triggers trophy evaluation.
    """
    if not instance.user_id:
        return

    try:
        if created:
            # New session - incremental update for session data
            UserStatisticsService.increment_workout(
                user=instance.user,
                session=instance,
            )
        else:
            # Session updated (e.g., time_start changed) - update times
            UserStatisticsService.increment_workout(
                user=instance.user,
                session=instance,
            )

        # Trigger trophy evaluation
        _trigger_trophy_evaluation(instance.user_id)
    except Exception as e:
        logger.error(f'Error updating statistics for session {instance.id}: {e}', exc_info=True)


@receiver(post_delete, sender=WorkoutSession)
def workout_session_deleted(sender, instance, **kwargs):
    """
    Handle WorkoutSession delete events.

    Triggers full statistics recalculation when a session is deleted.
    """
    if not instance.user_id:
        return

    try:
        UserStatisticsService.handle_workout_deletion(instance.user)
    except Exception as e:
        logger.error(f'Error updating statistics after session deletion for user {instance.user_id}: {e}', exc_info=True)
