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
from wger.measurements.api.views import (
    CategoryViewSet,
    MeasurementViewSet,
)
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
    """
    Measurement categories — directly owned by ``user``; the ``parent`` FK
    (multi-value groups) additionally needs an ownership check.
    """

    model = Category
    serializer_class = CategorySerializer
    viewset_class = CategoryViewSet
    json_fields = frozenset({'chart_config', 'dynamic_params'})

    # The serializer checks the "one category per metric type" rule, for which
    # it needs to know whose categories to look at
    pass_user_id_in_context = True

    def handle_delete(self, payload, user_id):
        entry = self._get_or_none(payload, user_id)
        if entry is not None and entry.is_official:
            return {
                'error': 'Forbidden',
                'details': 'Official categories cannot be deleted',
            }
        return super().handle_delete(payload, user_id)


@register_handler
class MeasurementHandler(PowerSyncHandler):
    """Measurements live under a ``Category``; ownership rides on that FK."""

    model = Measurement
    serializer_class = MeasurementSerializer
    viewset_class = MeasurementViewSet
    user_filter = 'category__user_id'
    json_fields = frozenset({'extra_data'})

    def create_save_kwargs(self, payload, user_id):
        # Ownership is enforced through the category FK, not via a direct
        # user_id on the Measurement row.
        return {}
