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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy
from django.utils.translation import ugettext as _

from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DeleteView

from wger.exercises.models import Exercise
from wger.exercises.models import ExerciseImage

from wger.utils.generic_views import WgerFormMixin
from wger.utils.generic_views import WgerDeleteMixin
from wger.utils.generic_views import WgerPermissionMixin


logger = logging.getLogger('wger.custom')

'''
Exercise images
'''


class ExerciseImageEditView(WgerFormMixin, UpdateView, WgerPermissionMixin):
    '''
    Generic view to update an existing exercise image
    '''

    model = ExerciseImage
    title = ugettext_lazy('Edit exercise image')
    permission_required = 'exercises.change_exerciseimage'

    def get_success_url(self):
        return reverse('exercise-view', kwargs={'id': self.object.exercise.id})

    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(ExerciseImageEditView, self).get_context_data(**kwargs)
        context['enctype'] = 'multipart/form-data'
        context['form_action'] = reverse('exerciseimage-edit',
                                         kwargs={'pk': self.object.id})

        return context


class ExerciseImageAddView(WgerFormMixin, CreateView, WgerPermissionMixin):
    '''
    Generic view to add a new exercise image
    '''

    model = ExerciseImage
    title = ugettext_lazy('Add exercise image')
    permission_required = 'exercises.add_exerciseimage'

    def form_valid(self, form):
        form.instance.exercise = Exercise.objects.get(pk=self.kwargs['exercise_pk'])
        return super(ExerciseImageAddView, self).form_valid(form)

    def get_success_url(self):
        return reverse('exercise-view', kwargs={'id': self.object.exercise.id})

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(ExerciseImageAddView, self).get_context_data(**kwargs)
        context['enctype'] = 'multipart/form-data'
        context['form_action'] = reverse('exerciseimage-add',
                                         kwargs={'exercise_pk': self.kwargs['exercise_pk']})

        return context


class ExerciseImageDeleteView(WgerDeleteMixin, DeleteView, WgerPermissionMixin):
    '''
    Generic view to delete an existing exercise image
    '''

    model = ExerciseImage
    messages = ugettext_lazy('Successfully deleted')
    permission_required = 'exercises.delete_exerciseimage'

    def get_success_url(self):
        '''
        Return to exercise image
        '''
        return reverse('exercise-view', kwargs={'id': self.kwargs['exercise_pk']})

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        pk = self.kwargs['pk']
        exercise_pk = self.kwargs['exercise_pk']
        context = super(ExerciseImageDeleteView, self).get_context_data(**kwargs)

        context['title'] = _('Delete exercise image?')
        context['form_action'] = reverse('exerciseimage-delete',
                                         kwargs={'pk': pk, 'exercise_pk': exercise_pk})

        return context
