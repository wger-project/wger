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

# wger
from wger.core.tests import powersync_base_test
from wger.nutrition.models import (
    LogItem,
    NutritionPlan,
)


# Pinned in test-nutrition-data.json
PLAN_OWNED = 1  # user 'test'
PLAN_OTHER = 2  # user 'admin'

# Pinned in test-nutrition-diary.json (linked to PLAN_OWNED)
LOG_OWNED_UUID = 'ee000000-0000-0000-0000-000000000001'

INGREDIENT_PUBLIC = 1


class NutritionPlanPowerSyncTestCase(
    powersync_base_test.PowerSyncBaseTestCase,
    powersync_base_test.PowerSyncCreateNotAllowedTestCase,
    powersync_base_test.PowerSyncUpdateTestCase,
    powersync_base_test.PowerSyncDeleteTestCase,
):
    """
    PowerSync handlers for nutrition.NutritionPlan. Creation must go through
    REST (the dispatcher rejects PUT), so only PATCH/DELETE are tested.
    """

    table = 'nutrition_nutritionplan'
    resource = NutritionPlan

    pk_owned = PLAN_OWNED

    update_payload = {
        'id': pk_owned,
        'description': 'Renamed via PowerSync',
    }

    create_payload = {'id': 9999, 'description': 'should not be created'}


class LogItemPowerSyncTestCase(powersync_base_test.PowerSyncResourceTestCase):
    """
    PowerSync handlers for nutrition.LogItem. The handler runs
    check_fk_ownership against (NutritionPlan, 'plan') and (Meal, 'meal').
    Lookup uses the uuid field, not the integer pk.
    """

    table = 'nutrition_logitem'
    resource = LogItem

    pk_owned = LOG_OWNED_UUID

    create_payload = {
        'id': 'ee000000-0000-0000-0000-000000000099',
        'plan': PLAN_OWNED,
        'datetime': '2030-01-15T10:00:00Z',
        'ingredient': INGREDIENT_PUBLIC,
        'amount': '50',
    }
    update_payload = {
        'id': pk_owned,
        'amount': '99',
    }

    fk_ownership = (
        ('plan', PLAN_OTHER),
    )

    def _get_entry_for_update(self):
        # LogItem's PowerSync handler looks up by uuid, not pk
        return LogItem.objects.get(uuid=self.update_payload['id'])
