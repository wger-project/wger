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
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

# Standard Library
import logging
import threading

# Django
from django.conf import settings
from django.db import transaction

# wger
from wger.measurements.dynamic.base import get_type
from wger.measurements.models import (
    Category,
    Measurement,
)
from wger.measurements.models.measurement import MeasurementSource


logger = logging.getLogger(__name__)

_pending = threading.local()


def reconcile(category: Category) -> None:
    """
    Brings the stored calculated rows of a category to the state its type
    computes: missing rows are created, changed ones updated, orphans deleted.

    Backfill, live updates and repair are all this one operation. For a
    category that is not (or no longer) dynamic it degrades to deleting
    whatever calculated rows are left.
    """
    calc = get_type(category.dynamic_type)
    existing = Measurement.objects.filter(
        category=category,
        source=MeasurementSource.CALCULATED,
    )

    if calc is None:
        existing.delete()
        return

    existing_rows = {row.external_id: row for row in existing}

    for row in calc.compute(category):
        current = existing_rows.pop(row.external_id, None)
        if current is None:
            # get_or_create so a concurrent reconcile cannot trip over the
            # (category, source, external_id) constraint
            Measurement.objects.get_or_create(
                category=category,
                source=MeasurementSource.CALCULATED,
                external_id=row.external_id,
                defaults={
                    'date': row.date,
                    'value': row.value,
                    'extra_data': row.extra_data,
                },
            )
        elif (current.date, current.value, current.extra_data) != (
            row.date,
            row.value,
            row.extra_data,
        ):
            current.date = row.date
            current.value = row.value
            current.extra_data = row.extra_data
            current.save()

    for stale in existing_rows.values():
        stale.delete()


def reconcile_by_id(category_id) -> None:
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return
    reconcile(category)


def schedule_reconcile(category_id) -> None:
    """
    Queues a reconcile for after the current transaction, deduplicated so a
    batch of source writes triggers one recompute rather than one per row
    """
    ids = getattr(_pending, 'ids', None)
    if ids is None:
        ids = _pending.ids = set()
    if category_id in ids:
        return
    ids.add(category_id)
    transaction.on_commit(lambda: _run_scheduled(category_id))


def _run_scheduled(category_id) -> None:
    getattr(_pending, 'ids', set()).discard(category_id)
    if settings.WGER_SETTINGS['USE_CELERY']:
        # wger
        from wger.measurements.tasks import reconcile_dynamic_category_task

        reconcile_dynamic_category_task.delay(str(category_id))
    else:
        reconcile_by_id(category_id)
