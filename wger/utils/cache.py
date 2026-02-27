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

# Standard Library
import logging

# Django
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key


logger = logging.getLogger(__name__)


def reset_exercise_api_cache(uuid: str):
    cache.delete(CacheKeyMapper.get_exercise_api_key(uuid))


def reset_workout_log_cache(user_pk, year, month, day=None):
    """
    Resets the cached workout logs
    """

    log_hash = hash((user_pk, year, month))
    cache.delete(cache_mapper.get_workout_log_list(log_hash))

    log_hash = hash((user_pk, year, month, day))
    cache.delete(cache_mapper.get_workout_log_list(log_hash))


class CacheKeyMapper:
    """
    Simple class for mapping the cache keys of different objects
    """

    def get_pk(self, param):
        """
        Small helper function that returns the PK for the given parameter
        """
        return param.pk if hasattr(param, 'pk') else param

    def get_language_key(self, param):
        """
        Return the language cache key
        """
        return f'language-{self.get_pk(param)}'

    def get_ingredient_key(self, param):
        """
        Return the ingredient cache key
        """
        return f'ingredient-{self.get_pk(param)}'

    def get_workout_log_list(self, hash_value):
        """
        Return the workout canonical representation
        """
        return f'workout-log-hash-{hash_value}'

    def get_nutrition_cache_by_key(self, params):
        """
        get nutritional info values canonical representation  using primary key.
        """
        return f'nutrition-cache-log-{self.get_pk(params)}'

    @classmethod
    def get_exercise_api_key(cls, base_uuid: str):
        """
        get the exercise base cache key used in the API
        """
        return f'base-uuid-{base_uuid}'

    @classmethod
    def routine_date_sequence_key(cls, pk: int):
        return f'routine-date-sequence-{pk}'

    @classmethod
    def routine_api_date_sequence_display_key(cls, pk: int, user_id: int):
        return f'routine-api-date-sequence-display-{user_id}-{pk}'

    @classmethod
    def routine_api_date_sequence_gym_key(cls, pk: int, user_id: int):
        return f'routine-api-date-sequence-gym-{user_id}-{pk}'

    @classmethod
    def routine_api_stats(cls, pk: int, user_id: int):
        return f'routine-api-stats-{user_id}-{pk}'

    @classmethod
    def routine_api_logs(cls, pk: int, user_id: int):
        return f'routine-api-logs-{user_id}-{pk}'

    @classmethod
    def routine_api_structure_key(cls, pk: int, user_id: int = None):
        return f'routine-api-structure-{user_id}-{pk}'

    @classmethod
    def slot_entry_configs_key(cls, pk: int):
        return f'slot-entry-configs-{pk}'

    @classmethod
    def ingredient_celery_sync(cls, page: int):
        return f'ingredients-sync-page-{page}'


cache_mapper = CacheKeyMapper()
