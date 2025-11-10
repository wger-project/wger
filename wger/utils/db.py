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
from functools import wraps

# Django
from django.conf import settings


def is_postgres_db():
    return 'postgres' in settings.DATABASES['default']['ENGINE']


def postgres_only(func):
    """Decorator that runs the decorated function only if the database is PostgreSQL."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if is_postgres_db():
            return func(*args, **kwargs)
        else:
            return

    return wrapper
