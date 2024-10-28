# -*- coding: utf-8 -*-

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
from django.db.models.signals import (
    post_save,
    pre_delete,
    pre_save,
)

# wger
from wger.gym.helpers import get_user_last_activity
from wger.manager.helpers import reset_routine_cache
from wger.manager.models import (
    Day,
    MaxRepsConfig,
    MaxRestConfig,
    MaxWeightConfig,
    RepsConfig,
    RestConfig,
    RiRConfig,
    Routine,
    SetsConfig,
    Slot,
    SlotConfig,
    WeightConfig,
    WorkoutLog,
    WorkoutSession,
)


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


def update_cache_slot_config(sender, instance: SlotConfig, **kwargs):
    reset_routine_cache(instance.slot.day.routine)


def update_cache_weight_config(sender, instance: WeightConfig, **kwargs):
    reset_routine_cache(instance.slot_config.slot.day.routine)


def update_cache_max_weight_config(sender, instance: MaxWeightConfig, **kwargs):
    reset_routine_cache(instance.slot_config.slot.day.routine)


def update_cache_reps_config(sender, instance: RepsConfig, **kwargs):
    reset_routine_cache(instance.slot_config.slot.day.routine)


def update_cache_max_reps_config(sender, instance: MaxRepsConfig, **kwargs):
    reset_routine_cache(instance.slot_config.slot.day.routine)


def update_cache_sets_config(sender, instance: SetsConfig, **kwargs):
    reset_routine_cache(instance.slot_config.slot.day.routine)


def update_cache_rest_config(sender, instance: RestConfig, **kwargs):
    reset_routine_cache(instance.slot_config.slot.day.routine)


def update_cache_max_rest_config(sender, instance: MaxRestConfig, **kwargs):
    reset_routine_cache(instance.slot_config.slot.day.routine)


def update_cache_rir_config(sender, instance: RiRConfig, **kwargs):
    reset_routine_cache(instance.slot_config.slot.day.routine)


post_save.connect(update_activity_cache, sender=WorkoutSession)
post_save.connect(update_activity_cache, sender=WorkoutLog)

pre_save.connect(update_cache_routine, sender=Routine)
pre_save.connect(update_cache_day, sender=Day)
pre_save.connect(update_cache_slot, sender=Slot)
pre_save.connect(update_cache_slot_config, sender=SlotConfig)
pre_save.connect(update_cache_weight_config, sender=WeightConfig)
pre_save.connect(update_cache_max_weight_config, sender=MaxWeightConfig)
pre_save.connect(update_cache_reps_config, sender=RepsConfig)
pre_save.connect(update_cache_max_reps_config, sender=MaxRepsConfig)
pre_save.connect(update_cache_sets_config, sender=SetsConfig)
pre_save.connect(update_cache_rest_config, sender=RestConfig)
pre_save.connect(update_cache_max_rest_config, sender=MaxRestConfig)
pre_save.connect(update_cache_rir_config, sender=RiRConfig)

pre_delete.connect(update_cache_routine, sender=Routine)
pre_delete.connect(update_cache_day, sender=Day)
pre_delete.connect(update_cache_slot, sender=Slot)
pre_delete.connect(update_cache_slot_config, sender=SlotConfig)
pre_delete.connect(update_cache_weight_config, sender=WeightConfig)
pre_delete.connect(update_cache_max_weight_config, sender=MaxWeightConfig)
pre_delete.connect(update_cache_reps_config, sender=RepsConfig)
pre_delete.connect(update_cache_max_reps_config, sender=MaxRepsConfig)
pre_delete.connect(update_cache_sets_config, sender=SetsConfig)
pre_delete.connect(update_cache_rest_config, sender=RestConfig)
pre_delete.connect(update_cache_max_rest_config, sender=MaxRestConfig)
pre_delete.connect(update_cache_rir_config, sender=RiRConfig)
