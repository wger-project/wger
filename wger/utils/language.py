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
from django.utils import translation

# wger
from wger.core.models import Language
from wger.utils.cache import cache_mapper
from wger.utils.constants import ENGLISH_SHORT_NAME


logger = logging.getLogger(__name__)


def load_language(language_code=None):
    """
    Returns the currently used language, e.g. to load appropriate exercises
    """

    # Read the first part of a composite language, e.g. 'de-at'
    used_language = (
        translation.get_language().split('-')[0] if language_code is None else language_code
    )

    language = cache.get(cache_mapper.get_language_key(used_language))
    if language:
        return language

    try:
        language = Language.objects.get(short_name=used_language)
    except Language.DoesNotExist:
        language = Language.objects.get(short_name=ENGLISH_SHORT_NAME)

    cache.set(cache_mapper.get_language_key(language.short_name), language)
    return language


def get_language_data(language):
    return {
        'name': language[1],
        'code': language[0],
        'path': f'images/icons/flags/{language[0]}.svg',
    }
