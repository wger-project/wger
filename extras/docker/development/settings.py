#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wger
from wger.settings_global import *

# Third Party
import environ


env = environ.Env(
    # set casting, default value
    DJANGO_DEBUG=(bool, False)
)

# Use 'DEBUG = True' to get more details for server errors
DEBUG = env("DJANGO_DEBUG")

ADMINS = (
    ('Your name', 'your_email@example.com'),
)
MANAGERS = ADMINS

if os.environ.get("DJANGO_DB_ENGINE"):
    DATABASES = {
        'default': {
            'ENGINE': env.str("DJANGO_DB_ENGINE"),
            'NAME': env.str("DJANGO_DB_DATABASE"),
            'USER': env.str("DJANGO_DB_USER"),
            'PASSWORD': env.str("DJANGO_DB_PASSWORD"),
            'HOST': env.str("DJANGO_DB_HOST"),
            'PORT': env.int("DJANGO_DB_PORT"),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/home/wger/db/database.sqlite',
        }
    }

# Timezone for this installation. Consult settings_global.py for more information
TIME_ZONE = env.str("TIME_ZONE", 'Europe/Berlin')

# Make this unique, and don't share it with anybody.
SECRET_KEY = env.str("SECRET_KEY", 'wger-docker-supersecret-key-1234567890!@#$%^&*(-_)')


# Your reCaptcha keys
RECAPTCHA_PUBLIC_KEY = env.str('RECAPTCHA_PUBLIC_KEY', '')
RECAPTCHA_PRIVATE_KEY = env.str('RECAPTCHA_PRIVATE_KEY', '')

# The site's URL (e.g. http://www.my-local-gym.com or http://localhost:8000)
# This is needed for uploaded files and images (exercise images, etc.) to be
# properly served.
SITE_URL = env.str('SITE_URL', 'http://localhost:8000')

# Path to uploaded files
# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = env.str("DJANGO_MEDIA_ROOT", '/home/wger/media')
STATIC_ROOT = env.str("DJANGO_STATIC_ROOT", '/home/wger/static')

# If you change these, adjust nginx alias definitions as well
MEDIA_URL = env.str('MEDIA_URL', '/media/')
STATIC_URL = env.str('STATIC_URL', '/static/')

LOGIN_REDIRECT_URL = env.str('LOGIN_REDIRECT_URL', '/')

# Allow all hosts to access the application. Change if used in production.
ALLOWED_HOSTS = '*'

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

# Configure a real backend in production
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
if os.environ.get("ENABLE_EMAIL"):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = env.str("EMAIL_HOST")
    EMAIL_PORT = env.int("EMAIL_PORT")
    EMAIL_HOST_USER = env.str("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD")
    EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", True)
    EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", True)
    EMAIL_TIMEOUT = 60


# Sender address used for sent emails
WGER_SETTINGS['EMAIL_FROM'] = f'wger Workout Manager <{env.str("FROM_EMAIL")}>'
DEFAULT_FROM_EMAIL = WGER_SETTINGS['EMAIL_FROM']

# Management
WGER_SETTINGS["ALLOW_REGISTRATION"] = env.bool("ALLOW_REGISTRATION", True)
WGER_SETTINGS["ALLOW_GUEST_USERS"] = env.bool("ALLOW_GUEST_USERS", True)
WGER_SETTINGS["ALLOW_UPLOAD_VIDEOS"] = env.bool("ALLOW_UPLOAD_VIDEOS", True)
WGER_SETTINGS["EXERCISE_CACHE_TTL"] = env.int("EXERCISE_CACHE_TTL", 3600)


# Cache
if os.environ.get("DJANGO_CACHE_BACKEND"):
    CACHES = {
        'default': {
            'BACKEND': env.str("DJANGO_CACHE_BACKEND"),
            'LOCATION': env.str("DJANGO_CACHE_LOCATION"),
            'TIMEOUT': env.int("DJANGO_CACHE_TIMEOUT"),
            'OPTIONS': {
                'CLIENT_CLASS': env.str("DJANGO_CACHE_CLIENT_CLASS"),
            }
        }
    }

# Folder for compressed CSS and JS files
COMPRESS_ROOT = STATIC_ROOT

# The site's domain as used by the email verification workflow
EMAIL_PAGE_DOMAIN = 'http://localhost/'


# Django Axes
AXES_ENABLED = True  # allow to disable axes entirely (e.g. if this is run in a local network or so we would save up some resources), but default is true
AXES_FAILURE_LIMIT = 5  # configurable, default is 5
AXES_COOLOFF_TIME = 0.5  # configurable, default is 0.5 hours
AXES_HANDLER = 'axes.handlers.cache.AxesCacheHandler'  # Configurable, but default is the cache handler

#
# Django Rest Framework SimpleJWT
#
SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] = timedelta(minutes=env.int("ACCESS_TOKEN_LIFETIME", 15))
SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'] = timedelta(hours=env.int("REFRESH_TOKEN_LIFETIME", 24))
SIMPLE_JWT['SIGNING_KEY'] = env.str("SIGNING_KEY", SECRET_KEY)