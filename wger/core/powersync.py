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

# wger
from wger.core.api.serializers import UserprofileSerializer
from wger.core.models import UserProfile
from wger.utils.powersync import (
    PowerSyncHandler,
    register_handler,
)


@register_handler
class UserProfileHandler(PowerSyncHandler):
    """
    The profile row is created together with the user account and must always
    exist, so PowerSync may only edit it
    """

    model = UserProfile
    serializer_class = UserprofileSerializer
    supports_create = False
    supports_delete = False
