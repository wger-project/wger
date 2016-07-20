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

from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import permission_required
from django.utils.translation import ugettext_lazy

from django.views.generic import CreateView, UpdateView

from wger.exercises.forms import CommentForm
from wger.exercises.models import Exercise, ExerciseComment
from wger.utils.generic_views import WgerFormMixin


logger = logging.getLogger(__name__)


# ************************
#    Exercise comments
# ************************


class ExerciseCommentEditView(WgerFormMixin,
                              LoginRequiredMixin,
                              PermissionRequiredMixin,
                              UpdateView):
    '''
    Generic view to update an existing exercise comment
    '''

    model = ExerciseComment
    form_class = CommentForm
    title = ugettext_lazy('Edit')
    permission_required = 'exercises.change_exercisecomment'

    def get_success_url(self):
        return reverse('exercise:exercise:view', kwargs={'id': self.object.exercise.id})

    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(ExerciseCommentEditView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('exercise:comment:edit',
                                         kwargs={'pk': self.object.id})

        return context


class ExerciseCommentAddView(WgerFormMixin,
                             LoginRequiredMixin,
                             PermissionRequiredMixin,
                             CreateView):
    '''
    Generic view to add a new exercise comment
    '''

    model = ExerciseComment
    form_class = CommentForm
    title = ugettext_lazy('Add exercise comment')
    permission_required = 'exercises.add_exercisecomment'

    def form_valid(self, form):
        form.instance.exercise = Exercise.objects.get(pk=self.kwargs['exercise_pk'])
        return super(ExerciseCommentAddView, self).form_valid(form)

    def get_success_url(self):
        return reverse('exercise:exercise:view', kwargs={'id': self.object.exercise.id})

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(ExerciseCommentAddView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('exercise:comment:add',
                                         kwargs={'exercise_pk': self.kwargs['exercise_pk']})

        return context


@permission_required('exercises.delete_exercisecomment')
def delete(request, id):
    # Load the comment
    comment = get_object_or_404(ExerciseComment, pk=id)
    exercise_id = comment.exercise.id
    comment.delete()

    return HttpResponseRedirect(reverse('exercise:exercise:view', kwargs={'id': exercise_id}))
