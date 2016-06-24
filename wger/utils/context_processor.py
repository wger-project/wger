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

from django.conf import settings
from django.templatetags.static import static

from wger import get_version
from wger.utils import constants
from wger.utils.language import load_language


def processor(request):

    language = load_language()
    full_path = request.get_full_path()
    i18n_path = {}
    static_path = static('images/logos/logo-marketplace-256.png')

    for lang in settings.LANGUAGES:
        i18n_path[lang[0]] = u'/{0}{1}'.format(lang[0], full_path[3:])

    context = {
        # Application version
        'version': get_version(),

        # Twitter handle for this instance
        'twitter': settings.WGER_SETTINGS['TWITTER'],

        # User language
        'language': language,

        # Available application languages
        'languages': settings.LANGUAGES,

        # The current path
        'request_full_path': full_path,

        # The current full path with host
        'request_absolute_path': request.build_absolute_uri(),
        'image_absolute_path': request.build_absolute_uri(static_path),


        # Translation links
        'i18n_path': i18n_path,

        # Flag for guest users
        'has_demo_data': request.session.get('has_demo_data', False),

        # Don't show messages on AJAX requests (they are deleted if shown)
        'no_messages': request.META.get('HTTP_X_WGER_NO_MESSAGES', False),

        # Default cache time for template fragment caching
        'cache_timeout': settings.CACHES['default']['TIMEOUT'],

        # Used for logged in trainers
        'trainer_identity': request.session.get('trainer.identity'),
    }

    # Pseudo-intelligent navigation here
    if '/software/' in request.get_full_path() \
       or '/contact' in request.get_full_path() \
       or '/api/v2' in request.get_full_path():
            context['active_tab'] = constants.SOFTWARE_TAB
            context['show_shariff'] = True

    elif '/exercise/' in request.get_full_path():
        context['active_tab'] = constants.EXERCISE_TAB

    elif '/nutrition/' in request.get_full_path():
        context['active_tab'] = constants.NUTRITION_TAB

    elif '/weight/' in request.get_full_path():
        context['active_tab'] = constants.WEIGHT_TAB

    elif '/workout/' in request.get_full_path():
        context['active_tab'] = constants.WORKOUT_TAB

    else:
        context['active_tab'] = constants.USER_TAB

    return context
