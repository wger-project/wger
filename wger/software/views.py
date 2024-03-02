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
from django.core.cache import cache
from django.shortcuts import render

# Third Party
import requests

# wger
from wger.core.forms import (
    RegistrationForm,
    RegistrationFormNoCaptcha,
)
from wger.exercises.models import ExerciseBase
from wger.nutrition.models import Ingredient


logger = logging.getLogger(__name__)

CACHE_KEY = 'landing-page-context'


def features(request):
    """
    Render the landing page
    """

    context = cache.get(CACHE_KEY)
    if not context:
        result_github_api = requests.get('https://api.github.com/repos/wger-project/wger').json()
        context = {
            'nr_users': User.objects.count(),
            'nr_exercises': ExerciseBase.objects.count(),
            'nr_ingredients': Ingredient.objects.count(),
            'nr_stars': result_github_api.get('stargazers_count', '2000'),
        }
        cache.set(CACHE_KEY, context, 60 * 60 * 24 * 7)  # one week

    FormClass = (
        RegistrationForm if settings.WGER_SETTINGS['USE_RECAPTCHA'] else RegistrationFormNoCaptcha
    )
    form = FormClass()
    form.fields['username'].widget.attrs.pop('autofocus', None)

    context['form'] = form
    context['allow_registration'] = settings.WGER_SETTINGS['ALLOW_REGISTRATION']
    context['allow_guest_users'] = settings.WGER_SETTINGS['ALLOW_GUEST_USERS']

    return render(request, 'features.html', context)
