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

from django.core.urlresolvers import reverse
from django.core.cache import cache

from wger.core.models import License

from wger.manager.tests.testcase import WorkoutManagerAccessTestCase
from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.manager.tests.testcase import WorkoutManagerDeleteTestCase
from wger.manager.tests.testcase import WorkoutManagerEditTestCase
from wger.manager.tests.testcase import WorkoutManagerAddTestCase
from wger.manager.tests.testcase import ApiBaseResourceTestCase
from wger.utils.cache import get_template_cache_name, cache_mapper

from wger.utils.constants import PAGINATION_OBJECTS_PER_PAGE


class LicenseOverviewTest(WorkoutManagerAccessTestCase):
    '''
    Tests the licese overview page
    '''

    url = 'core:license-list'
    anonymous_fail = True


class AddLicenseTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a new license
    '''

    object_class = License
    url = 'core:license-add'
    data = {'full_name': 'Something here',
            'short_name': 'SH'}
    pk = 3


class DeleteLicenseTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting a license
    '''

    object_class = License
    url = 'core:license-delete'
    pk = 1


class EditLicenseTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a license
    '''

    object_class = License
    url = 'core:license-edit'
    pk = 1
    data = {'full_name': 'Something here 1.1',
            'short_name': 'SH 1.1'}


class LicenseApiTestCase(ApiBaseResourceTestCase):
    '''
    Tests the license resource
    '''
    resource = 'license'
    user = None
    resource_updatable = False


class LicenseDetailApiTestCase(ApiBaseResourceTestCase):
    '''
    Tests accessing a specific license
    '''
    resource = 'license/1'
    user = None
    resource_updatable = False
