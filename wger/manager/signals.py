# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

# Django
from django.core.cache import cache
from django.db.models.signals import (
    post_save,
    pre_delete,
)

# wger
from wger.gym.helpers import get_user_last_activity
from wger.manager.helpers import reset_routine_cache
from wger.manager.models import (
    AbstractChangeConfig,
    Day,
    MaxRepetitionsConfig,
    MaxRestConfig,
    MaxRiRConfig,
    MaxSetsConfig,
    MaxWeightConfig,
    RepetitionsConfig,
    RestConfig,
    RiRConfig,
    Routine,
    SetsConfig,
    Slot,
    SlotEntry,
    WeightConfig,
    WorkoutLog,
    WorkoutSession,
)
from wger.utils.cache import CacheKeyMapper


def update_activity_cache(sender, instance, **kwargs):
    """
    Update the user's cached last activity date
    """

    user = instance.user
    user.usercache.last_activity = get_user_last_activity(user)
    user.usercache.save()


def update_cache_routine(sender, instance: Routine, **kwargs):
    reset_routine_cache(instance)


def update_cache_day(sender, instance: Day, **kwargs):
    reset_routine_cache(instance.routine)


def update_cache_slot(sender, instance: Slot, **kwargs):
    reset_routine_cache(instance.day.routine)


def update_cache_slot_entry(sender, instance: SlotEntry, **kwargs):
    reset_routine_cache(instance.slot.day.routine)


def handle_config_change(sender, instance: AbstractChangeConfig, **kwargs):
    reset_routine_cache(instance.slot_entry.slot.day.routine)


def handle_workout_log_change(sender, instance: WorkoutLog, **kwargs):
    update_activity_cache(sender, instance, **kwargs)
    if instance.routine:
        cache.delete(CacheKeyMapper.routine_api_logs(instance.routine.id, instance.user_id))
        reset_routine_cache(instance.routine, structure=False)


def handle_workout_session_change(sender, instance: WorkoutSession, **kwargs):
    update_activity_cache(sender, instance, **kwargs)
    if instance.routine:
        cache.delete(CacheKeyMapper.routine_api_logs(instance.routine.id, instance.user_id))
        reset_routine_cache(instance.routine, structure=False)


post_save.connect(handle_workout_session_change, sender=WorkoutSession)
post_save.connect(handle_workout_log_change, sender=WorkoutLog)

post_save.connect(update_cache_routine, sender=Routine)
post_save.connect(update_cache_day, sender=Day)
post_save.connect(update_cache_slot, sender=Slot)
post_save.connect(update_cache_slot_entry, sender=SlotEntry)

post_save.connect(handle_config_change, sender=WeightConfig)
post_save.connect(handle_config_change, sender=MaxWeightConfig)
post_save.connect(handle_config_change, sender=RepetitionsConfig)
post_save.connect(handle_config_change, sender=MaxRepetitionsConfig)
post_save.connect(handle_config_change, sender=SetsConfig)
post_save.connect(handle_config_change, sender=MaxSetsConfig)
post_save.connect(handle_config_change, sender=RestConfig)
post_save.connect(handle_config_change, sender=MaxRestConfig)
post_save.connect(handle_config_change, sender=RiRConfig)
post_save.connect(handle_config_change, sender=MaxRiRConfig)

pre_delete.connect(update_cache_routine, sender=Routine)
pre_delete.connect(update_cache_day, sender=Day)
pre_delete.connect(update_cache_slot, sender=Slot)
pre_delete.connect(update_cache_slot_entry, sender=SlotEntry)

pre_delete.connect(handle_config_change, sender=WeightConfig)
pre_delete.connect(handle_config_change, sender=MaxWeightConfig)
pre_delete.connect(handle_config_change, sender=RepetitionsConfig)
pre_delete.connect(handle_config_change, sender=MaxRepetitionsConfig)
pre_delete.connect(handle_config_change, sender=SetsConfig)
pre_delete.connect(handle_config_change, sender=MaxSetsConfig)
pre_delete.connect(handle_config_change, sender=RestConfig)
pre_delete.connect(handle_config_change, sender=MaxRestConfig)
pre_delete.connect(handle_config_change, sender=RiRConfig)
pre_delete.connect(handle_config_change, sender=MaxRiRConfig)

pre_delete.connect(handle_workout_log_change, sender=WorkoutLog)
pre_delete.connect(handle_workout_session_change, sender=WorkoutSession)
