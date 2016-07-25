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
import decimal

from django.core.urlresolvers import reverse

from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import WorkoutManagerAddTestCase
from wger.core.tests.base_testcase import WorkoutManagerEditTestCase, WorkoutManagerTestCase
from wger.utils.constants import TWOPLACES
from wger.weight.models import WeightEntry


class MealRepresentationTestCase(WorkoutManagerTestCase):
    '''
    Test the representation of a model
    '''

    def test_representation(self):
        '''
        Test that the representation of an object is correct
        '''
        self.assertEqual("{0}".format(WeightEntry.objects.get(pk=1)), '2012-10-01: 77.00 kg')


class WeightEntryAccessTestCase(WorkoutManagerTestCase):
    '''
    Test accessing the weight overview page
    '''

    def test_access_shared(self):
        '''
        Test accessing the URL of a shared weight overview
        '''
        url = reverse('weight:overview', kwargs={'username': 'admin'})

        self.user_login('admin')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.user_login('test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.user_logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_access_not_shared(self):
        '''
        Test accessing the URL of an unshared weight overview
        '''
        url = reverse('weight:overview', kwargs={'username': 'test'})

        self.user_login('admin')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        self.user_login('test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.user_logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class AddWeightEntryTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a weight entry
    '''

    object_class = WeightEntry
    url = 'weight:add'
    user_fail = False
    data = {'weight': decimal.Decimal(81.1).quantize(TWOPLACES),
            'date': datetime.date(2013, 2, 1),
            'user': 1}


class EditWeightEntryTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a weight entry
    '''

    object_class = WeightEntry
    url = 'weight:edit'
    pk = 1
    data = {'weight': 100,
            'date': datetime.date(2013, 2, 1),
            'user': 1}
    user_success = 'test'
    user_fail = 'admin'


class WeightEntryTestCase(api_base_test.ApiBaseResourceTestCase):
    '''
    Tests the weight entry overview resource
    '''
    pk = 3
    resource = WeightEntry
    private_resource = True
    data = {'weight': 100,
            'date': datetime.date(2013, 2, 1)}
