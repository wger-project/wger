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

# ruff: noqa: F405, F403

# Third Party
import environ

# wger
from .settings_global import *

env = environ.Env()

DEBUG = False

"""
Settings for CI:

The basic changes are

* skip migrations
* use a faster password hasher
* use plain (un-hashed) static file storage
* use an in-memory backend for media files
"""

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

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
        'NAME': 'database.sqlite',
        'TEST': {
            'MIGRATE': False,
        },
    }
}

ADMINS = ['"Your name" <your_email@example.com>']
MANAGERS = ADMINS

TIME_ZONE = 'Europe/Berlin'
SECRET_KEY = '61fxc$k%9nj!be-_up9%xzm(z)9l7$h33b1!@bf9581=c-03%p'

RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
USE_RECAPTCHA = False

# Test-only RSA keypair for JWT, safe to commit.
JWT_PRIVATE_KEY = (
    'eyJhbGciOiAiUlMyNTYiLCAia3R5IjogIlJTQSIsICJuIjogIjlSbXdqZDJadG9DUzg4N0hNY2JpNFpK'
    'RE5WS3dBWG1QSURSby1vejdaWWl1SFpUSzRXNkJYUHpIWnJJd1g5ZXFEOWJBSmNUZzd5NGFKbHRPZ1JY'
    'aFFwdDFZbWo2THRTbkV6NEdRQnM4MjVUS2liS3NIRVpHV2Y5cENWazFleTB3XzNEQTNFSEhQdWNwdEto'
    'cHhzNFFXRERSTEFGamh6WHJVZjQ5X3R2S25aWVcyZ295NEpLVEFsdGFZLUJfemVYYTZZZUx2d1JBbTJU'
    'eVgtV0o5aGVVNjFVRTZ1R2toaTg2Y240WjdlSmsxYmtpNUlxNGRBMC1nVElrNGNzR3VZV2FNU0hfLThP'
    'b1NGU0FjcTFMRGVfdlYwSFhmUHZMMmpSeEhsTkQ1cE12dUlZRU8tNU8yeHVzZU5JU2lJN1YzVDJaWGJG'
    'UWdESHZ2YXlCV0lhQ3V0Z0x5dyIsICJlIjogIkFRQUIiLCAiZCI6ICJJUVFBNEZ0RlpXd1VYM3N2SWVs'
    'a2puWWhUNEZfNl9MdjhLcWVxWUZzSzlVcGZ4cVg2WjMxRncyRjNyT0tDSjhJYlhIRUdGSlk2bDhQYnJO'
    'RjgtVjZubnBLYWFNeWNEUjhfUDZSNFBqS1RkblJIcE5PMDlBemtkUHgxaXlLSTdtR3JDSUlHS05UcjRs'
    'Ny1MWG02YnpBUHVEMGpEVHpyemI0Si1kVGVvMG8wZWt1VnMxTmFHRjBKOUgxeXJyUUt3d1ZtejJEZWoz'
    'OVBERFFWbmVCNk5VNDhzQnRqaFc1YnpBNXF1bWlwSm8tQm9MY0stQ3lBVWl2YVJoYU5IT2U0SDFXYzVT'
    'RlA2czZyeGZ3Z1lNbHlLQVZZU1lvYUVvYThRUTh6akFxN0c3Z3FLQ1dHems5ZkZQUGZjbFVvcGtWWHVJ'
    'elNZdXROV1NDUzQ5eVpJZExENk1JWVEiLCAicCI6ICItb2FHdzNpZElzbVNSNnkxZWNVVlkxYk51QnNG'
    'Q2tFWURWcHNJQjg1YUlJS1NQR1dqTEFjM3hXU1hBZWktekxWY3pQTDVWRVFYQ09Fell2TGV3NWI1MUd0'
    'SXM5MEp5ekxDVGh6SEl4NGlUdnVURUN0U09oMEoxUkxQcDdFbkxKREZsZUItN0txbjFDUWNNREQwV0Vi'
    'SWJZd29XTmNDR1N3dzFEVWZ6RXhfRDAiLCAicSI6ICItblRRY3hHeEdoM3Q2YUluenNSZXhnRkxVaktn'
    'c1NDMUtJMFRqeTRCUktlb040MFhYNXhDSHlfUnRzSkRneUljR1F6UjZNVXZxM0xwTnZNNzRkbHdRUTQ3'
    'YkRCYlJIMjFVc05YeDl0c2phQUpuRGMtX1pONHFyQzNYMFpjM2pRTERuNEUxazFvQWxMTmM0QXNyNVB0'
    'REFUSzF6YzdoaVJqSng4eGdQVjJnS2MiLCAiZHAiOiAiMXpGUzlQalgwUmZnSk56X2pUZHpKYjljT2Za'
    'TG9BRkdEY0pMLWxPWDFtTk5QbGIyZ0thT1JqbWJYSjNhcTNlQXpkSUNKRm83ZVVteE8zWUhOUTZpZHRJ'
    'N3JCa1Nwc3ZkSTNCdndHZ1E2YUNuRXF6RHJFcXY2MUNHeWFWTE1XWVdKa3pJaEZGMktoN2owMVpoWGFy'
    'UnlXVmI1R1VhbXNNUzZ0SzFsUVBHOGVrIiwgImRxIjogImwtaWVQZ3p2QkU0LTdVUWpMUEJDSTRySmFw'
    'TzJqM2l0S0dsWkFiRF9wLXFneHdEV3VuRUdVZkFwSE5aN0tHQlo5bi1tR2E3d0dPZGJ1SzZURll0UzRN'
    'S0hIRG5BUWF5VmZCdHJkSmNNSW1KOU1iajRoY2thbVQwU0c4R0x0bUtPaWoyNUpWcFJ5WWI3Z2lDdC1k'
    'aVpJSDhQb0xXcGJ0VkhKb1Z1LXk3bXIyVSIsICJxaSI6ICJub1QxRnVfMURfUFVxVEY2NlVJWXpNYVZB'
    'bHN5ZU5WMFAydmMycFRZQ1lpb29lam4xNkEwc3FMMHZ3VmstM2Mzc2dtU0oyejc4SklWTXoxMlFtTHl1'
    'aGlMa01HZEpzeUJUYTdnWGI2RXcxQnFHTmxoVHFXX0p6RGJEclNmSEJpMnA5dFZPUFVTSW5ZaURxbXRy'
    'bkFMWnVDZ3ZqUFItVzlPaF9rTUlNbUJQUmMiLCAia2lkIjogImNpLXRlc3QifQ=='
)
JWT_PUBLIC_KEY = (
    'eyJrdHkiOiAiUlNBIiwgIm4iOiAiOVJtd2pkMlp0b0NTODg3SE1jYmk0WkpETlZLd0FYbVBJRFJvLW96'
    'N1pZaXVIWlRLNFc2QlhQekhackl3WDllcUQ5YkFKY1RnN3k0YUpsdE9nUlhoUXB0MVltajZMdFNuRXo0'
    'R1FCczgyNVRLaWJLc0hFWkdXZjlwQ1ZrMWV5MHdfM0RBM0VISFB1Y3B0S2hweHM0UVdERFJMQUZqaHpY'
    'clVmNDlfdHZLblpZVzJnb3k0SktUQWx0YVktQl96ZVhhNlllTHZ3UkFtMlR5WC1XSjloZVU2MVVFNnVH'
    'a2hpODZjbjRaN2VKazFia2k1SXE0ZEEwLWdUSWs0Y3NHdVlXYU1TSF8tOE9vU0ZTQWNxMUxEZV92VjBI'
    'WGZQdkwyalJ4SGxORDVwTXZ1SVlFTy01TzJ4dXNlTklTaUk3VjNUMlpYYkZRZ0RIdnZheUJXSWFDdXRn'
    'THl3IiwgImUiOiAiQVFBQiIsICJhbGciOiAiUlMyNTYiLCAia2lkIjogImNpLXRlc3QifQ=='
)
SIMPLE_JWT['SIGNING_KEY'] = jwk_b64_to_pem(JWT_PRIVATE_KEY)
SIMPLE_JWT['VERIFYING_KEY'] = jwk_b64_to_pem(JWT_PUBLIC_KEY)
HEADLESS_JWT_PRIVATE_KEY = SIMPLE_JWT['SIGNING_KEY']

SITE_URL = 'http://localhost:8000'

MEDIA_ROOT = '/tmp/'
MEDIA_URL = '/media/'

ALLOWED_HOSTS = [
    '*',
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = WGER_SETTINGS['EMAIL_FROM']
EMAIL_PAGE_DOMAIN = SITE_URL
AXES_ENABLED = False

STORAGES = {
    # In-memory storage avoids disk writes for media uploads during tests.
    'default': {
        'BACKEND': 'django.core.files.storage.InMemoryStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}
