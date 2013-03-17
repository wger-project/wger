# -*- coding: utf-8 -*-

# This file is part of Workout Manager.
#
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
import logging
import json
import uuid

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.forms import ModelForm
from django.forms import ModelChoiceField
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import permission_required
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from django.views.generic import ListView
from django.views.generic import DeleteView
from django.views.generic import CreateView
from django.views.generic import UpdateView

from wger.manager.utils import load_language

from wger.manager.models import WorkoutLog

from wger.exercises.models import Exercise
from wger.exercises.models import ExerciseComment
from wger.exercises.models import ExerciseCategory
from wger.exercises.models import Muscle

from wger.workout_manager.generic_views import YamlFormMixin
from wger.workout_manager.generic_views import YamlDeleteMixin


logger = logging.getLogger('workout_manager.custom')


# ************************
#   Exercise categories
# ************************
class ExerciseCategoryForm(ModelForm):
    class Meta:
        model = ExerciseCategory
        exclude = ('language',)


class ExerciseCategoryAddView(YamlFormMixin, CreateView):
    '''
    Generic view to add a new exercise category
    '''

    model = ExerciseCategory
    form_class = ExerciseCategoryForm
    success_url = reverse_lazy('wger.exercises.views.exercises.exercise_overview')
    title = ugettext_lazy('Add category')
    form_action = reverse_lazy('exercisecategory-add')

    def form_valid(self, form):
        form.instance.language = load_language()

        return super(ExerciseCategoryAddView, self).form_valid(form)


class ExerciseCategoryUpdateView(YamlFormMixin, UpdateView):
    '''
    Generic view to update an existing exercise category
    '''

    model = ExerciseCategory
    form_class = ExerciseCategoryForm
    success_url = reverse_lazy('wger.exercises.views.exercises.exercise_overview')

    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(ExerciseCategoryUpdateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('exercisecategory-edit', kwargs={'pk': self.object.id})
        context['title'] = _('Edit %s') % self.object.name

        return context

    def form_valid(self, form):
        form.instance.language = load_language()

        return super(ExerciseCategoryUpdateView, self).form_valid(form)


class ExerciseCategoryDeleteView(YamlDeleteMixin, DeleteView):
    '''
    Generic view to delete an existing exercise category
    '''

    model = ExerciseCategory
    success_url = reverse_lazy('wger.exercises.views.exercises.exercise_overview')
    delete_message = ugettext_lazy('This will also delete all exercises in this category.')

    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(ExerciseCategoryDeleteView, self).get_context_data(**kwargs)

        context['title'] = _('Delete category %s?') % self.object.name
        context['form_action'] = reverse('exercise-delete', kwargs={'pk': self.kwargs['pk']})

        return context
