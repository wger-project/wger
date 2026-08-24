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

# Django
from django.conf import settings
from django.core.cache import cache
from django.db import transaction

# wger
from wger.measurements.dynamic.base import get_type
from wger.measurements.models import (
    Category,
    Measurement,
)
from wger.measurements.models.measurement import MeasurementSource


logger = logging.getLogger(__name__)

# One queued task per category: the marker suppresses further queueing until
# the task starts, and the countdown gives a write burst (e.g. a draining
# upload queue) time to finish so it collapses into that one run
RECONCILE_DEBOUNCE_SECONDS = 15

# A crashed task suppresses reconciles at most this long; the daily catch-all
# repairs anything behind it
RECONCILE_MARKER_TIMEOUT = 5 * 60


def reconcile_marker_key(category_id) -> str:
    return f'measurements-dynamic-reconcile-{category_id}'


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
    Queues a reconcile for after the current transaction.

    With celery the queueing is single-flight per category: while a task is
    waiting, further writes queue nothing, and the task removes the marker
    before it computes so a write arriving during the run queues a follow-up.
    Without celery the reconcile runs right here, there is no later moment to
    collapse a burst into.
    """
    transaction.on_commit(lambda: _run_scheduled(category_id))


def _run_scheduled(category_id) -> None:
    # This runs after the commit, so a failure here has nothing to roll back
    # and would only turn an unrelated request into a 500. The daily task
    # picks the category up again
    try:
        if settings.WGER_SETTINGS['USE_CELERY']:
            # wger
            from wger.measurements.tasks import reconcile_dynamic_category_task

            # add() is atomic across processes: True means no task is waiting
            if cache.add(reconcile_marker_key(category_id), True, RECONCILE_MARKER_TIMEOUT):
                reconcile_dynamic_category_task.apply_async(
                    args=[str(category_id)],
                    countdown=RECONCILE_DEBOUNCE_SECONDS,
                )
        else:
            reconcile_by_id(category_id)
    except Exception:
        logger.exception(f'Could not reconcile dynamic category {category_id}')
