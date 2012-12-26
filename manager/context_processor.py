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
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.


from workout_manager import get_version

from manager.utils import load_language

from workout_manager import constants


def processor(request):

    context = {
        # Application version
        'version': get_version(),

        # Do not track header
        'DNT': request.META.get('HTTP_DNT', False),

        # User language
        'language': load_language(),

        # The current path
        'request_full_path': request.get_full_path()
    }

    # Pseudo-intelligent navigation here
    if '/software/' in request.get_full_path():
        context['active_tab'] = constants.SOFTWARE_TAB

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
