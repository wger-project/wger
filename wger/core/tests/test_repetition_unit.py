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

# wger
from wger.core.models import RepetitionUnit
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import (
    WgerAccessTestCase,
    WgerAddTestCase,
    WgerDeleteTestCase,
    WgerEditTestCase,
    WgerTestCase,
)


class RepresentationTestCase(WgerTestCase):
    """
    Test the representation of a model
    """

    def test_representation(self):
        """
        Test that the representation of an object is correct
        """
        self.assertEqual(f'{RepetitionUnit.objects.get(pk=1)}', 'Repetitions')


class UnitTypeTestCase(WgerTestCase):
    """
    Test the unit_type field and related properties
    """

    def test_time_unit_type(self):
        """Test that Seconds unit has TIME type"""
        unit = RepetitionUnit.objects.get(pk=3)  # Seconds
        self.assertEqual(unit.unit_type, RepetitionUnit.UNIT_TYPE_TIME)
        self.assertTrue(unit.is_time)
        self.assertFalse(unit.is_distance)

    def test_repetitions_unit_type(self):
        """Test that Repetitions unit has REPETITIONS type"""
        unit = RepetitionUnit.objects.get(pk=1)  # Repetitions
        self.assertEqual(unit.unit_type, RepetitionUnit.UNIT_TYPE_REPETITIONS)
        self.assertFalse(unit.is_time)
        self.assertFalse(unit.is_distance)

    def test_distance_unit_type(self):
        """Test that Miles unit has DISTANCE type"""
        unit = RepetitionUnit.objects.get(pk=5)  # Miles
        self.assertEqual(unit.unit_type, RepetitionUnit.UNIT_TYPE_DISTANCE)
        self.assertFalse(unit.is_time)
        self.assertTrue(unit.is_distance)


class OverviewTest(WgerAccessTestCase):
    """
    Tests the settings unit overview page
    """

    url = 'core:repetition-unit:list'
    anonymous_fail = True


class AddTestCase(WgerAddTestCase):
    """
    Tests adding a new unit
    """

    object_class = RepetitionUnit
    url = 'core:repetition-unit:add'
    data = {'name': 'Furlongs'}
    user_success = ('admin',)
    user_fail = (
        'general_manager1',
        'general_manager2',
        'member1',
        'member2',
        'trainer2',
        'trainer3',
        'trainer4',
        'manager3',
    )


class DeleteTestCase(WgerDeleteTestCase):
    """
    Tests deleting a unit
    """

    pk = 1
    object_class = RepetitionUnit
    url = 'core:repetition-unit:delete'
    user_success = ('admin',)
    user_fail = (
        'general_manager1',
        'general_manager2',
        'member1',
        'member2',
        'trainer2',
        'trainer3',
        'trainer4',
        'manager3',
    )


class EditTestCase(WgerEditTestCase):
    """
    Tests editing a unit
    """

    pk = 1
    object_class = RepetitionUnit
    url = 'core:repetition-unit:edit'
    data = {'name': 'Furlongs'}
    user_success = ('admin',)
    user_fail = (
        'general_manager1',
        'general_manager2',
        'member1',
        'member2',
        'trainer2',
        'trainer3',
        'trainer4',
        'manager3',
    )


class ApiTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the unit resource
    """

    pk = 1
    resource = RepetitionUnit
    private_resource = False

    def get_resource_name(self):
        return 'setting-repetitionunit'
