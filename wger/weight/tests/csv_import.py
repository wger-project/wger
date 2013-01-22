# This file is part of Workout Manager.
# 
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License

import logging


from django.test import TestCase
from django.core.urlresolvers import reverse

from wger.weight.models import WeightEntry

from wger.manager.tests.testcase import WorkoutManagerTestCase

logger = logging.getLogger('workout_manager.custom')


class WeightCsvImportTestCase(WorkoutManagerTestCase):
    '''
    Test case for the CSV import for weight entries
    '''
  
    def import_csv(self, fail = False):
        '''
        Helper function to test the CSV import
        '''
        response = self.client.get(reverse('weight-import-csv'))
        
        if fail:
            # There is a redirect
            self.assertEqual(response.status_code, 302)
        else:
            # Logged in users see a page
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
19.03.10	72	 222'''
        response = self.client.post(reverse('weight-import-csv'),
                                    {'stage': 1,
                                     'csv_input': csv_input,
                                     'date_format': '%d.%m.%y'})
        
        if fail:
            self.assertEqual(response.status_code, 302)
        
        else:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context['weight_list']), 6)
            self.assertEqual(len(response.context['error_list']), 3)
        
        # 2nd. step
        response = self.client.post(reverse('weight-import-csv'),
                                    {'stage': 2,
                                     'hash': 'fde7e06185aad7151b8c93ee961499ebabb7983d',
                                     'csv_input': csv_input,
                                     'date_format': '%d.%m.%y'})
        
        count_after = WeightEntry.objects.count()
        self.assertEqual(response.status_code, 302)
        
        if fail:
            self.assertEqual(count_before, count_after)
        else:
            self.assertGreater(count_after, count_before)

    def test_import_csv_anonymous(self):
        """Test deleting a category by an unauthorized user"""
        
        self.import_csv(fail=True)
        
    def test_import_csv_loged_in(self):
        """Test deleting a category by a logged in user"""
        
        self.user_login('test')
        self.import_csv(fail=False)
        
