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
from wger.weight.models import WeightEntry


class WeightEntryPowerSyncTestCase(powersync_base_test.PowerSyncResourceTestCase):
    """
    Verify that the PowerSync handlers in wger/weight/powersync.py only let a
    user touch their own WeightEntry rows.
    """

    table = 'weight_weightentry'
    resource = WeightEntry

    # owned by user 'test'
    pk_owned = '11111111-1111-1111-1111-000000000003'

    create_payload = {
        'date': '2030-01-15T10:00:00Z',
        'weight': '95.5',
    }
    update_payload = {
        'id': pk_owned,
        'weight': '88.5',
    }

    def _get_entry_for_update(self):
        # WeightEntry's PowerSync handler looks up by uuid, not pk
        return WeightEntry.objects.get(uuid=self.update_payload['id'])
