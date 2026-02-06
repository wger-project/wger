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

# ruff: noqa: F405

# Third Party
import environ

# wger
from .settings_global import *  # noqa: F403

env = environ.Env()

# Use 'DEBUG = True' to get more details for server errors
DEBUG = True

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
        'NAME': '/Users/roland/Entwicklung/wger/server/database.sqlite',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}  # yapf: disable

# List of administrations
ADMINS = (('Your name', 'your_email@example.com'),)
MANAGERS = ADMINS

# SERVER_EMAIL = 'info@my-domain.com'
# The email address that error messages (and only error messages, such as
# internal server errors) come from, such as those sent to ADMINS and MANAGERS.

# Timezone for this installation. Consult settings_global.py for more information
TIME_ZONE = 'Europe/Berlin'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '61fxc$k%9nj!be-_up9%xzm(z)9l7$h33b1!@bf9581=c-03%p'

# Your reCaptcha keys
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
USE_RECAPTCHA = False

# The site's URL (e.g. http://www.my-local-gym.com or http://localhost:8000)
# This is needed for uploaded files and images (exercise images, etc.) to be
# properly served.
SITE_URL = 'http://localhost:8000'

# Path to uploaded files
# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = env.str('DJANGO_MEDIA_ROOT', '/tmp/')
MEDIA_URL = '/media/'

# Allow all hosts to access the application.
ALLOWED_HOSTS = [
    '*',
]

# This might be a good idea if you set up redis
# SESSION_ENGINE = "django.contrib.sessions.backends.cache"

# Configure a real backend in production
# See: https://docs.djangoproject.com/en/dev/topics/email/#email-backends
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_FROM_EMAIL = WGER_SETTINGS['EMAIL_FROM']

# The site's domain as used by the email verification workflow
EMAIL_PAGE_DOMAIN = SITE_URL

#
# https://django-axes.readthedocs.io/en/latest/
#
AXES_ENABLED = False
