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
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import (
    post_delete,
    post_save,
)
from django.dispatch import receiver

# wger
# The types have to be imported before the receivers are wired up below,
# source_models() only knows what is registered
import wger.measurements.dynamic.types  # noqa: F401
from wger.measurements.dynamic.base import (
    all_types,
    source_models,
)
from wger.measurements.dynamic.engine import schedule_reconcile
from wger.measurements.models import (
    Category,
    Measurement,
)
from wger.measurements.models.measurement import MeasurementSource
from wger.utils.helpers import (
    deletion_originates_from_user,
    disable_for_loaddata,
)


logger = logging.getLogger(__name__)


def _dispatch_source_change(sender, instance):
    """
    Schedules a reconcile for every dynamic category that depends on the
    changed instance
    """
    # The engine's own writes must not trigger another round
    if isinstance(instance, Measurement) and instance.source == MeasurementSource.CALCULATED:
        return

    # One category query per owner instead of one per type: almost every
    # write belongs to a user without any calculated category
    wanted: dict[int, set[str]] = {}
    for calc in all_types():
        for dep in calc.depends_on:
            if dep.model is not sender:
                continue
            try:
                if not dep.when(instance):
                    continue
                user_id = dep.user_id(instance)
            except ObjectDoesNotExist:
                # A related row vanished in the same cascade
                continue
            if user_id is None:
                continue
            wanted.setdefault(user_id, set()).add(calc.slug)

    for user_id, slugs in wanted.items():
        categories = Category.objects.filter(
            user_id=user_id,
            dynamic_type__in=slugs,
        ).values_list('pk', flat=True)
        for category_id in categories:
            schedule_reconcile(category_id)


@disable_for_loaddata
def _source_saved(sender, instance, **kwargs):
    _dispatch_source_change(sender, instance)


def _source_deleted(sender, instance, origin=None, **kwargs):
    if deletion_originates_from_user(origin):
        return
    _dispatch_source_change(sender, instance)


for model in source_models():
    uid = f'measurements_dynamic_{model._meta.label_lower}'
    post_save.connect(_source_saved, sender=model, dispatch_uid=f'{uid}_save')
    post_delete.connect(_source_deleted, sender=model, dispatch_uid=f'{uid}_delete')


@receiver(post_save, sender=Category, dispatch_uid='measurements_dynamic_category')
@disable_for_loaddata
def _category_saved(sender, instance, **kwargs):
    """
    Enabling, reconfiguring or disabling a dynamic type on a category: the
    reconcile backfills or clears its calculated rows
    """
    schedule_reconcile(instance.pk)
