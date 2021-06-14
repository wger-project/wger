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
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin
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
    Textarea
)
from django.http import (
    HttpResponseForbidden,
    HttpResponseRedirect
)
from django.shortcuts import (
    get_object_or_404,
    render
)
from django.template.loader import render_to_string
from django.urls import (
    reverse,
    reverse_lazy
)
from django.utils.cache import patch_vary_headers
from django.utils.translation import (
    gettext as _,
    gettext_lazy
)
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView
)

# Third Party
from crispy_forms.layout import (
    Column,
    Layout,
    Row
)

# wger
from django.views.generic.base import TemplateResponseMixin

from wger.config.models import LanguageConfig
from wger.exercises.models import (
    Equipment,
    Exercise,
    ExerciseBase,
    ExerciseCategory,
    Muscle
)
from wger.manager.models import WorkoutLog
from wger.utils.constants import MIN_EDIT_DISTANCE_THRESHOLD
from wger.utils.generic_views import (
    WgerDeleteMixin,
    WgerFormMixin
)
from wger.utils.helpers import levenshtein
from wger.utils.language import (
    load_item_languages,
    load_language
)
from wger.utils.widgets import TranslatedSelectMultiple
from wger.weight.helpers import process_log_entries


logger = logging.getLogger(__name__)



@permission_required('exercises.change_exercise')
def overview(request):
    """
    Generic view to list the history of the exercises
    """
    context = {}

    out = []
    history = Exercise.history.all()
    for entry in history:
        if entry.prev_record:
            out.append({'record': entry,
                        'delta':  entry.diff_against(entry.prev_record)})


    context['history'] = out

    return render(request, 'history/list.html', context)
