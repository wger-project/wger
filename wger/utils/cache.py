# This file is part of Workout Manager.
#
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

import logging
import hashlib

from django.core.cache import cache
from django.utils.encoding import force_bytes


logger = logging.getLogger('workout_manager.custom')


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


class CacheKeyMapper(object):
    '''
    Simple class for mapping the cache keys of different objects
    '''

    # Keys used by the cache
    LANGUAGE_CACHE_KEY = 'language-{0}'
    LANGUAGE_CONFIG_CACHE_KEY = 'language-config-{0}-{1}'
    EXERCISE_CACHE_KEY = 'exercise-{0}'
    EXERCISE_CACHE_KEY_MUSCLE_BG = 'exercise-muscle-bg-{0}'
    INGREDIENT_CACHE_KEY = 'ingredient-{0}'
    WORKOUT_MUSCLE_BG = 'workout-muscle-bg-{0}'

    def get_exercise_key(self, param):
        '''
        Return the exercise cache key
        '''
        try:
            pk = param.pk
        except AttributeError:
            pk = param

        return self.EXERCISE_CACHE_KEY.format(pk)

    def get_exercise_muscle_bg_key(self, param):
        '''
        Return the exercise muscle background cache key
        '''
        try:
            pk = param.pk
        except AttributeError:
            pk = param

        return self.EXERCISE_CACHE_KEY_MUSCLE_BG.format(pk)

    def get_language_key(self, param):
        '''
        Return the language cache key
        '''
        try:
            pk = param.pk
        except AttributeError:
            pk = param

        return self.LANGUAGE_CACHE_KEY.format(pk)

    def get_language_config_key(self, param, item):
        '''
        Return the language cache key
        '''
        try:
            pk = param.pk
        except AttributeError:
            pk = param

        return self.LANGUAGE_CONFIG_CACHE_KEY.format(pk, item)

    def get_ingredient_key(self, param):
        '''
        Return the ingredient cache key
        '''
        try:
            pk = param.pk
        except AttributeError:
            pk = param

        return self.INGREDIENT_CACHE_KEY.format(pk)

    def get_workout_muscle_bg(self, param):
        '''
        Return the workout muscle background cache key
        '''
        try:
            pk = param.pk
        except AttributeError:
            pk = param

        return self.WORKOUT_MUSCLE_BG.format(pk)

cache_mapper = CacheKeyMapper()
