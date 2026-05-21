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

# Standard Library
from typing import Any

# wger
from wger.utils.powersync import (
    PowerSyncHandler,
    register_handler,
)
from wger.weight.api.serializers import WeightEntrySerializer
from wger.weight.models import WeightEntry


@register_handler
class WeightEntryHandler(PowerSyncHandler):
    """
    Body weight uses a client-supplied UUID as the synchronised primary key,
    so the handler must round-trip the payload's ``id`` into the ``uuid``
    column on create.
    """

    model = WeightEntry
    serializer_class = WeightEntrySerializer
    lookup_field = 'uuid'

    def create_save_kwargs(self, payload: dict[str, Any], user_id: int) -> dict[str, Any]:
        return {'user_id': user_id, 'uuid': payload['id']}
