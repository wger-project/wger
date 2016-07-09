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

import datetime
import json
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from wger.core.models import UserProfile
from wger.core.tests.base_testcase import WorkoutManagerTestCase
from wger.utils.constants import TWOPLACES
from wger.weight.models import WeightEntry


class BmiTestCase(WorkoutManagerTestCase):
    '''
    Tests the BMI methods and views
    '''

    def test_page(self):
        '''
        Access the BMI page
        '''

        response = self.client.get(reverse('nutrition:bmi:view'))
        self.assertEqual(response.status_code, 302)

        self.user_login('test')
        response = self.client.get(reverse('nutrition:bmi:view'))
        self.assertEqual(response.status_code, 200)

    def test_calculator(self):

        '''
        Tests the calculator itself
        '''

        self.user_login('test')
        response = self.client.post(reverse('nutrition:bmi:calculate'),
                                    {'height': 180,
                                     'weight': 80})
        self.assertEqual(response.status_code, 200)
        bmi = json.loads(response.content.decode('utf8'))
        self.assertEqual(Decimal(bmi['bmi']), Decimal(24.69).quantize(TWOPLACES))
        self.assertEqual(Decimal(bmi['weight']), Decimal(80))
        self.assertEqual(Decimal(bmi['height']), Decimal(180))

    def test_calculator_imperial(self):

        '''
        Tests the calculator using imperial units
        '''

        self.user_login('test')
        profile = UserProfile.objects.get(user__username='test')
        profile.weight_unit = 'lb'
        profile.save()
        response = self.client.post(reverse('nutrition:bmi:calculate'),
                                    {'height': 180,
                                     'weight': 176.36})
        self.assertEqual(response.status_code, 200)
        bmi = json.loads(response.content.decode('utf8'))
        self.assertEqual(Decimal(bmi['bmi']), Decimal(24.69).quantize(TWOPLACES))
        self.assertEqual(Decimal(bmi['weight']), Decimal(176.36).quantize(TWOPLACES))
        self.assertEqual(Decimal(bmi['height']), Decimal(180))

    def test_automatic_weight_entry(self):
        '''
        Tests that weight entries are automatically created or updated
        '''

        self.user_login('test')
        user = User.objects.get(username=self.current_user)

        # Existing weight entry is old, a new one is created
        entry1 = WeightEntry.objects.filter(user=user).latest()
        response = self.client.post(reverse('nutrition:bmi:calculate'),
                                    {'height': 180,
                                     'weight': 80})
        self.assertEqual(response.status_code, 200)
        entry2 = WeightEntry.objects.filter(user=user).latest()
        self.assertEqual(entry1.weight, 83)
        self.assertEqual(entry2.weight, 80)

        # Existing weight entry is from today, is updated
        entry2.delete()
        entry1.date = datetime.date.today()
        entry1.save()
        response = self.client.post(reverse('nutrition:bmi:calculate'),
                                    {'height': 180,
                                     'weight': 80})
        self.assertEqual(response.status_code, 200)
        entry2 = WeightEntry.objects.filter(user=user).latest()
        self.assertEqual(entry1.pk, entry2.pk)
        self.assertEqual(entry2.weight, 80)

        # No existing entries
        WeightEntry.objects.filter(user=user).delete()
        response = self.client.post(reverse('nutrition:bmi:calculate'),
                                    {'height': 180,
                                     'weight': 80})
        self.assertEqual(response.status_code, 200)
        entry = WeightEntry.objects.filter(user=user).latest()
        self.assertEqual(entry.weight, 80)
        self.assertEqual(entry.date, datetime.date.today())
