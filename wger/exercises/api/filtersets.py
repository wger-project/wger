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
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import (
    Exists,
    OuterRef,
    Q,
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
    language__code = filters.CharFilter(method='search_languagecode')

    def search_name_fulltext(self, queryset, name, value):
        if not value:
            return queryset

        languages_param = self.data.get('language__code')
        languages = None
        if languages_param:
            languages = [load_language(code) for code in set(languages_param.split(','))]

        if is_postgres_db():
            translation_subquery = Translation.objects.filter(exercise=OuterRef('pk'))
            if languages:
                translation_subquery = translation_subquery.filter(language__in=languages)
            translation_subquery = translation_subquery.annotate(
                similarity=TrigramSimilarity('name', value)
            ).filter(Q(similarity__gt=0.15) | Q(alias__alias__icontains=value))

            qs = queryset.filter(Exists(translation_subquery))
        else:
            translation_subquery = Translation.objects.filter(exercise=OuterRef('pk')).filter(
                Q(name__icontains=value) | Q(alias__alias__icontains=value)
            )
            if languages:
                translation_subquery = translation_subquery.filter(language__in=languages)
            qs = queryset.filter(Exists(translation_subquery))

        return qs.distinct()

    def search_languagecode(self, queryset, name, value):
        if not value:
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
        }
