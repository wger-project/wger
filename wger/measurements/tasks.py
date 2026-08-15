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
import random

# Third Party
from celery.schedules import crontab

# wger
from wger.celery_configuration import app
from wger.measurements.dynamic.engine import (
    reconcile,
    reconcile_by_id,
)
from wger.measurements.models import Category


logger = logging.getLogger(__name__)


@app.task
def reconcile_dynamic_category_task(category_id: str):
    """
    Recomputes the calculated rows of one dynamic category
    """
    reconcile_by_id(category_id)


@app.task
def reconcile_all_dynamic_categories_task():
    """
    Recomputes every dynamic category, the safety net for source writes that
    bypass the signals (bulk operations, data migrations)
    """
    count = 0
    for category in Category.objects.exclude(dynamic_type=Category.DynamicType.NONE).iterator():
        reconcile(category)
        count += 1
    logger.info(f'Reconciled {count} dynamic measurement categories')


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(
            hour=str(random.randint(0, 23)),
            minute=str(random.randint(0, 59)),
        ),
        reconcile_all_dynamic_categories_task.s(),
        name='Reconcile dynamic measurement categories',
    )
