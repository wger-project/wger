# This file is part of Workout Manager.
#
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

from os.path import join as path_join

from django.conf import settings
from django.utils import translation
from django.core.exceptions import ObjectDoesNotExist

from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import StyleSheet1
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from wger.exercises.models import Language
from wger.config.models import LanguageConfig


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


def load_item_languages(item):
    '''
    Returns the languages for a data type (exercises, ingredients)
    '''

    #SHOW_ITEM_EXERCISES = '1'
    #SHOW_ITEM_INGREDIENTS = '2'

    # Load the configurations we are interested in and return the languages
    LanguageConfig.SHOW_ITEM_LIST
    language = load_language()
    languages = []

    config = LanguageConfig.objects.filter(language=language, item=item, show=True)
    if not config:
        languages.append(Language.objects.get(short_name="en"))
        return languages

    for i in config:
        languages.append(i.language_target)

    return languages


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
        profile = request.user.get_profile()
        show_english = profile.show_english_ingredients

        # If the user's language is not english and has the preference, add english to the list
        if show_english and language.short_name != 'en':
            languages = (language.id, 2)

    return languages


# register new truetype fonts for reportlab
pdfmetrics.registerFont(TTFont(
    'OpenSans', path_join(settings.SITE_ROOT, 'manager/static/fonts/OpenSans-Light.ttf')))
pdfmetrics.registerFont(TTFont(
    'OpenSans-Bold', path_join(settings.SITE_ROOT, 'manager/static/fonts/OpenSans-Bold.ttf')))
pdfmetrics.registerFont(TTFont(
    'OpenSans-Regular', path_join(settings.SITE_ROOT, 'manager/static/fonts/OpenSans-Regular.ttf')))

styleSheet = StyleSheet1()
styleSheet.add(ParagraphStyle(
               name='Normal',
               fontName='OpenSans',
               fontSize=10,
               leading=12,
               ))
styleSheet.add(ParagraphStyle(
               parent=styleSheet['Normal'],
               fontSize=8,
               name='Small',
               ))
styleSheet.add(ParagraphStyle(
               parent=styleSheet['Normal'],
               name='Bold',
               fontName='OpenSans-Bold',
               ))
