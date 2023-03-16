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
from datetime import timedelta


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
    'wger.gallery',
    'wger.measurements',

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
    'crispy_bootstrap4',
    # note: bs3 can be deleted when we solve https://github.com/wger-project/wger/issues/1127
    'crispy_bootstrap3',

    # REST-API
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'rest_framework_simplejwt',

    # Breadcrumbs
    'django_bootstrap_breadcrumbs',

    # CORS
    'corsheaders',

    # Django Axes
    'axes',

    # History keeping
    'simple_history',

    # Django email verification
    'django_email_verification',

    # Activity stream
    'actstream',

    # Fontawesome
    'fontawesomefree',
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

    # History keeping
    'simple_history.middleware.HistoryRequestMiddleware',

    # Django Axes
    'axes.middleware.AxesMiddleware',  # should be the last one in the list
)

AUTHENTICATION_BACKENDS = (
    'axes.backends.AxesStandaloneBackend',  # should be the first one in the list
    'django.contrib.auth.backends.ModelBackend',
    'wger.utils.helpers.EmailAuthBackend',
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
TIME_ZONE = 'UTC'

# Available languages. Needs to be kept in sync with sufficiently
# translated languages: https://hosted.weblate.org/projects/wger/web/
#
# Translated languages for which a country specific locale exists in django
# upstream need to be added here as well (plus their country flag)
# https://github.com/django/django/blob/main/django/conf/global_settings.py
AVAILABLE_LANGUAGES = (
    ('bg', 'Bulgarian'),
    ('ca', 'Catalan'),
    ('cs', 'Czech'),
    ('de', 'German'),
    ('el', 'Greek'),
    ('en', 'English'),
    ('en-au', 'Australian English'),
    ('en-gb', 'British English'),
    ('es', 'Spanish'),
    ('es-ar', 'Argentinian Spanish'),
    ('es-co', 'Colombian Spanish'),
    ('es-mx', 'Mexican Spanish'),
    ('es-ni', 'Nicaraguan Spanish'),
    ('es-ve', 'Venezuelan Spanish'),
    ('fr', 'French'),
    ('it', 'Italian'),
    ('nl', 'Dutch'),
    ('no', 'Norwegian'),
    ('pl', 'Polish'),
    ('pt', 'Portuguese'),
    ('pt-br', 'Brazilian Portuguese'),
    ('ru', 'Russian'),
    ('sv', 'Swedish'),
    ('tr', 'Turkish'),
    ('uk', 'Ukrainian'),
    ('zh', 'Chinese simplified'),
)

# Default language code for this installation.
LANGUAGE_CODE = 'en'

# All translation files are in one place
LOCALE_PATHS = (os.path.join(SITE_ROOT, 'locale'), )

# Primary keys are AutoFields
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

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
# Django Axes
#
AXES_ENABLED = True
AXES_FAILURE_LIMIT = 10
AXES_COOLOFF_TIME = timedelta(minutes=30)
AXES_LOCKOUT_TEMPLATE = None
AXES_RESET_ON_SUCCESS = False
AXES_RESET_COOL_OFF_ON_FAILURE_DURING_LOCKOUT = True

# If you want to set up redis, set AXES_HANDLER = 'axes.handlers.cache.AxesCacheHandler'
AXES_HANDLER = 'axes.handlers.database.AxesDatabaseHandler'

# If your redis or MemcachedCache has a different name other than 'default'
# (e.g. when you have multiple caches defined in CACHES), change the following value to that name
AXES_CACHE = 'default'

#
# Django Crispy Templates
#
CRISPY_TEMPLATE_PACK = 'bootstrap4'
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap4'

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
    COMPRESS_OFFLINE_CONTEXT = [
        {
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
        }
    ]
else:
    STATIC_URL = '/static/'

#
# Django compressor
#

# The default is not DEBUG, override if needed
# COMPRESS_ENABLED = True
COMPRESS_CSS_FILTERS = (
    'compressor.filters.css_default.CssAbsoluteFilter', 'compressor.filters.cssmin.rCSSMinFilter'
)
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
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_THROTTLE_CLASSES': ['rest_framework.throttling.ScopedRateThrottle'],
    'DEFAULT_THROTTLE_RATES': {
        'login': '3/min'
    }
}

#
# Django Rest Framework SimpleJWT
#
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,
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
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

USER_AGENTS_CACHE = 'default'

#
# Application specific configuration options
#
# Consult docs/settings.rst for more information
#
WGER_SETTINGS = {
    'ALLOW_GUEST_USERS': True,
    'ALLOW_REGISTRATION': True,
    'ALLOW_UPLOAD_VIDEOS': False,
    'MIN_ACCOUNT_AGE_TO_TRUST': 21,
    'EMAIL_FROM': 'wger Workout Manager <wger@example.com>',
    'EXERCISE_CACHE_TTL': 3600,
    'TWITTER': False,
    'USE_RECAPTCHA': False
}


#
# Django email verification
#
def email_verified_callback(user):
    user.userprofile.email_verified = True
    user.userprofile.save()


EMAIL_VERIFIED_CALLBACK = email_verified_callback
EMAIL_FROM_ADDRESS = WGER_SETTINGS['EMAIL_FROM']
EMAIL_MAIL_SUBJECT = 'Confirm your email'
EMAIL_MAIL_HTML = 'email_verification/email_body_html.tpl'
EMAIL_MAIL_PLAIN = 'email_verification/email_body_txt.tpl'
EMAIL_MAIL_TOKEN_LIFE = 60 * 60
EMAIL_MAIL_PAGE_TEMPLATE = 'email_verification/confirm_template.html'
EMAIL_PAGE_DOMAIN = 'http://localhost:8000/'

#
# Django activity stream
#
ACTSTREAM_SETTINGS = {
    'USE_JSONFIELD': True,
}
