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
import logging

# Django
from django.contrib.postgres.search import TrigramSimilarity

# Third Party
from django_filters import rest_framework as filters

# wger
from wger.nutrition.models import (
    Ingredient,
    LogItem,
)
from wger.utils.db import is_postgres_db
from wger.utils.language import load_language


logger = logging.getLogger(__name__)


class LogItemFilterSet(filters.FilterSet):
    class Meta:
        model = LogItem
        fields = {
            'datetime': ['exact', 'date', 'gt', 'gte', 'lt', 'lte'],
            'amount': ['exact'],
            'ingredient': ['exact'],
            'plan': ['exact'],
            'weight_unit': ['exact'],
        }


class IngredientFilterSet(filters.FilterSet):
    code = filters.CharFilter(method='search_barcode')
    name__search = filters.CharFilter(method='search_name_fulltext')
    language__code = filters.CharFilter(method='search_languagecode')

    def search_barcode(self, queryset, name, value):
        """
        'exact' search for the barcode.

        It this is not known locally, try fetching the result from OFF
        """

        if not value:
            return queryset

        queryset = queryset.filter(code=value)
        if queryset.count() == 0:
            logger.debug('barcode not found locally, trying to fetch ingredient from OFF')
            Ingredient.fetch_ingredient_from_off(value)

        return queryset

    def search_name_fulltext(self, queryset, name, value):
        """
        Perform a fulltext search when postgres is available
        """

        if is_postgres_db():
            # Note: this uses the default value for pg_trgm.similarity_threshold (0.3) which
            # might be too strict (doesn't find "butter" from "buttr"). If this needs to be
            # changed later, e.g.:

            # with connection.cursor() as cursor:
            #     cursor.execute('SET LOCAL pg_trgm.similarity_threshold = 0.15')

            return (
                queryset.filter(name__trigram_similar=value)
                .annotate(similarity=TrigramSimilarity('name', value))
                .order_by('-similarity', 'name')
            )
        else:
            # Explicit order_by('name') because the viewset strips Meta.ordering.
            # Search results are small, so sorting them is cheap.
            return queryset.filter(name__icontains=value).order_by('name')

    def search_languagecode(self, queryset, name, value):
        """
        Filter based on language codes, not IDs

        Also accepts a comma-separated list of codes. Unknown codes are ignored
        and duplicates removed.
        """
        languages = [load_language(l) for l in set(value.split(','))]
        if languages:
            queryset = queryset.filter(language__in=languages)

        return queryset

    class Meta:
        model = Ingredient
        fields = {
            'id': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'uuid': ['exact'],
            'code': ['exact'],
            'source_name': ['exact'],
            'name': ['exact'],
            'energy': ['exact'],
            'protein': ['exact'],
            'carbohydrates': ['exact'],
            'carbohydrates_sugar': ['exact'],
            'fat': ['exact'],
            'fat_saturated': ['exact'],
            'fiber': ['exact'],
            'sodium': ['exact'],
            'is_vegan': ['exact'],
            'is_vegetarian': ['exact'],
            'nutriscore': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'created': ['exact', 'gt', 'lt'],
            'last_update': ['exact', 'gt', 'lt'],
            'last_imported': ['exact', 'gt', 'lt'],
            'language': ['exact', 'in'],
            'license': ['exact'],
            'license_author': ['exact'],
        }
