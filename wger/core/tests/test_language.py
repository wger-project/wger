# -*- coding: utf-8 -*-

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
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

from django.core.urlresolvers import reverse_lazy

from wger.core.models import Language
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import WorkoutManagerAccessTestCase
from wger.core.tests.base_testcase import WorkoutManagerAddTestCase
from wger.core.tests.base_testcase import WorkoutManagerDeleteTestCase, WorkoutManagerTestCase
from wger.core.tests.base_testcase import WorkoutManagerEditTestCase


class LanguageRepresentationTestCase(WorkoutManagerTestCase):
    '''
    Test the representation of a model
    '''

    def test_representation(self):
        '''
        Test that the representation of an object is correct
        '''
        self.assertEqual("{0}".format(Language.objects.get(pk=1)), 'Deutsch (de)')


class LanguageOverviewTest(WorkoutManagerAccessTestCase):
    '''
    Tests accessing the system's languages
    '''

    url = 'core:language:overview'
    anonymous_fail = True


class LanguageDetailViewTest(WorkoutManagerAccessTestCase):
    '''
    Tests accessing a detail view of a language
    '''

    url = reverse_lazy('core:language:view', kwargs={'pk': 1})
    anonymous_fail = True


class CreateLanguageTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a new language
    '''

    object_class = Language
    url = 'core:language:add'
    data = {'short_name': 'dk',
            'full_name': 'Dansk'}


class EditLanguageTestCase(WorkoutManagerEditTestCase):
    '''
    Tests adding a new language
    '''

    object_class = Language
    url = 'core:language:edit'
    pk = 1
    data = {'short_name': 'dk',
            'full_name': 'Dansk'}


class DeleteLanguageTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests adding a new language
    '''

    object_class = Language
    url = 'core:language:delete'
    pk = 1


class LanguageApiTestCase(api_base_test.ApiBaseResourceTestCase):
    '''
    Tests the language overview resource
    '''
    pk = 1
    resource = Language
    private_resource = False
