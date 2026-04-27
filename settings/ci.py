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

# ruff: noqa: F405, F403

# Third Party
import environ

# wger
from .settings_global import *

env = environ.Env()

DEBUG = False

"""
Settings for CI:

The basic changes are

* skip migrations
* use a faster password hasher
* use plain (un-hashed) static file storage
* use an in-memory backend for media files
"""

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

# Application settings
WGER_SETTINGS['EMAIL_FROM'] = 'wger Workout Manager <wger@example.com>'
WGER_SETTINGS['ALLOW_REGISTRATION'] = True
WGER_SETTINGS['ALLOW_GUEST_USERS'] = True
WGER_SETTINGS['ALLOW_UPLOAD_VIDEOS'] = False
WGER_SETTINGS['MIN_ACCOUNT_AGE_TO_TRUST'] = 21  # in days
WGER_SETTINGS['EXERCISE_CACHE_TTL'] = 3600  # in seconds

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'database.sqlite',
        'TEST': {
            'MIGRATE': False,
        },
    }
}

ADMINS = ['"Your name" <your_email@example.com>']
MANAGERS = ADMINS

TIME_ZONE = 'Europe/Berlin'
SECRET_KEY = '61fxc$k%9nj!be-_up9%xzm(z)9l7$h33b1!@bf9581=c-03%p'

RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
USE_RECAPTCHA = False

SITE_URL = 'http://localhost:8000'

MEDIA_ROOT = env.str('DJANGO_MEDIA_ROOT', '/tmp/')
MEDIA_URL = '/media/'

ALLOWED_HOSTS = [
    '*',
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = WGER_SETTINGS['EMAIL_FROM']
EMAIL_PAGE_DOMAIN = SITE_URL
AXES_ENABLED = False

STORAGES = {
    # In-memory storage avoids disk writes for media uploads during tests.
    'default': {
        'BACKEND': 'django.core.files.storage.InMemoryStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}
