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

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from django.views.generic import ListView
from django.views.generic import DeleteView
from django.views.generic import CreateView
from django.views.generic import UpdateView

from wger.exercises.models import Muscle

from wger.workout_manager.generic_views import YamlFormMixin
from wger.workout_manager.generic_views import YamlDeleteMixin

logger = logging.getLogger('workout_manager.custom')


class MuscleListView(ListView):
    '''
    Overview of all muscles and their exercises
    '''
    model = Muscle
    queryset = Muscle.objects.all().order_by('-is_front', 'name'),
    context_object_name = 'muscle_list'
    template_name = 'muscles/overview.html'


class MuscleAddView(YamlFormMixin, CreateView):
    '''
    Generic view to add a new muscle
    '''

    model = Muscle
    success_url = reverse_lazy('muscle-overview')
    title = ugettext_lazy('Add muscle')
    form_action = reverse_lazy('muscle-add')


class MuscleUpdateView(YamlFormMixin, UpdateView):
    '''
    Generic view to update an existing muscle
    '''

    model = Muscle
    title = ugettext_lazy('Edit muscle')
    success_url = reverse_lazy('muscle-overview')

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(MuscleUpdateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('muscle-edit', kwargs={'pk': self.object.id})
        context['title'] = _('Edit %s') % self.object.name
        return context


class MuscleDeleteView(YamlDeleteMixin, DeleteView):
    '''
    Generic view to delete an existing muscle
    '''

    model = Muscle
    success_url = reverse_lazy('muscle-overview')

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(MuscleDeleteView, self).get_context_data(**kwargs)
        context['title'] = _('Delete muscle %s?') % self.object.name
        context['form_action'] = reverse('muscle-delete', kwargs={'pk': self.kwargs['pk']})
        return context
