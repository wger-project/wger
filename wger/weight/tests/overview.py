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

from django.core.urlresolvers import reverse

from wger.manager.tests.testcase import WorkoutManagerTestCase

logger = logging.getLogger('workout_manager.custom')


class WeightOverviewTestCase(WorkoutManagerTestCase):
    '''
    Test case for the weight overview page
    '''

    def weight_overview(self):
        '''
        Helper function to test the weight overview page
        '''
        response = self.client.get(reverse('weight-overview'))
        self.assertEqual(response.status_code, 200)

    def test_weight_overview_loged_in(self):
        '''
        Test the weight overview page by a logged in user
        '''
        self.user_login('test')
        self.weight_overview()


class WeightExportCsvTestCase(WorkoutManagerTestCase):
    '''
    Tests exporting the saved weight entries as a CSV file
    '''

    def csv_export(self):
        '''
        Helper function to test exporting the saved weight entries as a CSV file
        '''
        response = self.client.get(reverse('wger.weight.views.export_csv'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(len(response.content), 132)

    def test_csv_export_loged_in(self):
        '''
        Test exporting the saved weight entries as a CSV file by a logged in user
        '''
        self.user_login('test')
        self.csv_export()
