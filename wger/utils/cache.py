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


def delete_template_fragment_cache(fragment_name='', vary_on=None):
    """
    Deletes a cache key created on the template with django's cache tag
    """
    out = vary_on if isinstance(vary_on, (list, tuple)) else [vary_on]
    cache.delete(make_template_fragment_key(fragment_name, out))


def reset_workout_canonical_form(workout_id):
    cache.delete(cache_mapper.get_workout_canonical(workout_id))


def reset_exercise_api_cache(uuid: str):
    cache.delete(CacheKeyMapper.get_exercise_api_key(uuid))


def reset_workout_log(user_pk, year, month, day=None):
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

    # Keys used by the cache
    LANGUAGE_CACHE_KEY = 'language-{0}'
    INGREDIENT_CACHE_KEY = 'ingredient-{0}'
    WORKOUT_CANONICAL_REPRESENTATION = 'workout-canonical-representation-{0}'
    WORKOUT_LOG_LIST = 'workout-log-hash-{0}'
    NUTRITION_CACHE_KEY = 'nutrition-cache-log-{0}'
    EXERCISE_API_KEY = 'base-uuid-{0}'

    def get_pk(self, param):
        """
        Small helper function that returns the PK for the given parameter
        """
        return param.pk if hasattr(param, 'pk') else param

    def get_language_key(self, param):
        """
        Return the language cache key
        """
        return self.LANGUAGE_CACHE_KEY.format(self.get_pk(param))

    def get_ingredient_key(self, param):
        """
        Return the ingredient cache key
        """
        return self.INGREDIENT_CACHE_KEY.format(self.get_pk(param))

    def get_workout_canonical(self, param):
        """
        Return the workout canonical representation
        """
        return self.WORKOUT_CANONICAL_REPRESENTATION.format(self.get_pk(param))

    def get_workout_log_list(self, hash_value):
        """
        Return the workout canonical representation
        """
        return self.WORKOUT_LOG_LIST.format(hash_value)

    def get_nutrition_cache_by_key(self, params):
        """
        get nutritional info values canonical representation  using primary key.
        """
        return self.NUTRITION_CACHE_KEY.format(self.get_pk(params))

    @classmethod
    def get_exercise_api_key(cls, base_uuid: str):
        """
        get the exercise base cache key used in the API
        """
        return cls.EXERCISE_API_KEY.format(base_uuid)


cache_mapper = CacheKeyMapper()
