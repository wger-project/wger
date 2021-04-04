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

# Standard Library
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import re
"""
This file contains the global settings that don't usually need to be changed.
For a full list of options, visit:
    https://docs.djangoproject.com/en/dev/ref/settings/
"""

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

#
# Application definition
#
SITE_ID = 1
ROOT_URLCONF = 'wger.urls'
WSGI_APPLICATION = 'wger.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django_extensions',
    'storages',

    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',

    # Apps from wger proper
    'wger.config',
    'wger.core',
    'wger.mailer',
    'wger.exercises',
    'wger.gym',
    'wger.manager',
    'wger.nutrition',
    'wger.software',
    'wger.utils',
    'wger.weight',

    # reCaptcha support, see https://github.com/praekelt/django-recaptcha
    'captcha',

    # The sitemaps app
    'django.contrib.sitemaps',

    # thumbnails
    'easy_thumbnails',

    # CSS/JS compressor
    'compressor',

    # Form renderer helper
    'crispy_forms',

    # REST-API
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',

    # Breadcrumbs
    'django_bootstrap_breadcrumbs',

    # CORS
    'corsheaders',
    #social Authentication
    'social_django',
)

MIDDLEWARE = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    # Django Admin
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    # Javascript Header. Sends helper headers for AJAX
    'wger.utils.middleware.JavascriptAJAXRedirectionMiddleware',

    # Custom authentication middleware. Creates users on-the-fly for certain paths
    'wger.utils.middleware.WgerAuthenticationMiddleware',

    # Send an appropriate Header so search engines don't index pages
    'wger.utils.middleware.RobotsExclusionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'social_core.backends.linkedin.LinkedinOAuth2',
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.github.GithubOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'wger.utils.context_processor.processor',

                # Django
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',

                #Social_Django
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',

                # Breadcrumbs
                'django.template.context_processors.request'
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'debug':
            False
        },
    },
]

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
LOGIN_REDIRECT_URL = '/dashboard'
LOGOUT_URL = 'logout'
LOGOUT_REDIRECT_URL = '/user/login'

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
TIME_ZONE = 'UTC'

# Restrict the available languages
LANGUAGES = (
    ('en', 'English'),
    ('de', 'German'),
    ('bg', 'Bulgarian'),
    ('es', 'Spanish'),
    ('ru', 'Russian'),
    ('nl', 'Dutch'),
    ('pt', 'Portuguese'),
    ('el', 'Greek'),
    ('cs', 'Czech'),
    ('sv', 'Swedish'),
    ('no', 'Norwegian'),
    ('fr', 'French'),
    ('it', 'Italian'),
    ('pl', 'Polish'),
    ('uk', 'Ukrainian'),
    ('tr', 'Turkish'),
)

# Default language code for this installation.
LANGUAGE_CODE = 'en'

# All translation files are in one place
LOCALE_PATHS = (os.path.join(SITE_ROOT, 'locale'), )

#
# Logging
# See http://docs.python.org/library/logging.config.html
#
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'wger': {
            'handlers': ['console'],
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
# Django Crispy Templates
#
CRISPY_TEMPLATE_PACK = 'bootstrap4'

#
# Easy thumbnails
#
THUMBNAIL_ALIASES = {
    '': {
        'micro': {
            'size': (30, 30)
        },
        'micro_cropped': {
            'size': (30, 30),
            'crop': 'smart'
        },
        'thumbnail': {
            'size': (80, 80)
        },
        'thumbnail_cropped': {
            'size': (80, 80),
            'crop': 'smart'
        },
        'small': {
            'size': (200, 200)
        },
        'small_cropped': {
            'size': (200, 200),
            'crop': 'smart'
        },
        'medium': {
            'size': (400, 400)
        },
        'medium_cropped': {
            'size': (400, 400),
            'crop': 'smart'
        },
        'large': {
            'size': (800, 800),
            'quality': 90
        },
        'large_cropped': {
            'size': (800, 800),
            'crop': 'smart',
            'quality': 90
        },
    },
}

STATIC_ROOT = ''
USE_S3 = os.getenv('USE_S3') == 'TRUE'

if USE_S3:
    # aws settings
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_CUSTOM_DOMAIN = os.getenv('WGER_CDN_DOMAIN')
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=31557600'}
    # s3 static settings
    AWS_LOCATION = 'static'
    STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    COMPRESS_URL = STATIC_URL
    COMPRESS_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    COMPRESS_OFFLINE = True
    COMPRESS_OFFLINE_CONTEXT = [{
        'request': {
            'user_agent': {
                'is_mobile': True
            }
        },
        'STATIC_URL': STATIC_URL
    }, {
        'request': {
            'user_agent': {
                'is_mobile': False
            }
        },
        'STATIC_URL': STATIC_URL
    }]
else:
    STATIC_URL = '/static/'

#
# Django compressor
#

# The default is not DEBUG, override if needed
# COMPRESS_ENABLED = True
COMPRESS_CSS_FILTERS = ('compressor.filters.css_default.CssAbsoluteFilter',
                        'compressor.filters.cssmin.rCSSMinFilter')
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
    'compressor.filters.template.TemplateFilter',
]
COMPRESS_ROOT = STATIC_ROOT

#
# Django Rest Framework
#
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('wger.utils.permissions.WgerPermission', ),
    'DEFAULT_PAGINATION_CLASS':
    'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE':
    20,
    'PAGINATE_BY_PARAM':
    'limit',  # Allow client to override, using `?limit=xxx`.
    'TEST_REQUEST_DEFAULT_FORMAT':
    'json',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS':
    ('django_filters.rest_framework.DjangoFilterBackend',
     'rest_framework.filters.OrderingFilter'),
    'DEFAULT_THROTTLE_CLASSES':
    ['rest_framework.throttling.ScopedRateThrottle'],
    'DEFAULT_THROTTLE_RATES': {
        'login': '3/min'
    }
}

#
# CORS headers: allow all hosts to access the API
#
CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^/api/.*$'

#
# Ignore these URLs if they cause 404
#
IGNORABLE_404_URLS = (re.compile(r'^/favicon\.ico$'), )

#
# Password rules
#
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

USER_AGENTS_CACHE = 'default'

#
# Application specific configuration options
#
# Consult docs/settings.rst for more information
#
WGER_SETTINGS = {
    'USE_RECAPTCHA': False,
    'REMOVE_WHITESPACE': False,
    'ALLOW_REGISTRATION': True,
    'ALLOW_GUEST_USERS': True,
    'EMAIL_FROM': 'wger Workout Manager <wger@example.com>',
    'TWITTER': False
}

SOCIAL_AUTH_FACEBOOK_KEY = "961524321254840"
SOCIAL_AUTH_FACEBOOK_SECRET = 'ce5af1f199d033cb3a946544fa91962f'

SOCIAL_AUTH_GITHUB_KEY = 'c0c53a42aa56aa6a233f'
SOCIAL_AUTH_GITHUB_SECRET = '3123c7edbf6931b9022764f57f46501a7ae7b68c'

SOCIAL_AUTH_TWITTER_KEY = 'OggysVyw1nkH6p5VQCWXH1wFT'
SOCIAL_AUTH_TWITTER_SECRET = 'BPnLkLT2UJP2TWBxNu9IJSP8Y6SQKpDEDMUJ6RA0LgOPJZIHZ6'
