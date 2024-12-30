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

# Django
from django.conf import settings
from django.templatetags.static import static
from django.utils.translation import get_language

# wger
from wger.config.models import GymConfig
from wger.utils import constants
from wger.utils.constants import ENGLISH_SHORT_NAME
from wger.utils.language import get_language_data


def processor(request):
    languages_dict = dict(settings.AVAILABLE_LANGUAGES)
    full_path = request.get_full_path()
    i18n_path = {}
    static_path = static('images/logos/logo-social.png')

    for lang in settings.AVAILABLE_LANGUAGES:
        i18n_path[lang[0]] = '/{0}/{1}'.format(lang[0], '/'.join(full_path.split('/')[2:]))

    # yapf: disable
    context = {
        'mastodon': settings.WGER_SETTINGS['MASTODON'],
        'twitter': settings.WGER_SETTINGS['TWITTER'],

        # Languages
        'i18n_language':
            get_language_data(
                (get_language(), languages_dict.get(get_language(), ENGLISH_SHORT_NAME)),
            ),
        'languages': settings.AVAILABLE_LANGUAGES,

        # The current path
        'request_full_path': full_path,

        # The current full path with host
        'request_absolute_path': request.build_absolute_uri(),
        'image_absolute_path': request.build_absolute_uri(static_path),

        # Translation links
        'i18n_path': i18n_path,
        'is_api_path': '/api/' in request.build_absolute_uri(),

        # Flag for guest users
        'has_demo_data': request.session.get('has_demo_data', False),

        # Don't show messages on AJAX requests (they are deleted if shown)
        'no_messages': request.META.get('HTTP_X_WGER_NO_MESSAGES', False),

        # Default cache time for template fragment caching
        'cache_timeout': settings.CACHES['default']['TIMEOUT'],

        # Used for logged in trainers
        'trainer_identity': request.session.get('trainer.identity'),

        # current gym, if available
        'custom_header': get_custom_header(request),
    }
    # yapf: enable

    # Pseudo-intelligent navigation here
    if (
        '/software/' in request.get_full_path()
        or '/contact' in request.get_full_path()
        or '/api/v2' in request.get_full_path()
    ):
        context['active_tab'] = constants.SOFTWARE_TAB

    elif '/exercise/' in request.get_full_path():
        context['active_tab'] = constants.WORKOUT_TAB

    elif '/nutrition/' in request.get_full_path():
        context['active_tab'] = constants.NUTRITION_TAB

    elif '/weight/' in request.get_full_path():
        context['active_tab'] = constants.WEIGHT_TAB

    elif '/workout/' in request.get_full_path():
        context['active_tab'] = constants.WORKOUT_TAB

    return context


def get_custom_header(request):
    """
    Loads the custom header for the application, if available

    Currently the header can only be overwritten to use the user's current gym
    """

    # Current gym
    current_gym = None
    if request.user.is_authenticated and request.user.userprofile.gym:
        current_gym = request.user.userprofile.gym
    else:
        global_gymconfig = GymConfig.objects.get(pk=1)
        if global_gymconfig.default_gym:
            current_gym = global_gymconfig.default_gym

    # Put the custom header together
    custom_header = None
    if current_gym and current_gym.config.show_name:
        custom_header = current_gym.name
    return custom_header
