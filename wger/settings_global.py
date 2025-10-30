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
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

# Standard Library
import datetime
import os
import re
import sys
from datetime import timedelta

# wger
from wger.utils.constants import DOWNLOAD_INGREDIENT_WGER
from wger.version import get_version


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

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
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

    # hCaptcha (replaces Google reCAPTCHA)
    'hcaptcha',

    # The sitemaps app
    'django.contrib.sitemaps',

    # thumbnails
    'easy_thumbnails',

    # CSS/JS compressor
    'compressor',

    # Form renderer helper
    'crispy_forms',
    'crispy_bootstrap5',

    # REST-API
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'drf_spectacular_sidecar',

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

    # Prometheus
    'django_prometheus',
]

MIDDLEWARE = [
    # Prometheus
    'django_prometheus.middleware.PrometheusBeforeMiddleware',

    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    # Django Admin
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    # Auth proxy middleware
    'wger.core.middleware.AuthProxyHeaderMiddleware',

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

    # Prometheus
    'django_prometheus.middleware.PrometheusAfterMiddleware',

    # Django Axes
    'axes.middleware.AxesMiddleware',  # should be the last one in the list
]

AUTHENTICATION_BACKENDS = (
    'axes.backends.AxesStandaloneBackend',  # should be the first one in the list
    'wger.core.backends.AuthProxyUserBackend',
    'django.contrib.auth.backends.ModelBackend',
    'wger.utils.helpers.EmailAuthBackend',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
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
            'debug': False
        },
    },
]

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

STATICFILES_DIRS = (
    ('node', os.path.join(BASE_DIR, '..', 'node_modules')),
)

#
# Email
#
EMAIL_SUBJECT_PREFIX = '[wger] '

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
USE_THOUSAND_SEPARATOR = True
TIME_ZONE = 'UTC'

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
    ('he', 'Hebrew'),
    ('hr', 'Croatian'),
    ('it', 'Italian'),
    ('ko', 'Korean'),
    ('nl', 'Dutch'),
    ('nb', 'Norwegian'),
    ('pl', 'Polish'),
    ('pt', 'Portuguese'),
    ('pt-br', 'Brazilian Portuguese'),
    ('ru', 'Russian'),
    ('sk', 'Slovak'),
    ('sl', 'Slovenian'),
    ('sr', 'Serbian'),
    ('sv', 'Swedish'),
    ('ta', 'Tamil'),
    ('th', 'Thai'),
    ('tr', 'Turkish'),
    ('uk', 'Ukrainian'),
    ('zh-hans', 'Chinese simplified'),
    ('zh-hant', 'Traditional Chinese'),
)

LANGUAGE_CODE = 'en'
LOCALE_PATHS = (os.path.join(SITE_ROOT, 'locale'),)
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

#
# Logging
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
            'level': 'INFO',
        },
    }
}

#
# hCaptcha (replaces Google reCAPTCHA)
#
HCAPTCHA_SITEKEY = os.getenv('HCAPTCHA_SITEKEY', '')
HCAPTCHA_SECRET = os.getenv('HCAPTCHA_SECRET', '')
HCAPTCHA_API_URL = 'https://hcaptcha.com/siteverify'

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
AXES_HANDLER = 'axes.handlers.database.AxesDatabaseHandler'
AXES_CACHE = 'default'

#
# Django Crispy Templates
#
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = 'bootstrap5'

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

STATIC_ROOT = ''
USE_S3 = os.getenv('USE_S3') == 'TRUE'

if USE_S3:
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_CUSTOM_DOMAIN = os.getenv('WGER_CDN_DOMAIN')
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=31557600'}
    AWS_LOCATION = 'static'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    COMPRESS_URL = STATIC_URL
    COMPRESS_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    COMPRESS_OFFLINE = True
    COMPRESS_OFFLINE_CONTEXT = [
        {'request': {'user_agent': {'is_mobile': True}}, 'STATIC_URL': STATIC_URL},
        {'request': {'user_agent': {'is_mobile': False}}, 'STATIC_URL': STATIC_URL}
    ]
