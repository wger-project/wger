# -*- coding: utf-8 -*-

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

from wger.main import fs2unicode

'''
This file contains the global settings that don't usually need to be changed.
For a full list of options, visit:
    https://docs.djangoproject.com/en/dev/ref/settings/
'''

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))


#
# Application definition
#
SITE_ID = 1
ROOT_URLCONF = 'wger.urls'
WSGI_APPLICATION = 'wger.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django_browserid',  # Load after auth to monkey-patch it.
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Uncomment the next line to enable the admin:
    'django.contrib.admin',

    # Apps from wger proper
    'wger.core',
    'wger.manager',
    'wger.weight',
    'wger.exercises',
    'wger.nutrition',
    'wger.software',
    'wger.utils',
    'wger.config',
    'wger.gym',

    # reCaptcha support, see https://github.com/praekelt/django-recaptcha
    'captcha',

    # The sitemaps app
    'django.contrib.sitemaps',

    # Django mobile
    'django_mobile',

    # thumbnails
    'easy_thumbnails',

    # CSS/JS compressor
    'compressor',

    # REST-API
    'tastypie',
    'rest_framework',
    'rest_framework.authtoken',

    # Breadcrumbs
    'django_bootstrap_breadcrumbs',

    # CORS
    'corsheaders',
)

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    # Custom authentication middleware. Creates users on-the-fly for certain paths
    'wger.utils.middleware.WgerAuthenticationMiddleware',

    # Send an appropriate Header so search engines don't index pages
    'wger.utils.middleware.RobotsExclusionMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',

    # Django mobile
    'django_mobile.middleware.MobileDetectionMiddleware',
    'django_mobile.middleware.SetFlavourMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_browserid.auth.BrowserIDBackend',
)

# Set the context processors
TEMPLATE_CONTEXT_PROCESSORS = (
    'wger.utils.context_processor.processor',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',

    # Django mobile
    'django_mobile.context_processors.flavour',

    # Breadcrumbs
    'django.core.context_processors.request'
)

TEMPLATE_LOADERS = (
    # Django mobile
    'django_mobile.loader.Loader',

    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# Store the user messages in the session
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',

    # Django compressor
    'compressor.finders.CompressorFinder',
)


#
# Email
#
EMAIL_SUBJECT_PREFIX = '[wger] '
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


#
# Login
#
LOGIN_URL = '/user/login'
LOGIN_REDIRECT_URL = '/'


#
# Internationalization
#
USE_TZ = True
USE_I18N = True
USE_L10N = True

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = None

# Restrict the available languages
LANGUAGES = (
            ('en', 'English'),
            ('de', 'German'),
            ('bg', 'Bulgarian'),
            ('es', 'Spanish'),
            ('ru', 'Russian'),
            ('nl', 'Dutch'),
            ('pt', 'Portuguese'),
)

# Default language code for this installation.
LANGUAGE_CODE = 'en'

# All translation files are in one place
LOCALE_PATHS = (
    fs2unicode(os.path.join(SITE_ROOT, 'locale')),
)

FLAVOURS_STORAGE_BACKEND = 'session'


#
# Logging
#
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'wger.custom': {
            'handlers': ['console', 'mail_admins'],
            'level': 'DEBUG',
        }
    }
}


#
# ReCaptcha
#
RECAPTCHA_USE_SSL = True


#
# Cache
#
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'wger-cache',
        'TIMEOUT': 30 * 24 * 60 * 60,  # Cache for a month
    }
}


#
# Easy thumbnails
#
THUMBNAIL_ALIASES = {
    '': {
        'micro': {'size': (30, 30)},
        'micro_cropped': {'size': (30, 30), 'crop': 'smart'},

        'thumbnail': {'size': (80, 80)},
        'thumbnail_cropped': {'size': (80, 80), 'crop': 'smart'},

        'small': {'size': (200, 200)},
        'small_cropped': {'size': (200, 200), 'crop': 'smart'},

        'medium': {'size': (400, 400)},
        'medium_cropped': {'size': (400, 400), 'crop': 'smart'},

        'large': {'size': (800, 800), 'quality': 90},
        'large_cropped': {'size': (800, 800), 'crop': 'smart', 'quality': 90},
        },
}


#
# Django compressor
#
STATIC_ROOT = ''
STATIC_URL = '/static/'

# The default is not DEBUG, override if needed
# COMPRESS_ENABLED = True
COMPRESS_ROOT = STATIC_ROOT


#
# Django Rest Framework
#
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('wger.utils.permissions.WgerPermission',),
    'PAGINATE_BY': 20,
    'PAGINATE_BY_PARAM': 'limit',  # Allow client to override, using `?limit=xxx`.
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',
                                'rest_framework.filters.OrderingFilter',)
}


#
# CORS headers: allow all hosts to access the API
#
CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^/api/.*$'
