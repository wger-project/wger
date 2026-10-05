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
from wger.measurements.models import Measurement


class WeightEntryFilterSet(filters.FilterSet):
    weight = filters.NumberFilter(field_name='value', lookup_expr='exact')
    weight__gt = filters.NumberFilter(field_name='value', lookup_expr='gt')
    weight__gte = filters.NumberFilter(field_name='value', lookup_expr='gte')
    weight__lt = filters.NumberFilter(field_name='value', lookup_expr='lt')
    weight__lte = filters.NumberFilter(field_name='value', lookup_expr='lte')

    class Meta:
        model = Measurement
        fields = {
            'id': ['exact', 'in'],
            'date': ['exact', 'gt', 'gte', 'lt', 'lte'],
        }