else:
    STATIC_URL = '/static/'

#
# Django compressor
#
COMPRESS_CSS_FILTERS = (
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.rCSSMinFilter',
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
    'DEFAULT_PERMISSION_CLASSES': ('wger.utils.permissions.WgerPermission',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20,
    'PAGINATE_BY_PARAM': 'limit',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
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
    'DEFAULT_THROTTLE_RATES': {'login': '10/min', 'registration': '5/min'},
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'wger',
    'SERVERS': [
        {'url': '/', 'description': 'This server'},
        {'url': 'https://wger.de', 'description': 'The "official" upstream wger instance'},
    ],
    'DESCRIPTION': 'Self hosted FLOSS workout and fitness tracker',
    'VERSION': get_version(),
    'SERVE_INCLUDE_SCHEMA': True,
    'SCHEMA_PATH_PREFIX': '/api/v[0-9]',
    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
    'COMPONENT_SPLIT_REQUEST': True
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,
}

CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^/api/.*$'
IGNORABLE_404_URLS = (re.compile(r'^/favicon\.ico$'),)

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

USER_AGENTS_CACHE = 'default'

#
# Application specific configuration options
#
WGER_SETTINGS = {
    'ALLOW_GUEST_USERS': True,
    'ALLOW_REGISTRATION': True,
    'ALLOW_UPLOAD_VIDEOS': False,
    'EMAIL_FROM': 'wger Workout Manager <wger@example.com>',
    'EXERCISE_CACHE_TTL': 3600,
    'DOWNLOAD_INGREDIENTS_FROM': DOWNLOAD_INGREDIENT_WGER,
    'INGREDIENT_CACHE_TTL': 604800,
    'INGREDIENT_IMAGE_CHECK_INTERVAL': datetime.timedelta(weeks=12),
    'ROUTINE_CACHE_TTL': 4 * 604800,
    'MIN_ACCOUNT_AGE_TO_TRUST': 21,
    'SYNC_EXERCISES_CELERY': False,
    'SYNC_EXERCISE_IMAGES_CELERY': False,
    'SYNC_EXERCISE_VIDEOS_CELERY': False,
    'SYNC_INGREDIENTS_CELERY': False,
    'SYNC_OFF_DAILY_DELTA_CELERY': False,
    'CACHE_API_EXERCISES_CELERY': False,
    'CACHE_API_EXERCISES_CELERY_FORCE_UPDATE': False,
    'TWITTER': False,
    'MASTODON': 'https://fosstodon.org/@wger',
    'USE_CELERY': False,
    'USE_RECAPTCHA': False,
    'WGER_INSTANCE': 'https://wger.de',
}

AUTH_PROXY_HEADER = ''
AUTH_PROXY_USER_EMAIL_HEADER = ''
AUTH_PROXY_USER_NAME_HEADER = ''
AUTH_PROXY_TRUSTED_IPS = []
AUTH_PROXY_CREATE_UNKNOWN_USER = False

EXPOSE_PROMETHEUS_METRICS = False
PROMETHEUS_URL_PATH = 'super-secret-path'

def email_verified_callback(user):
    user.userprofile.email_verified = True
    user.userprofile.save()

EMAIL_MAIL_CALLBACK = email_verified_callback
EMAIL_FROM_ADDRESS = WGER_SETTINGS['EMAIL_FROM']
EMAIL_MAIL_SUBJECT = 'Confirm your email'
EMAIL_MAIL_HTML = 'email_verification/email_body_html.tpl'
EMAIL_MAIL_PLAIN = 'email_verification/email_body_txt.tpl'
EMAIL_MAIL_TOKEN_LIFE = 60 * 60
EMAIL_MAIL_PAGE_TEMPLATE = 'email_verification/confirm_template.html'
EMAIL_PAGE_DOMAIN = 'http://localhost:8000/'

ACTSTREAM_SETTINGS = {
    'USE_JSONFIELD': True,
}

TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'
