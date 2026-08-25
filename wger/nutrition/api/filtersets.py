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
from django.contrib.postgres.search import (
    TrigramSimilarity,
    TrigramStrictWordSimilarity,
)
from django.db.models import (
    Case,
    F,
    IntegerField,
    Q,
    Value,
    When,
)

# Third Party
from django_filters import rest_framework as filters

# wger
from wger.core.models import Language
from wger.nutrition.models import (
    Ingredient,
    LogItem,
)
from wger.utils.db import (
    PostgresILikeContains,
    PostgresILikeExact,
    PostgresILikeStartsWith,
    is_postgres_db,
)
from wger.utils.language import load_language


logger = logging.getLogger(__name__)


def _has_literal_trigram(value: str) -> bool:
    """Return whether a substring lookup has a guaranteed indexable trigram."""
    consecutive = 0
    for character in value:
        consecutive = consecutive + 1 if character.isalnum() else 0
        if consecutive == 3:
            return True
    return False


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
    language__code = filters.CharFilter(
        method='search_languagecode',
        help_text=(
            'Filter by language code. Multiple values may be separated by commas. '
            'Unknown codes are ignored.'
        ),
    )

    def search_barcode(self, queryset, name, value):
        """
        'exact' search for the barcode.

        It this is not known locally, try fetching the result from OFF
        """

        if not value:
            return queryset

        result = queryset.filter(code=value)
        if not result.exists():
            logger.debug('barcode not found locally, trying to fetch ingredient from OFF')
            ingredient = Ingredient.fetch_ingredient_from_off(value)
            if ingredient is not None:
                result = queryset.filter(pk=ingredient.pk)

        return result

    def search_name_fulltext(self, queryset, name, value):
        """
        Try a barcode lookup first, then perform a fulltext search when Postgres is available
        """

        # If a numeric value looks like a barcode (EAN-8, UPC-A, EAN-13, GTIN-14),
        # try an exact barcode lookup first.
        if value.isdigit() and len(value) in (8, 12, 13, 14):
            barcode_qs = self.search_barcode(queryset, 'code', value)

            if barcode_qs.exists():
                return barcode_qs

        if is_postgres_db():
            if not any(character.isalnum() for character in value):
                return queryset.none()

            # A trigram index cannot accelerate unrestricted one- or two-character
            # substring patterns. Exact matching still supports valid short names.
            if len(value) < 3:
                exact = PostgresILikeExact(F('name'), value)
                return queryset.filter(exact).order_by('name')

            exact = PostgresILikeExact(F('name'), value)
            starts_with = PostgresILikeStartsWith(F('name'), value)
            contains = PostgresILikeContains(F('name'), value)

            candidates = Q(name__trigram_similar=value)
            # Whole-name similarity already retrieves specific multi-word queries;
            # the extra substring scan is useful for single terms in long names.
            if len(value.split(maxsplit=1)) == 1 and _has_literal_trigram(value):
                candidates |= contains

            return (
                queryset.filter(candidates)
                .annotate(
                    word_similarity=TrigramStrictWordSimilarity(value, 'name'),
                    similarity=TrigramSimilarity('name', value),
                )
                .annotate(
                    match_rank=Case(
                        When(exact, then=Value(3)),
                        When(starts_with, then=Value(2)),
                        When(word_similarity=1, then=Value(1)),
                        default=Value(0),
                        output_field=IntegerField(),
                    ),
                )
                .order_by('-match_rank', '-similarity', 'name')
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
        languages = []
        for code in set(value.split(',')):
            try:
                languages.append(load_language(code, default_to_english=False))
            except Language.DoesNotExist:
                pass
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
