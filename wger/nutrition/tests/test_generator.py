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
from django.core.management import call_command

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.nutrition.models import NutritionPlan


class NutritionalPlansGeneratorTestCase(WgerTestCase):
    def test_generator(self):
        # Arrange
        NutritionPlan.objects.all().delete()

        # Act
        call_command('dummy-generator-nutrition', '--plans', 10)

        # Assert
        self.assertEqual(NutritionPlan.objects.filter(user_id=1).count(), 10)
