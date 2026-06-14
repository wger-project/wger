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

# Django
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import WgerTestCase


class ConfigFilterTestCase(WgerTestCase):
    """
    The config endpoints must honour the ``slot_entry`` query filter
    """

    def test_filter_by_slot_entry(self):
        self.user_login()
        url = reverse('weight-config-list')

        response = self.client.get(url)
        self.assertEqual(response.data['count'], 4)

        response = self.client.get(url, {'slot_entry': 1})
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['slot_entry'], 1)
