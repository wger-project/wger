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

# Valid datetime formats
DATETIME_FORMATS = [
    '%d.%m.%Y %H:%M:%S',  # '25.10.2012 14:30:00'
    '%d.%m.%Y %H:%M',  # '25.10.2012 14:30'
    '%d.%m.%y %H:%M:%S',  # '25.10.12 14:30:00'
    '%d.%m.%y %H:%M',  # '25.10.12 14:30'
    '%m/%d/%Y %H:%M:%S',  # '10/25/2012 14:30:00'
    '%m/%d/%Y %H:%M',  # '10/25/2012 14:30'
    '%m/%d/%y %H:%M:%S',  # '10/25/12 14:30:00'
    '%m/%d/%y %H:%M',  # '10/25/12 14:30'
    '%Y-%m-%d %H:%M:%S',  # '2012-10-25 14:30:00'
    '%Y-%m-%d %H:%M',  # '2012-10-25 14:30'
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
CC_BY_SA_4_LICENSE_ID = 2
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

# Known exercises
UUID_SQUATS = 'a2f5b6ef-b780-49c0-8d96-fdaff23e27ce'
UUID_CURLS = '1ae6a28d-10e7-4ecf-af4f-905f8193e2c6'
UUID_FRENCH_PRESS = '95a7e546-e8f8-4521-a76b-983d94161b25'
UUID_CRUNCHES = 'b186f1f8-4957-44dc-bf30-d0b00064ce6f'
UUID_LEG_RAISES = 'c2078aac-e4e2-4103-a845-6252a3eb795e'

CHARACTERS_TO_REMOVE_FROM_INGREDIENT_NAME: set[str] = {
    '\x8a',
    '\x83',
    '\x8f',
    '\x8d',
    '\x82',
    '\x9a',
    '\x89',
    '\x99',
    '\x87',
    '\x9c',
    '\x80',
    '\x96',
    '\t',
    '\x92',
    '\x8c',
    '\x90',
    '\x9f',
    '\x84',
    '\x97',
    '\x93',
    '\x98',
    '\x85',
}

HTML_ENTITY_TO_HUMAN_READABLE_MAP = {
    '&quot;': '"',
    '&gt;': '>',
    '&lt;': '<',
    '&amp;': '&',
    '&deg;': '°',
    '&euro;': '€',
    '&oelig;': 'œ',
    '&lsquo;': '‘',
    '&#40;': '(',
    '&#040;': '(',
    '&#41;': ')',
    '&#041;': ')',
    '&#34;': '"',
    '&#034;': '"',
    '&#39;': "'",
    '&#039;': "'",
    '&#47;': '/',
    '&#047;': '/',
    '&#37;': '%',
    '&#037;': '%',
    '&#38;': '&',
    '&#038;': '&',
    '&#322;': 'ł',
    '&#347;': 'ś',
    '&#324;': 'ń',
    '&#261;': 'ą',
    '&#281;': 'ę',
    '&#231;': 'ç',
    '&#180;': '´',
    '&#91;': '[',
    '&#091;': '[',
    '&#93;': ']',
    '&#093;': ']',
    '&#x27;': "'",
}

HTML_ENTITY_PATTERN = r'&[a-zA-Z0-9#x]+;'
