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
import datetime
from os.path import join as path_join

# Third Party
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import translation

from flask import jsonify

# wger
from wger import get_version
from wger.core.models import Language


# ************************
# Language functions
# ************************


def load_language():
    '''
    Returns the currently used language, e.g. to load appropriate exercises
    '''
    # TODO: perhaps store a language preference in the user's profile?

    # Read the first part of a composite language, e.g. 'de-at'
    used_language = translation.get_language().split('-')[0]

    try:
        language = Language.objects.get(short_name=used_language)

    # No luck, load english as our fall-back language
    except ObjectDoesNotExist:
        language = Language.objects.get(short_name="en")

    return language


def load_ingredient_languages(request):
    '''
    Filter the ingredients the user will see by its language.

    Additionally, if the user has selected on his preference page that he wishes
    to also see the ingredients in English (from the US Department of Agriculture),
    show those too.

    This only makes sense if the user's language isn't English, as he will be
    presented those in that case anyway, so also do a check for this.
    '''

    language = load_language()
    languages = (language.id,)

    # Only registered users have a profile
    if request.user.is_authenticated():
        profile = request.user.userprofile
        show_english = profile.show_english_ingredients

        # If the user's language is not english and has the preference, add english to the list
        if show_english and language.short_name != 'en':
            languages = (language.id, 2)

    return languages


def render_JSON_file(workout_name):
    '''
    Creates a JSON file with relevant workout details
    :return: a JSON file
    '''

    file = open(str(workout_name) + ".json", "w")
    file.write(str(render_header() + create_workout_JSON()))
    file.close()

    return file


def render_header():
    '''
    Renders the header for the JSON workout file
    :return: a multi-line JSON comment
    '''
    date = datetime.date.today().strftime("%d.%m.%Y")
    header =    "// This workout information was generated from http://wger.de"
           + "\n // Date: {date}"
           + "\n // Version: {version}"
           + "\n".format(date=date,
                         version=get_version())
    return header


def create_workout_JSON():
    '''
    Renders a JSON object with relevant workout details
    :return: a JSON object
    '''

    workout_info = {
        "name":    "FIXME",
        "days":    ["FIXME", "array", "of", "strings"],
        "details": {
            "FIXME": "FIXME"
        }
    }

    print jsonify(workout_info)
    return jsonify(workout_info)
    # return jsonify(username=g.user.username,
    #                email=g.user.email,
    #                id=g.user.id)