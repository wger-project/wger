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

import logging

from django.core.urlresolvers import reverse

from wger.core.tests.base_testcase import WorkoutManagerTestCase
from wger.weight.models import WeightEntry

logger = logging.getLogger(__name__)


class WeightCsvImportTestCase(WorkoutManagerTestCase):
    '''
    Test case for the CSV import for weight entries
    '''

    def import_csv(self):
        '''
        Helper function to test the CSV import
        '''
        response = self.client.get(reverse('weight:import-csv'))
        self.assertEqual(response.status_code, 200)

        # Do a direct post request
        # 1st step
        count_before = WeightEntry.objects.count()
        csv_input = '''Datum	Gewicht	KJ
05.01.10	error here	111
22.01.aa	69,2	222
27.01.10	69,6	222
02.02.10	69	222
11.02.10	70,4	222
19.02.10	71	222
26.02.10	71,9	222
26.02.10	71,9	222
19.03.10	72	 222'''
        response = self.client.post(reverse('weight:import-csv'),
                                    {'stage': 1,
                                     'csv_input': csv_input,
                                     'date_format': '%d.%m.%y'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['weight_list']), 6)
        self.assertEqual(len(response.context['error_list']), 4)
        hash_value = response.context['hash_value']

        # 2nd. step
        response = self.client.post(reverse('weight:import-csv'),
                                    {'stage': 2,
                                     'hash': hash_value,
                                     'csv_input': csv_input,
                                     'date_format': '%d.%m.%y'})

        count_after = WeightEntry.objects.count()
        self.assertEqual(response.status_code, 302)

        self.assertGreater(count_after, count_before)

    def test_import_csv_loged_in(self):
        '''
        Test deleting a category by a logged in user
        '''

        self.user_login('test')
        self.import_csv()
