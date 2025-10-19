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
from django_filters import rest_framework as filters

# wger
from wger.weight.models import WeightEntry


class WeightEntryFilterSet(filters.FilterSet):
    class Meta:
        model = WeightEntry
        fields = {
            'id': ['exact', 'in'],
            'weight': ['exact', 'gt', 'gte', 'lt', 'lte'],
            'date': ['exact', 'gt', 'gte', 'lt', 'lte'],
        }
