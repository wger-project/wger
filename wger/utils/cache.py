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

import logging
import hashlib

from django.core.cache import cache
from django.utils.encoding import force_bytes


logger = logging.getLogger(__name__)


def get_template_cache_name(fragment_name='', *args):
    '''
    Logic to calculate the cache key name when using django's template cache.
    Code taken from django/templatetags/cache.py
    '''
    key = u':'.join([str(arg) for arg in args])
    key_name = hashlib.md5(force_bytes(key)).hexdigest()
    return 'template.cache.{0}.{1}'.format(fragment_name, key_name)


def delete_template_fragment_cache(fragment_name='', *args):
    '''
    Deletes a cache key created on the template with django's cache tag
    '''
    cache.delete(get_template_cache_name(fragment_name, *args))


def reset_workout_canonical_form(workout_id):
    cache.delete(cache_mapper.get_workout_canonical(workout_id))


def reset_workout_log(user_pk, year, month, day=None):
    '''
    Resets the cached workout logs
    '''

    log_hash = hash((user_pk, year, month))
    cache.delete(cache_mapper.get_workout_log_list(log_hash))

    log_hash = hash((user_pk, year, month, day))
    cache.delete(cache_mapper.get_workout_log_list(log_hash))


class CacheKeyMapper(object):
    '''
    Simple class for mapping the cache keys of different objects
    '''

    # Keys used by the cache
    LANGUAGE_CACHE_KEY = 'language-{0}'
    LANGUAGE_CONFIG_CACHE_KEY = 'language-config-{0}-{1}'
    EXERCISE_CACHE_KEY_MUSCLE_BG = 'exercise-muscle-bg-{0}'
    INGREDIENT_CACHE_KEY = 'ingredient-{0}'
    WORKOUT_CANONICAL_REPRESENTATION = 'workout-canonical-representation-{0}'
    WORKOUT_LOG_LIST = 'workout-log-hash-{0}'

    def get_pk(self, param):
        '''
        Small helper function that returns the PK for the given parameter
        '''
        try:
            pk = param.pk
        except AttributeError:
            pk = param

        return pk

    def get_exercise_muscle_bg_key(self, param):
        '''
        Return the exercise muscle background cache key
        '''
        return self.EXERCISE_CACHE_KEY_MUSCLE_BG.format(self.get_pk(param))

    def get_language_key(self, param):
        '''
        Return the language cache key
        '''
        return self.LANGUAGE_CACHE_KEY.format(self.get_pk(param))

    def get_language_config_key(self, param, item):
        '''
        Return the language cache key
        '''
        return self.LANGUAGE_CONFIG_CACHE_KEY.format(self.get_pk(param), item)

    def get_ingredient_key(self, param):
        '''
        Return the ingredient cache key
        '''
        return self.INGREDIENT_CACHE_KEY.format(self.get_pk(param))

    def get_workout_canonical(self, param):
        '''
        Return the workout canonical representation
        '''
        return self.WORKOUT_CANONICAL_REPRESENTATION.format(self.get_pk(param))

    def get_workout_log_list(self, hash_value):
        '''
        Return the workout canonical representation
        '''
        return self.WORKOUT_LOG_LIST.format(hash_value)

cache_mapper = CacheKeyMapper()
