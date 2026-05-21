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
from wger.nutrition.api.serializers import (
    LogItemSerializer,
    MealItemSerializer,
    MealSerializer,
    NutritionPlanSerializer,
)
from wger.nutrition.api.views import (
    LogItemViewSet,
    MealItemViewSet,
    MealViewSet,
    NutritionPlanViewSet,
)
from wger.nutrition.models import (
    LogItem,
    Meal,
    MealItem,
    NutritionPlan,
)
from wger.utils.powersync import (
    PowerSyncHandler,
    register_handler,
)


@register_handler
class NutritionPlanHandler(PowerSyncHandler):
    model = NutritionPlan
    serializer_class = NutritionPlanSerializer
    viewset_class = NutritionPlanViewSet


@register_handler
class MealHandler(PowerSyncHandler):
    """
    Meals live under a plan; ownership is enforced via the ``plan`` FK, not a
    direct user_id on the row. ``order`` defaults to 1, matching the existing
    REST ``perform_create``.
    """

    model = Meal
    serializer_class = MealSerializer
    viewset_class = MealViewSet
    user_filter = 'plan__user_id'

    def create_save_kwargs(self, payload, user_id):
        return {'order': payload.get('order', 1)}


@register_handler
class MealItemHandler(PowerSyncHandler):
    model = MealItem
    serializer_class = MealItemSerializer
    viewset_class = MealItemViewSet
    user_filter = 'meal__plan__user_id'

    def create_save_kwargs(self, payload, user_id):
        return {'order': payload.get('order', 1)}


@register_handler
class LogItemHandler(PowerSyncHandler):
    """Diary log entries — owned via the plan FK chain."""

    model = LogItem
    serializer_class = LogItemSerializer
    viewset_class = LogItemViewSet
    user_filter = 'plan__user_id'

    def create_save_kwargs(self, payload, user_id):
        return {}
