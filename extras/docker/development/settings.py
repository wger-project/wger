#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wger
from wger.settings_global import *


# Use 'DEBUG = True' to get more details for server errors
DEBUG = os.environ.get("DJANGO_DEBUG", True)

ADMINS = (
    ('Your name', 'your_email@example.com'),
)
MANAGERS = ADMINS

if os.environ.get("DJANGO_DB_ENGINE"):
    DATABASES = {
        'default': {
            'ENGINE': os.environ.get("DJANGO_DB_ENGINE"),
            'NAME': os.environ.get("DJANGO_DB_DATABASE"),
            'USER': os.environ.get("DJANGO_DB_USER"),
            'PASSWORD': os.environ.get("DJANGO_DB_PASSWORD"),
            'HOST': os.environ.get("DJANGO_DB_HOST"),
            'PORT': os.environ.get("DJANGO_DB_PORT"),
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
TIME_ZONE = os.environ.get("TIME_ZONE" , 'Europe/Berlin')

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.environ.get("SECRET_KEY", 'wger-django-secret-key')


# Your reCaptcha keys
RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY', '')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY', '')

# The site's URL (e.g. http://www.my-local-gym.com or http://localhost:8000)
# This is needed for uploaded files and images (exercise images, etc.) to be
# properly served.
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8000')

# Path to uploaded files
# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = os.environ.get("DJANGO_MEDIA_ROOT", '/home/wger/media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.environ.get("DJANGO_STATIC_ROOT", '/home/wger/static')

# Allow all hosts to access the application. Change if used in production.
ALLOWED_HOSTS = '*'

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

# Configure a real backend in production
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
if os.environ.get("ENABLE_EMAIL"):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get("EMAIL_HOST")
    EMAIL_PORT = os.environ.get("EMAIL_PORT")
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
    EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS")
    EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL")
    EMAIL_TIMEOUT = 60


# Sender address used for sent emails
WGER_SETTINGS['EMAIL_FROM'] = f'wger Workout Manager <{os.environ.get("FROM_EMAIL")}>'
DEFAULT_FROM_EMAIL = WGER_SETTINGS['EMAIL_FROM']

# Management
if os.environ.get("ALLOW_REGISTRATION") == 'False':
    WGER_SETTINGS["ALLOW_REGISTRATION"] = False
else:
    WGER_SETTINGS["ALLOW_REGISTRATION"] = True

if os.environ.get("ALLOW_GUEST_USERS") == 'False':
    WGER_SETTINGS["ALLOW_GUEST_USERS"] = False
else:
    WGER_SETTINGS["ALLOW_GUEST_USERS"] = True

# Cache
if os.environ.get("DJANGO_CACHE_BACKEND"):
    CACHES = {
        'default': {
            'BACKEND': os.environ.get("DJANGO_CACHE_BACKEND"),
            'LOCATION': os.environ.get("DJANGO_CACHE_LOCATION"),
            'TIMEOUT': os.environ.get("DJANGO_CACHE_TIMEOUT"),
            'OPTIONS': {
                'CLIENT_CLASS': os.environ.get("DJANGO_CACHE_CLIENT_CLASS"),
            }
        }
    }

# Folder for compressed CSS and JS files
COMPRESS_ROOT = STATIC_ROOT
