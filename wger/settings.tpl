#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wger
from wger.settings_global import *


# Use 'DEBUG = True' to get more details for server errors
DEBUG = True

# Application settings
WGER_SETTINGS['EMAIL_FROM'] = 'wger Workout Manager <wger@example.com>'
WGER_SETTINGS["ALLOW_REGISTRATION"] = True
WGER_SETTINGS["ALLOW_GUEST_USERS"] = True
WGER_SETTINGS["ALLOW_UPLOAD_VIDEOS"] = False
WGER_SETTINGS["MIN_ACCOUNT_AGE_TO_TRUST"] = 21  # in days
WGER_SETTINGS["EXERCISE_CACHE_TTL"] = 3600  # in seconds

DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.{dbengine}',
        'NAME': '{dbname}',
        'USER': '{dbuser}',
        'PASSWORD': '{dbpassword}',
        'HOST': '{dbhost}',
        'PORT': '{dbport}',
    }}
}}  # yapf: disable

# List of administrations
ADMINS = (('Your name', 'your_email@example.com'),)
MANAGERS = ADMINS

# SERVER_EMAIL = 'info@my-domain.com'
# The email address that error messages (and only error messages, such as
# internal server errors) come from, such as those sent to ADMINS and MANAGERS.

# Timezone for this installation. Consult settings_global.py for more information
TIME_ZONE = 'Europe/Berlin'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '{default_key}'

# Your reCaptcha keys
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
USE_RECAPTCHA = False

# The site's URL (e.g. http://www.my-local-gym.com or http://localhost:8000)
# This is needed for uploaded files and images (exercise images, etc.) to be
# properly served.
SITE_URL = '{siteurl}'

# Path to uploaded files
# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = '{media_folder_path}'
MEDIA_URL = '/media/'

# Allow all hosts to access the application. Change if used in production.
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
# AXES_FAILURE_LIMIT = 10
# AXES_COOLOFF_TIME = timedelta(minutes=30)
# AXES_HANDLER = 'axes.handlers.cache.AxesCacheHandler'

#
# Sometimes needed if deployed behind a proxy with HTTPS enabled:
# https://docs.djangoproject.com/en/4.1/ref/csrf/
#
# CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1', 'https://my.domain.example.com']

# Alternative to above, needs changes to the reverse proxy's config
# https://docs.djangoproject.com/en/4.1/ref/settings/#secure-proxy-ssl-header
#
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO, 'https')

#
# Celery
# Needed if you plan to use celery for background tasks
# CELERY_BROKER_URL = "redis://localhost:6379/2"
# CELERY_RESULT_BACKEND = "redis://localhost:6379/2"
