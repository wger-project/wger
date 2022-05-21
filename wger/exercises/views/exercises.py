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
from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.core import mail
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
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.template.loader import render_to_string
from django.urls import (
    reverse,
    reverse_lazy,
)
from django.utils.translation import (
    gettext as _,
    gettext_lazy,
)
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
)

# Third Party
from crispy_forms.layout import (
    Column,
    Layout,
    Row,
)

# wger
from wger.exercises.models import (
    Equipment,
    Exercise,
    ExerciseBase,
    ExerciseCategory,
    Muscle,
)
from wger.manager.models import WorkoutLog
from wger.utils.constants import MIN_EDIT_DISTANCE_THRESHOLD
from wger.utils.generic_views import (
    WgerDeleteMixin,
    WgerFormMixin,
)
from wger.utils.helpers import levenshtein
from wger.utils.language import load_language
from wger.utils.widgets import TranslatedSelectMultiple
from wger.weight.helpers import process_log_entries


logger = logging.getLogger(__name__)


class ExerciseListView(ListView):
    """
    Generic view to list all exercises
    """

    model = ExerciseBase
    template_name = 'exercise/overview.html'
    context_object_name = 'bases'

    def get_queryset(self):
        """
        Filter to only active exercises in the configured languages
        """
        return ExerciseBase.objects.all() \
            .order_by('category_id') \
            .select_related()

    def get_context_data(self, **kwargs):
        """
        Pass additional data to the template
        """
        context = super(ExerciseListView, self).get_context_data(**kwargs)
        context['show_shariff'] = True
        return context


def view(request, id, slug=None):
    """
    Detail view for an exercise
    """

    exercise = get_object_or_404(Exercise, pk=id)
    context = {
        'comment_edit': False,
        'show_shariff': True,
        'exercise': exercise,
        "muscles_main_front": exercise.muscles.filter(is_front=True),
        "muscles_main_back": exercise.muscles.filter(is_front=False),
        "muscles_sec_front": exercise.muscles_secondary.filter(is_front=True),
        "muscles_sec_back": exercise.muscles_secondary.filter(is_front=False),
    }

    # If the user is logged in, load the log and prepare the entries for
    # rendering in the D3 chart
    entry_log = []
    chart_data = []
    if request.user.is_authenticated:
        logs = WorkoutLog.objects.filter(user=request.user, exercise_base=exercise.exercise_base)
        entry_log, chart_data = process_log_entries(logs)

    context['logs'] = entry_log
    context['json'] = chart_data
    context['svg_uuid'] = str(uuid.uuid4())
    context['cache_vary_on'] = "{}-{}".format(exercise.id, load_language().id)
    context['allow_upload_videos'] = settings.WGER_SETTINGS['ALLOW_UPLOAD_VIDEOS']

    return render(request, 'exercise/view.html', context)


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


class ExerciseDeleteView(
    WgerDeleteMixin,
    LoginRequiredMixin,
    PermissionRequiredMixin,
    DeleteView,
):
    """
    Generic view to delete an existing exercise
    """

    model = Exercise
    fields = ('description', 'name')
    success_url = reverse_lazy('exercise:exercise:overview')
    delete_message_extra = gettext_lazy('This will delete the exercise from all workouts.')
    messages = gettext_lazy('Successfully deleted')
    permission_required = 'exercises.delete_exercise'

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        context = super(ExerciseDeleteView, self).get_context_data(**kwargs)
        context['title'] = _('Delete {0}?').format(self.object.name)
        return context
