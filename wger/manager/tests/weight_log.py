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
import datetime

from django.core.urlresolvers import reverse

from wger.manager.models import WorkoutLog

from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.manager.tests.testcase import WorkoutManagerLiveServerTestCase

logger = logging.getLogger('workout_manager.custom')


class WeightLogTestCase(WorkoutManagerTestCase):
    '''
    Tests the weight log functionality
    '''

    def add_weight_log(self, fail=True):
        '''
        Helper function to test adding weight log entries
        '''

        # Fetch the overview page
        response = self.client.get(reverse('workout-log', kwargs={'pk': 1}))

        if fail:
            # Logged out users get a 302 redirect to login page
            # Users not owning the workout, a 403, forbidden
            self.assertTrue(response.status_code in (302, 403))
        else:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['active_tab'], 'workout')
            self.assertEqual(response.context['workout'].id, 1)

        # Add new log entries
        count_before = WorkoutLog.objects.count()
        response = self.client.post(reverse('day-log', kwargs={'pk': 1}),
                                    {'date': '2012-01-01',
                                     'form-0-reps': 10,
                                     'form-0-weight': 10,
                                     'form-TOTAL_FORMS': 3,
                                     'form-INITIAL_FORMS': 0,
                                     'form-MAX-NUM_FORMS': 3
                                    })

        count_after = WorkoutLog.objects.count()

        if fail:
            # Logged out users get a 302 redirect to login page
            # Users not owning the workout, a 403, forbidden
            self.assertTrue(response.status_code in (302, 403))

            self.assertEqual(count_before, count_after)
        else:
            self.assertEqual(response.status_code, 302)
            self.assertGreater(count_after, count_before)

    def test_add_weight_log_anonymous(self):
        '''
        Tests adding weight log entries as an anonymous user
        '''

        self.add_weight_log(fail=True)

    def test_add_weight_log_owner(self):
        '''
        Tests adding weight log entries as the owner user
        '''

        self.user_login('admin')
        self.add_weight_log(fail=False)

    def test_add_weight_log_other(self):
        '''
        Tests adding weight log entries as a logged user not owning the data
        '''

        self.user_login('test')
        self.add_weight_log(fail=True)


class WeightLogEntryTestCase(WorkoutManagerTestCase):
    '''
    Tests editing individual weight log entries
    '''

    def edit_log_entry(self, fail=True):
        '''
        Helper function to test edit log entries
        '''

        date_before = WorkoutLog.objects.get(pk=1).date
        response = self.client.post(reverse('workout-log-edit', kwargs={'pk': 1}),
                                    {'date': '2012-01-01',
                                     'reps': 10,
                                     'weight': 10,
                                     })

        date_after = WorkoutLog.objects.get(pk=1).date

        if fail:
            # Logged out users get a 302 redirect to login page
            # Users not owning the workout, a 403, forbidden
            self.assertTrue(response.status_code in (302, 403))
            self.assertEqual(date_before, date_after)

        else:
            self.assertEqual(response.status_code, 302)
            self.assertEqual(date_after, datetime.date(2012, 1, 1))

    def test_edit_log_entry_anonymous(self):
        '''
        Tests editing a weight log entries as an anonymous user
        '''

        self.edit_log_entry(fail=True)

    def test_edit_log_entry_owner(self):
        '''
        Tests editing a weight log entries as the owner user
        '''

        self.user_login('admin')
        self.edit_log_entry(fail=False)

    def test_edit_log_entry_other(self):
        '''
        Tests editing a weight log entries as a logged user not owning the data
        '''

        self.user_login('test')
        self.edit_log_entry(fail=True)


#class WorkoutLogLiveServerTestCase(WorkoutManagerLiveServerTestCase):
    #'''
    #Selenium tests for workout log
    #'''

    #def test_find_links(self):
        #'''
        #Tests that the correct links are in the right places on the workout
        #view
        #'''

        #self.user_login()
        #self.browser.get(self.live_server_url + reverse('workout-view', kwargs = {'id': 1}))

        ## There is a link to view/edit the logs for the day
        #table_row = self.browser.find_element_by_id('day-1')
        #self.assertTrue(table_row)
        #links = table_row.find_elements_by_tag_name('a')
        #self.assertEqual(len(links), 3)
        #log_link = links[2]
        #self.assertIn('Add weight log to this day', log_link.get_attribute('title'))
        #self.assertIn(reverse('day-log', kwargs={'pk': 1}),
                      #log_link.get_attribute('href'))

        ## There is a link on the sidebar to access the log for the current workout
        #sidebar = self.browser.find_element_by_id('main-sidebar')
        #workout_log = sidebar.find_elements_by_tag_name('a')[2]
        #self.assertIn(reverse('workout-log', kwargs={'pk': 1}),
                      #workout_log.get_attribute('href'))
