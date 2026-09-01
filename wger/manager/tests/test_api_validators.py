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

# Third Party
from rest_framework import serializers

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.api.validators import validate_requirements


class ValidateRequirementsTestCase(WgerTestCase):
    """
    Test suite for validate_requirements function
    """

    def test_valid_requirements(self):
        """Test valid requirement structures pass without errors"""
        # None is allowed
        self.assertIsNone(validate_requirements(None))

        # Basic rules
        self.assertIsNone(validate_requirements({'rules': ['weight']}))
        self.assertIsNone(validate_requirements({'rules': ['repetitions']}))
        self.assertIsNone(validate_requirements({'rules': ['rir']}))
        self.assertIsNone(validate_requirements({'rules': ['rest']}))

        # New max rules
        self.assertIsNone(validate_requirements({'rules': ['max_repetitions']}))
        self.assertIsNone(validate_requirements({'rules': ['max_weight']}))
        self.assertIsNone(validate_requirements({'rules': ['max_repetitions', 'weight']}))

        # With all_sets flag
        self.assertIsNone(validate_requirements({'rules': ['max_repetitions'], 'all_sets': True}))
        self.assertIsNone(validate_requirements({'rules': ['max_repetitions'], 'all_sets': False}))

        # Empty rules list
        self.assertIsNone(validate_requirements({'rules': []}))

    def test_invalid_type(self):
        """Test that non-dict value raises ValidationError"""
        with self.assertRaises(serializers.ValidationError):
            validate_requirements('not a dict')

        with self.assertRaises(serializers.ValidationError):
            validate_requirements(['rules'])

        with self.assertRaises(serializers.ValidationError):
            validate_requirements(123)

    def test_missing_required_rules_key(self):
        """Test that missing 'rules' key raises ValidationError"""
        with self.assertRaises(serializers.ValidationError):
            validate_requirements({})

        with self.assertRaises(serializers.ValidationError):
            validate_requirements({'all_sets': True})

    def test_invalid_rules_type(self):
        """Test that non-list 'rules' raises ValidationError"""
        with self.assertRaises(serializers.ValidationError):
            validate_requirements({'rules': 'repetitions'})

        with self.assertRaises(serializers.ValidationError):
            validate_requirements({'rules': {'repetitions': True}})

    def test_invalid_rule_name(self):
        """Test that invalid rule names are rejected"""
        with self.assertRaises(serializers.ValidationError):
            validate_requirements({'rules': ['invalid_rule']})

        with self.assertRaises(serializers.ValidationError):
            validate_requirements({'rules': ['repetitions', 'foo_bar']})

    def test_unknown_keys_rejected(self):
        """Test that unexpected keys in the requirements dict are rejected"""
        with self.assertRaises(serializers.ValidationError):
            validate_requirements({'rules': ['repetitions'], 'unknown_key': 123})

        with self.assertRaises(serializers.ValidationError):
            validate_requirements({'rules': ['repetitions'], 'extra': 'data'})

    def test_invalid_all_sets_type(self):
        """Test that non-boolean all_sets values are rejected"""
        with self.assertRaises(serializers.ValidationError):
            validate_requirements({'rules': ['max_repetitions'], 'all_sets': 'true'})

        with self.assertRaises(serializers.ValidationError):
            validate_requirements({'rules': ['max_repetitions'], 'all_sets': 1})

        with self.assertRaises(serializers.ValidationError):
            validate_requirements({'rules': ['max_repetitions'], 'all_sets': None})
