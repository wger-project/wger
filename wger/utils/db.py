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
from django.db import models

# wger
from wger.utils.uuid import uuid7


def is_postgres_db():
    return 'postgres' in settings.DATABASES['default']['ENGINE']


def postgres_only(func):
    """Decorator that runs the decorated function only if the database is PostgreSQL."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if is_postgres_db():
            return func(*args, **kwargs)
        else:
            return None

    return wrapper


def backfill_uuid_column(
    model: type[models.Model],
    column: str = 'uuid',
    batch_size: int = 2000,
) -> None:
    """
    Populate a freshly added UUID column for every existing row, in batches using
    the column's own model default.

    Every row is rewritten unconditionally: ``AddField`` with a callable default
    evaluates that default only once and fills *all* existing rows with the same
    value (``ADD COLUMN ... DEFAULT <one-value>``).
    """

    default = model._meta.get_field(column).default
    if not callable(default):
        default = uuid7

    batch = []
    for row in model.objects.all().only('pk').iterator(chunk_size=batch_size):
        setattr(row, column, default())
        batch.append(row)
        if len(batch) >= batch_size:
            model.objects.bulk_update(batch, [column])
            batch = []
    if batch:
        model.objects.bulk_update(batch, [column])
