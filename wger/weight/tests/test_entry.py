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

from wger.weight.models import WeightEntry

from wger.manager.tests.testcase import WorkoutManagerEditTestCase
from wger.manager.tests.testcase import WorkoutManagerAddTestCase
from wger.manager.tests.testcase import ApiBaseResourceTestCase


class AddWeightEntryTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a weight entry
    '''

    object_class = WeightEntry
    url = 'weight-add'
    pk = 8
    user_fail = False
    data = {'weight': 81.1,
            'creation_date': datetime.date(2013, 2, 1),
            'user': 1}


class EditWeightEntryTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a weight entry
    '''

    object_class = WeightEntry
    url = 'weight-edit'
    pk = 1
    data = {'weight': 100,
            'creation_date': datetime.date(2013, 2, 1),
            'user': 1}
    user_success = 'test'
    user_fail = 'admin'


class WeightEntryTestCase(ApiBaseResourceTestCase):
    '''
    Tests the weight entry overview resource
    '''
    resource = 'weightentry'
    resource_updatable = False


class WeightEntryDetailApiTestCase(ApiBaseResourceTestCase):
    '''
    Tests accessing a specific weight entry
    '''
    resource = 'weightentry/3'
