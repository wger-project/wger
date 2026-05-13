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


# Django
from django.db.models import (
    Exists,
    OuterRef,
    Q,
    QuerySet,
)

# Third Party
from django_filters import rest_framework as filters

# wger
from wger.exercises.models import (
    Exercise,
    Translation,
)
from wger.utils.db import is_postgres_db
from wger.utils.language import load_language


class ExerciseFilterSet(filters.FilterSet):
    """
    Filters for the regular exercises endpoints to support fulltext name search
    and language filtering, similar to IngredientFilterSet.
    """

    name__search = filters.CharFilter(method='search_name_fulltext')
    name__exact = filters.CharFilter(method='search_name_exact')
    language__code = filters.CharFilter(method='search_language_code')

    def _languages_from_params(self):
        if languages_param := self.data.get('language__code'):
            return [load_language(code) for code in set(languages_param.split(','))]
        return None

    def _filter_by_translation(self, queryset: QuerySet, q_expr: Q) -> QuerySet:
        translation_subquery = Translation.objects.filter(exercise=OuterRef('pk')).filter(q_expr)
        if languages := self._languages_from_params():
            translation_subquery = translation_subquery.filter(language__in=languages)
        return queryset.filter(Exists(translation_subquery)).distinct()

    def search_name_fulltext(self, queryset: QuerySet, name: str, value: str):
        """
        Searches for exercise matches with the given name.

        If the database is postgres a fuzzy full-text search is used, otherwise a simple
        exact match,
        """

        if not value:
            return queryset

        if not is_postgres_db():
            return self.search_name_exact(queryset, name, value)

        # Note: this uses the default value for pg_trgm.similarity_threshold (0.3)
        return self._filter_by_translation(
            queryset=queryset,
            q_expr=Q(name__trigram_similar=value) | Q(alias__alias__icontains=value),
        )

    def search_name_exact(self, queryset: QuerySet, name: str, value: str):
        """
        Searches for exact exercise matches with the given name
        """

        if not value:
            return queryset

        return self._filter_by_translation(
            queryset=queryset,
            q_expr=Q(name__icontains=value) | Q(alias__alias__icontains=value),
        )

    def search_language_code(self, queryset: QuerySet, name: str, value: str):
        if not value:
            return queryset

        # If a name filter is active, it already restricts translations, so
        # applying it again here would produce a redundant WHERE clause.
        if self.data.get('name__search') or self.data.get('name__exact'):
            return queryset

        languages = [load_language(code) for code in set(value.split(','))]
        if not languages:
            return queryset
        return queryset.filter(translations__language__in=languages).distinct()

    class Meta:
        model = Exercise
        fields = {
            'id': ['exact', 'in'],
            'uuid': ['exact'],
            'category': ['exact', 'in'],
            'muscles': ['exact', 'in'],
            'muscles_secondary': ['exact', 'in'],
            'equipment': ['exact', 'in'],
            'variation_group': ['exact', 'in'],
        }
