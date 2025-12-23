"""Local development settings for wger"""

# ruff: noqa: F405

# wger
from .settings_global import *  # noqa: F403

DEBUG = True

# List of administrators
ADMINS = (('Your name', 'your_email@example.com'),)
MANAGERS = ADMINS

# Don't use this key in production!
SECRET_KEY = 'wger-local-development-supersecret-key-1234567890!'

# Allow all hosts to access the application.
ALLOWED_HOSTS = ['*', ]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# WGER application
WGER_SETTINGS['ALLOW_UPLOAD_VIDEOS'] = True
WGER_SETTINGS['ALLOW_GUEST_USERS'] = True
WGER_SETTINGS['ALLOW_REGISTRATION'] = True
WGER_SETTINGS['DOWNLOAD_INGREDIENTS_FROM'] = 'WGER' # or 'None' to disable
WGER_SETTINGS['EMAIL_FROM'] = 'wger Workout Manager <wger@example.com>'
WGER_SETTINGS['EXERCISE_CACHE_TTL'] = 500
WGER_SETTINGS['INGREDIENT_CACHE_TTL'] = 500
WGER_SETTINGS['SYNC_EXERCISES_CELERY'] = False
WGER_SETTINGS['SYNC_EXERCISE_IMAGES_CELERY'] = True
WGER_SETTINGS['SYNC_EXERCISE_VIDEOS_CELERY'] = False
WGER_SETTINGS['SYNC_INGREDIENTS_CELERY'] = True
WGER_SETTINGS['USE_CELERY'] = False
WGER_SETTINGS['CACHE_API_EXERCISES_CELERY'] = True
WGER_SETTINGS['CACHE_API_EXERCISES_CELERY_FORCE_UPDATE'] = True
WGER_SETTINGS['ROUTINE_CACHE_TTL'] = 500
DEFAULT_FROM_EMAIL = WGER_SETTINGS['EMAIL_FROM']


# CELERY_BROKER_URL = "redis://localhost:6379/2"
# CELERY_RESULT_BACKEND = "redis://localhost:6379/2"

CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']

EXPOSE_PROMETHEUS_METRICS = True

COMPRESS_ENABLED = False
AXES_ENABLED = False


# Does not really cache anything
CACHES_DUMMY = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        'TIMEOUT': 100,
    }
}

# In-memory cache, resets when the server restarts
CACHE_LOCMEM = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'wger-cache',
        'TIMEOUT': 100,
    }
}

# Redis cache
CACHE_REDIS = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
        'TIMEOUT': 5000,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient'
        }
    }
}


# CACHES = CACHE_REDIS
# CACHES = CACHE_LOCMEM
CACHES = CACHES_DUMMY


# Django Debug Toolbar
# INSTALLED_APPS += ['django_extensions', 'debug_toolbar']
# MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware", ]
# INTERNAL_IPS = ["127.0.0.1", ]

# AUTH_PROXY_HEADER = 'HTTP_X_REMOTE_USER'
# AUTH_PROXY_USER_EMAIL_HEADER = 'HTTP_X_REMOTE_USER_EMAIL'
# AUTH_PROXY_USER_NAME_HEADER = 'HTTP_X_REMOTE_USER_NAME'
# AUTH_PROXY_TRUSTED_IPS = ['127.0.0.1', ]
# AUTH_PROXY_CREATE_UNKNOWN_USER = True


DBCONFIG_PG = {
    'ENGINE': 'django_prometheus.db.backends.postgresql',
    'NAME': 'wger',
    'USER': 'wger',
    'PASSWORD': 'wger',
    'HOST': 'localhost',
    'PORT': '5432',
}


DBCONFIG_SQLITE = {
    'ENGINE': 'django_prometheus.db.backends.sqlite3',
    'NAME':  BASE_DIR.parent / 'db' / 'database.sqlite',
}

DATABASES = {
    # 'default': DBCONFIG_PG,
    'default': DBCONFIG_SQLITE,
}


# Import other local settings that are not in version control
try:
    from .local_dev_extra import *  # noqa: F403
except ImportError:
    pass
