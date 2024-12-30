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
from decimal import Decimal


# Navigation
WORKOUT_TAB = 'workout'
EXERCISE_TAB = 'exercises'
WEIGHT_TAB = 'weight'
NUTRITION_TAB = 'nutrition'
SOFTWARE_TAB = 'software'
USER_TAB = 'user'

# Default quantization
TWOPLACES = Decimal('0.01')
FOURPLACES = Decimal('0.0001')

# Valid date formats
DATE_FORMATS = [
    '%d.%m.%Y',  # '25.10.2012'
    '%d.%m.%y',  # '25.10.12'
    '%m/%d/%Y',  # '10/25/2012'
    '%m/%d/%y',  # '10/25/12'
    '%Y-%m-%d',  # '2012-10-25'
]

# Allowed tags, attributes and styles allowed in textareas edited with a JS
# editor. Everything not in these whitelists is stripped.
HTML_TAG_WHITELIST = {'b', 'i', 'strong', 'em', 'ul', 'ol', 'li', 'p'}
HTML_ATTRIBUTES_WHITELIST = {'*': 'style'}
HTML_STYLES_WHITELIST = ('text-decoration',)

# Pagination
PAGINATION_OBJECTS_PER_PAGE = 25
PAGINATION_MAX_TOTAL_PAGES = 10
PAGINATION_PAGES_AROUND_CURRENT = 5

# Important license IDs
CC_BY_SA_4_ID = 2
CC_BY_SA_3_LICENSE_ID = 1
CC_0_LICENSE_ID = 3
ODBL_LICENSE_ID = 5

# Default/fallback language
ENGLISH_SHORT_NAME = 'en'

# Possible values for ingredient image download
DOWNLOAD_INGREDIENT_WGER = 'WGER'
DOWNLOAD_INGREDIENT_OFF = 'OFF'
DOWNLOAD_INGREDIENT_NONE = 'None'
DOWNLOAD_INGREDIENT_OPTIONS = (
    DOWNLOAD_INGREDIENT_WGER,
    DOWNLOAD_INGREDIENT_OFF,
    DOWNLOAD_INGREDIENT_NONE,
)

# API
API_MAX_ITEMS = 999
SEARCH_ALL_LANGUAGES = '*'
