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

import json
import decimal
import datetime

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from wger.utils.constants import TWOPLACES

from wger.weight.models import WeightEntry
from wger.manager.tests.testcase import WorkoutManagerTestCase


class CaloriesCalculatorTestCase(WorkoutManagerTestCase):
    '''
    Tests the calories calculator methods and views
    '''

    def test_page(self):
        '''
        Access the page
        '''

        response = self.client.get(reverse('calories-calculator'))
        self.assertEqual(response.status_code, 200)

    def test_calculator(self):
        '''
        Tests the calculator itself
        '''

        self.user_login('test')
        response = self.client.post(reverse('calories-calculate-activities'),
                                    {'sleep_hours': 7,
                                     'work_hours': 8,
                                     'work_intensity': 1,
                                     'sport_hours': 6,
                                     'sport_intensity': 3,
                                     'freetime_hours': 8,
                                     'freetime_intensity': 1})
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(decimal.Decimal(result['factor']),
                         decimal.Decimal(1.57).quantize(TWOPLACES))
        self.assertEqual(decimal.Decimal(result['activities']), decimal.Decimal(2920))

    def test_automatic_weight_entry_bmi(self):
        '''
        Tests that weight entries are automatically created or updated
        '''

        self.user_login('test')
        user = User.objects.get(username=self.current_user)

        # Existing weight entry is old, a new one is created
        entry1 = WeightEntry.objects.filter(user=user).latest()
        response = self.client.post(reverse('bmi-calculate'),
                                    {'height': 180,
                                     'weight': 80})
        self.assertEqual(response.status_code, 200)
        entry2 = WeightEntry.objects.filter(user=user).latest()
        self.assertEqual(entry1.weight, 83)
        self.assertEqual(entry2.weight, 80)

        # Existing weight entry is from today, is updated
        entry2.delete()
        entry1.creation_date = datetime.date.today()
        entry1.save()
        response = self.client.post(reverse('bmi-calculate'),
                                    {'height': 180,
                                     'weight': 80})
        self.assertEqual(response.status_code, 200)
        entry2 = WeightEntry.objects.filter(user=user).latest()
        self.assertEqual(entry1.pk, entry2.pk)
        self.assertEqual(entry2.weight, 80)

        # No existing entries
        WeightEntry.objects.filter(user=user).delete()
        response = self.client.post(reverse('bmi-calculate'),
                                    {'height': 180,
                                     'weight': 80})
        self.assertEqual(response.status_code, 200)
        entry = WeightEntry.objects.filter(user=user).latest()
        self.assertEqual(entry.weight, 80)
        self.assertEqual(entry.creation_date, datetime.date.today())

    def test_bmr(self):
        '''
        Tests the BMR view
        '''

        self.user_login('test')
        response = self.client.post(reverse('calories-calculate-bmr'),
                                    {'age': 30,
                                     'height': 180,
                                     'gender': 1,
                                     'weight': 80})
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result, {'bmr': '1780'})

    def test_total_calories_form(self):
        '''
        Tests the form with the total calories
        '''

        self.user_login('test')
        user = User.objects.get(username=self.current_user)
        self.assertEqual(user.userprofile.calories, 3500)

        response = self.client.post(reverse('calories-calculate-total'),
                                    {'additional_calories': 0,
                                     'calories': 2000})
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(username=self.current_user)
        self.assertEqual(user.userprofile.calories, 2000)

    def test_automatic_weight_entry_bmr(self):
        '''
        Tests that weight entries are automatically created or updated
        '''

        self.user_login('test')
        user = User.objects.get(username=self.current_user)

        # Existing weight entry is old, a new one is created
        entry1 = WeightEntry.objects.filter(user=user).latest()
        response = self.client.post(reverse('calories-calculate-bmr'),
                                    {'age': 30,
                                     'height': 180,
                                     'gender': 1,
                                     'weight': 80})
        self.assertEqual(response.status_code, 200)
        entry2 = WeightEntry.objects.filter(user=user).latest()
        self.assertEqual(entry1.weight, 83)
        self.assertEqual(entry2.weight, 80)

        # Existing weight entry is from today, is updated
        entry2.delete()
        entry1.creation_date = datetime.date.today()
        entry1.save()
        response = self.client.post(reverse('calories-calculate-bmr'),
                                    {'age': 30,
                                     'height': 180,
                                     'gender': 1,
                                     'weight': 80})
        self.assertEqual(response.status_code, 200)
        entry2 = WeightEntry.objects.filter(user=user).latest()
        self.assertEqual(entry1.pk, entry2.pk)
        self.assertEqual(entry2.weight, 80)

        # No existing entries
        WeightEntry.objects.filter(user=user).delete()
        response = self.client.post(reverse('calories-calculate-bmr'),
                                    {'age': 30,
                                     'height': 180,
                                     'gender': 1,
                                     'weight': 80})
        self.assertEqual(response.status_code, 200)
        entry = WeightEntry.objects.filter(user=user).latest()
        self.assertEqual(entry.weight, 80)
        self.assertEqual(entry.creation_date, datetime.date.today())
