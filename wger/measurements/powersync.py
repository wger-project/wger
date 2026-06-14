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
from wger.measurements.api.serializers import (
    CategorySerializer,
    MeasurementSerializer,
)
from wger.measurements.api.views import MeasurementViewSet
from wger.measurements.models import (
    Category,
    Measurement,
)
from wger.utils.powersync import (
    PowerSyncHandler,
    register_handler,
)


@register_handler
class CategoryHandler(PowerSyncHandler):
    """Measurement categories — directly owned by ``user`` so no FK ownership check is needed."""

    model = Category
    serializer_class = CategorySerializer


@register_handler
class MeasurementHandler(PowerSyncHandler):
    """Measurements live under a ``Category``; ownership rides on that FK."""

    model = Measurement
    serializer_class = MeasurementSerializer
    viewset_class = MeasurementViewSet
    user_filter = 'category__user_id'

    def create_save_kwargs(self, payload, user_id):
        # Ownership is enforced through the category FK, not via a direct
        # user_id on the Measurement row.
        return {}
