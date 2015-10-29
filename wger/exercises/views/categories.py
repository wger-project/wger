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
#
# You should have received a copy of the GNU Affero General Public License
import logging

from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from django.views.generic import (
    DeleteView,
    CreateView,
    UpdateView
)

from wger.exercises.models import ExerciseCategory

from wger.utils.generic_views import (
    WgerFormMixin,
    WgerDeleteMixin,
    WgerPermissionMixin
)
from wger.utils.language import load_language


logger = logging.getLogger(__name__)


# ************************
#   Exercise categories
# ************************


class ExerciseCategoryAddView(WgerFormMixin, CreateView, WgerPermissionMixin):
    '''
    Generic view to add a new exercise category
    '''

    model = ExerciseCategory
    fields = '__all__'
    success_url = reverse_lazy('exercise:exercise:overview')
    title = ugettext_lazy('Add category')
    form_action = reverse_lazy('exercise:category:add')
    permission_required = 'exercises.add_exercisecategory'

    def form_valid(self, form):
        form.instance.language = load_language()
        return super(ExerciseCategoryAddView, self).form_valid(form)


class ExerciseCategoryUpdateView(WgerFormMixin, UpdateView, WgerPermissionMixin):
    '''
    Generic view to update an existing exercise category
    '''

    model = ExerciseCategory
    fields = '__all__'
    success_url = reverse_lazy('exercise:exercise:overview')
    permission_required = 'exercises.change_exercisecategory'

    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(ExerciseCategoryUpdateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('exercise:category:edit', kwargs={'pk': self.object.id})
        context['title'] = _(u'Edit {0}').format(self.object.name)

        return context

    def form_valid(self, form):
        form.instance.language = load_language()

        return super(ExerciseCategoryUpdateView, self).form_valid(form)


class ExerciseCategoryDeleteView(WgerDeleteMixin, DeleteView, WgerPermissionMixin):
    '''
    Generic view to delete an existing exercise category
    '''

    model = ExerciseCategory
    success_url = reverse_lazy('exercise:exercise:overview')
    delete_message = ugettext_lazy('This will also delete all exercises in this category.')
    messages = ugettext_lazy('Successfully deleted')
    permission_required = 'exercises.delete_exercisecategory'

    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(ExerciseCategoryDeleteView, self).get_context_data(**kwargs)

        context['title'] = _(u'Delete {0}?').format(self.object.name)
        context['form_action'] = reverse('exercise:category:delete', kwargs={'pk': self.object.id})

        return context
