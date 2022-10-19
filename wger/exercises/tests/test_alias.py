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

# Standard Library
import json

# Django
from django.core import mail
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.template import (
    Context,
    Template,
)
from django.urls import reverse

# Third Party
from rest_framework import status

# wger
from wger.core.tests import api_base_test
from wger.core.tests.api_base_test import (
    ApiBaseTestCase,
    ExerciseCrudApiTestCase,
)
from wger.core.tests.base_testcase import (
    STATUS_CODES_FAIL,
    WgerDeleteTestCase,
    WgerTestCase,
)
from wger.exercises.models import (
    Alias,
    Exercise,
    ExerciseCategory,
    Muscle,
)
from wger.utils.cache import cache_mapper
from wger.utils.constants import WORKOUT_TAB
from wger.utils.helpers import random_string


class AliasCustomApiTestCase(ExerciseCrudApiTestCase):
    pk = 1

    data = {
        'exercise': 1,
        'alias': 'Alias 123',
    }

    def get_resource_name(self):
        return 'exercisealias'
