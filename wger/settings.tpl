#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wger.settings_global import *

# Use 'DEBUG = True' to get more details for server errors
DEBUG = True
TEMPLATES[0]['OPTIONS']['debug'] = True

ADMINS = (
    ('Your name', 'your_email@example.com'),
)
MANAGERS = ADMINS


DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.{dbengine}',
        'NAME': {dbname},
        'USER': '{dbuser}',
        'PASSWORD': '{dbpassword}',
        'HOST': '{dbhost}',
        'PORT': '{dbport}',
    }}
}}

# Make this unique, and don't share it with anybody.
SECRET_KEY = '{default_key}'

# Your reCaptcha keys
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
NOCAPTCHA = True

# The site's URL (e.g. http://www.my-local-gym.com or http://localhost:8000)
# This is needed for uploaded files and images (exercise images, etc.) to be
# properly served.
SITE_URL = '{siteurl}'

# Path to uploaded files
# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = {media_folder_path}
MEDIA_URL = '/media/'

# Allow all hosts to access the application. Change if used in production.
ALLOWED_HOSTS = '*'

# This might be a good idea if you setup memcached
#SESSION_ENGINE = "django.contrib.sessions.backends.cache"

# Configure a real backend in production
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Sender address used for sent emails
WGER_SETTINGS['EMAIL_FROM'] = 'wger Workout Manager <wger@example.com>'

# Your twitter handle, if you have one for this instance.
#WGER_SETTINGS['TWITTER'] = ''
