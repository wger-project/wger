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

from wger.core.models import License
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import WorkoutManagerAccessTestCase, WorkoutManagerTestCase
from wger.core.tests.base_testcase import WorkoutManagerAddTestCase
from wger.core.tests.base_testcase import WorkoutManagerDeleteTestCase
from wger.core.tests.base_testcase import WorkoutManagerEditTestCase


class LicenseRepresentationTestCase(WorkoutManagerTestCase):
    '''
    Test the representation of a model
    '''

    def test_representation(self):
        '''
        Test that the representation of an object is correct
        '''
        self.assertEqual("{0}".format(License.objects.get(pk=1)),
                         'A cool and free license - Germany (ACAFL - DE)')


class LicenseOverviewTest(WorkoutManagerAccessTestCase):
    '''
    Tests the licese overview page
    '''

    url = 'core:license:list'


class AddLicenseTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a new license
    '''

    object_class = License
    url = 'core:license:add'
    data = {'full_name': 'Something here',
            'short_name': 'SH'}


class DeleteLicenseTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting a license
    '''

    object_class = License
    url = 'core:license:delete'
    pk = 1


class EditLicenseTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a license
    '''

    object_class = License
    url = 'core:license:edit'
    pk = 1
    data = {'full_name': 'Something here 1.1',
            'short_name': 'SH 1.1'}


class LicenseApiTestCase(api_base_test.ApiBaseResourceTestCase):
    '''
    Tests the license resource
    '''
    pk = 1
    resource = License
    private_resource = False
