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

# Django
from django.test import SimpleTestCase

# Third Party
from rest_framework import serializers

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.api.serializers import WeightConfigSerializer
from wger.manager.api.validators import validate_requirements


class RequirementsValidatorTestCase(SimpleTestCase):
    """
    Serializer-level tests for ``validate_requirements``.

    The validator is wired into ``BaseConfigSerializer.requirements`` and is *not*
    invoked by model ``save()``, so these tests call it directly (the same way the
    serializer does) and assert acceptance / ``ValidationError`` rejection.
    """

    def test_accepts_none(self):
        # Should not raise
        validate_requirements(None)

    def test_accepts_existing_rules(self):
        validate_requirements({'rules': ['weight', 'repetitions', 'rir', 'rest']})

    def test_accepts_max_repetitions(self):
        validate_requirements({'rules': ['max_repetitions']})

    def test_accepts_max_weight(self):
        validate_requirements({'rules': ['max_weight']})

    def test_accepts_all_sets_true(self):
        validate_requirements({'rules': ['max_repetitions'], 'all_sets': True})

    def test_accepts_all_sets_false(self):
        validate_requirements({'rules': ['max_repetitions'], 'all_sets': False})

    def test_rejects_max_sets(self):
        with self.assertRaises(serializers.ValidationError):
            validate_requirements({'rules': ['max_sets']})

    def test_rejects_bogus_rule(self):
        with self.assertRaises(serializers.ValidationError):
            validate_requirements({'rules': ['bogus']})

    def test_rejects_non_boolean_all_sets(self):
        with self.assertRaises(serializers.ValidationError):
            validate_requirements({'rules': ['max_repetitions'], 'all_sets': 'yes'})

    def test_rejects_non_dict(self):
        with self.assertRaises(serializers.ValidationError):
            validate_requirements(['max_repetitions'])

    def test_rejects_missing_rules_key(self):
        with self.assertRaises(serializers.ValidationError):
            validate_requirements({'all_sets': True})

    def test_rejects_non_list_rules(self):
        with self.assertRaises(serializers.ValidationError):
            validate_requirements({'rules': 'max_repetitions'})

    def test_rejects_unknown_top_level_key(self):
        """A mistyped modifier (e.g. 'all_set') must error instead of silently passing"""
        with self.assertRaises(serializers.ValidationError):
            validate_requirements({'rules': ['max_repetitions'], 'all_set': True})

    def test_rejects_unknown_top_level_key_alongside_valid(self):
        with self.assertRaises(serializers.ValidationError):
            validate_requirements({'rules': ['max_repetitions'], 'all_sets': True, 'foo': 1})


class RequirementsSerializerWiringTestCase(WgerTestCase):
    """
    Confirms ``validate_requirements`` is actually wired into the config serializer
    field (``BaseConfigSerializer.requirements``), locking the end-to-end contract.
    """

    def test_serializer_accepts_valid_requirements(self):
        serializer = WeightConfigSerializer(
            data={
                'slot_entry': 1,
                'iteration': 1,
                'value': '80',
                'requirements': {'rules': ['max_repetitions'], 'all_sets': True},
            }
        )
        serializer.is_valid()
        self.assertNotIn('requirements', serializer.errors)

    def test_serializer_rejects_bogus_rule(self):
        serializer = WeightConfigSerializer(
            data={
                'slot_entry': 1,
                'iteration': 1,
                'value': '80',
                'requirements': {'rules': ['bogus']},
            }
        )
        serializer.is_valid()
        self.assertIn('requirements', serializer.errors)
