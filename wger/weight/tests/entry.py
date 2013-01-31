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

import datetime

from django.core.urlresolvers import reverse

from wger.weight.models import WeightEntry

from wger.manager.tests.testcase import WorkoutManagerTestCase


class AddWeightEntryTestCase(WorkoutManagerTestCase):
    '''
    Tests adding a weight entry
    '''

    def add_entry(self, fail=False):
        '''
        Helper function to test adding a weight entry
        '''

        # Fetch the add entry page
        response = self.client.get(reverse('weight-add'))

        if fail:
            self.assertIn(response.status_code, (302, 403))
            self.assertTemplateUsed('login.html')

        else:
            self.assertEqual(response.status_code, 200)

        # Enter the data
        response = self.client.post(reverse('weight-add'),
                                    {'weight': '81',
                                    'creation_date': '2013-02-01'})
        if fail:
            self.assertRaises(WeightEntry.DoesNotExist, WeightEntry.objects.get, pk=8)
            self.assertIn(response.status_code, (302, 403))
            self.assertTemplateUsed('login.html')

        else:
            entry = WeightEntry.objects.get(pk=8)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(entry.weight, 81)
            self.assertEqual(entry.creation_date, datetime.date(2013, 2, 1))

    def test_add_entry_anonymous(self):
        '''
        Test adding a weight entry as an anonymous user
        '''

        self.add_entry(fail=True)

    def test_add_entry_logged_in(self):
        '''
        Test adding a weight entry as a logged in user
        '''

        self.user_login('test')
        self.add_entry(fail=False)


class EditWeightEntryTestCase(WorkoutManagerTestCase):
    '''
    Tests editing a weight entry
    '''

    def edit_entry(self, fail=False):
        '''
        Helper function
        '''

        # Fetch the day edit page
        response = self.client.get(reverse('weight-edit', kwargs={'pk': 1}))

        if fail:
            self.assertIn(response.status_code, (302, 403))
            self.assertTemplateUsed('login.html')

        else:
            self.assertEqual(response.status_code, 200)

        # Edit the day
        response = self.client.post(reverse('weight-edit', kwargs={'pk': 1}),
                                    {'weight': 100,
                                    'creation_date': '2005-01-01'})

        entry = WeightEntry.objects.get(pk=1)

        if fail:
            self.assertIn(response.status_code, (302, 403))
            self.assertTemplateUsed('login.html')
            self.assertEqual(entry.weight, 77)
            self.assertEqual(entry.creation_date, datetime.date(2012, 10, 1))

        else:
            self.assertEqual(response.status_code, 302)
            self.assertEqual(entry.weight, 100)
            self.assertEqual(entry.creation_date, datetime.date(2005, 1, 1))

    def test_edit_entry_anonymous(self):
        '''
        Test editing a weight entry as an anonymous user
        '''

        self.edit_entry(fail=True)

    def test_edit_entry_owner(self):
        '''
        Test editing a weight entry as the owner user
        '''

        self.user_login('test')
        self.edit_entry(fail=False)

    def test_edit_entry_other(self):
        '''
        Test editing a weight entry as a different user
        '''

        self.user_login('admin')
        self.edit_entry(fail=True)
