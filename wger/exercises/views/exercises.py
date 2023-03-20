# -*- coding: utf-8 -*-

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
# You should have received a copy of the GNU Affero General Public License

# Standard Library
import logging
import uuid

# Django
from django.conf import settings
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.core.exceptions import ValidationError
from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    ModelChoiceField,
    ModelForm,
    ModelMultipleChoiceField,
    Select,
    Textarea,
)
from django.http import (
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.urls import (
    reverse,
    reverse_lazy,
)
from django.utils.translation import (
    gettext as _,
    gettext_lazy,
)
from django.views.generic import (
    DeleteView,
    TemplateView,
)

# wger
from wger.exercises.models import (
    Equipment,
    Exercise,
    ExerciseCategory,
    Muscle,
)
from wger.manager.models import WorkoutLog
from wger.utils.constants import MIN_EDIT_DISTANCE_THRESHOLD
from wger.utils.generic_views import WgerDeleteMixin
from wger.utils.helpers import levenshtein
from wger.utils.language import load_language
from wger.utils.widgets import TranslatedSelectMultiple
from wger.weight.helpers import process_log_entries


logger = logging.getLogger(__name__)


class ExerciseListView(TemplateView):
    """
    Generic view to list all exercises
    """
    template_name = 'exercise/overview.html'


def view(request, id, slug=None):
    """
    Detail view for an exercise translation
    """
    exercise = get_object_or_404(Exercise, pk=id)

    return HttpResponsePermanentRedirect(
        reverse(
            'exercise:exercise:view-base', kwargs={
                'pk': exercise.exercise_base_id,
                'slug': slug
            }
        )
    )


class ExerciseForm(ModelForm):
    # Redefine some fields here to set some properties
    # (some of this could be done with a crispy form helper and would be
    # a cleaner solution)
    category = ModelChoiceField(queryset=ExerciseCategory.objects.all(), widget=Select())
    muscles = ModelMultipleChoiceField(
        queryset=Muscle.objects.all(),
        widget=CheckboxSelectMultiple(),
        required=False,
    )

    muscles_secondary = ModelMultipleChoiceField(
        queryset=Muscle.objects.all(),
        widget=CheckboxSelectMultiple(),
        required=False,
    )

    equipment = ModelMultipleChoiceField(
        queryset=Equipment.objects.all(),
        widget=CheckboxSelectMultiple(),
        required=False,
    )

    description = CharField(
        label=_('Description'),
        widget=Textarea,
        required=False,
    )

    class Meta:
        model = Exercise
        widgets = {'equipment': TranslatedSelectMultiple()}
        fields = [
            'name',
            'category',
            'description',
            'muscles',
            'muscles_secondary',
            'equipment',
            'license',
            'license_author',
        ]

    class Media:
        js = (settings.STATIC_URL + 'yarn/tinymce/tinymce.min.js', )

    def clean_name(self):
        """
        Throws a validation error if the newly submitted name is too similar to
        an existing exercise's name
        """
        name = self.cleaned_data['name']

        if not self.instance.id:
            language = load_language()
            exercises = Exercise.objects.all() \
                .filter(language=language)
            for exercise in exercises:
                exercise_name = str(exercise)
                min_edit_dist = levenshtein(exercise_name.casefold(), name.casefold())
                if min_edit_dist < MIN_EDIT_DISTANCE_THRESHOLD:
                    raise ValidationError(
                        _('%(name)s is too similar to existing exercise '
                          '"%(exercise_name)s"'),
                        params={
                            'name': name,
                            'exercise_name': exercise_name
                        },
                    )
        return name
