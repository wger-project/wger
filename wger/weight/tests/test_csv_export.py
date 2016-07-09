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

logger = logging.getLogger(__name__)


class WeightCsvExportTestCase(WorkoutManagerTestCase):
    '''
    Test case for the CSV export for weight entries
    '''

    def export_csv(self):
        '''
        Helper function to test the CSV export
        '''
        response = self.client.get(reverse('weight:export-csv'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(response['Content-Disposition'],
                         'attachment; filename=Weightdata.csv')
        self.assertGreaterEqual(len(response.content), 120)
        self.assertLessEqual(len(response.content), 150)

    def test_export_csv_logged_in(self):
        '''
        Test the CSV export for weight entries by a logged in user
        '''

        self.user_login('test')
        self.export_csv()
