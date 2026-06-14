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

# Third Party
from rest_framework.throttling import ScopedRateThrottle


class CreateScopedRateThrottle(ScopedRateThrottle):
    """
    Scoped rate throttle that only limits object creation (POST requests).

    Reads, edits and deletes pass through unthrottled, so browsing and editing
    stay fast. Used to cap how quickly new exercises and translations can be
    created through the API.

    Users with the ``exercises.add_exercise`` permission are exempt.
    """

    def allow_request(self, request, view):
        if request.method != 'POST':
            return True

        user = request.user
        if user.is_authenticated and user.has_perm('exercises.add_exercise'):
            return True

        return super().allow_request(request, view)
