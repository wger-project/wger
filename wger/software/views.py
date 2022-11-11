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

# Standard Library
import logging

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import render
from django.views.decorators.cache import cache_page

# Third Party
import requests

# wger
from wger.exercises.models import ExerciseBase
from wger.nutrition.models import Ingredient


logger = logging.getLogger(__name__)


# @cache_page(60 * 60 * 24 * 10)
def features(request):
    """
    Render the features page
    """

    # Fetch number of stars from GitHub. The page is cached, so doing this is OK
    result = requests.get('https://api.github.com/repos/wger-project/wger').json()

    context = {
        'allow_registration': settings.WGER_SETTINGS['ALLOW_REGISTRATION'],
        'allow_guest_users': settings.WGER_SETTINGS['ALLOW_GUEST_USERS'],
        'nr_users': User.objects.count(),
        'nr_exercises': ExerciseBase.objects.count(),
        'nr_ingredients': Ingredient.objects.count(),
        'nr_stars': result.get('stargazers_count', '2000')
    }
    return render(request, 'features.html', context)
