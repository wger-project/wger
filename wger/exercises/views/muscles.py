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
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from django.views.generic import (
    ListView,
    DeleteView,
    CreateView,
    UpdateView
)

from wger.exercises.models import Muscle
from wger.utils.generic_views import (
    WgerFormMixin,
    WgerDeleteMixin
)
from wger.utils.language import load_item_languages
from wger.config.models import LanguageConfig

logger = logging.getLogger(__name__)


class MuscleListView(ListView):
    '''
    Overview of all muscles and their exercises
    '''
    model = Muscle
    queryset = Muscle.objects.all().order_by('-is_front', 'name'),
    context_object_name = 'muscle_list'
    template_name = 'muscles/overview.html'

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(MuscleListView, self).get_context_data(**kwargs)
        context['active_languages'] = load_item_languages(LanguageConfig.SHOW_ITEM_EXERCISES)
        context['show_shariff'] = True
        return context


class MuscleAdminListView(LoginRequiredMixin, PermissionRequiredMixin, MuscleListView):
    '''
    Overview of all muscles, for administration purposes
    '''
    permission_required = 'exercises.change_muscle'
    queryset = Muscle.objects.order_by('name')
    template_name = 'muscles/admin-overview.html'


class MuscleAddView(WgerFormMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    '''
    Generic view to add a new muscle
    '''

    model = Muscle
    fields = '__all__'
    success_url = reverse_lazy('exercise:muscle:admin-list')
    title = ugettext_lazy('Add muscle')
    form_action = reverse_lazy('exercise:muscle:add')
    permission_required = 'exercises.add_muscle'


class MuscleUpdateView(WgerFormMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    '''
    Generic view to update an existing muscle
    '''

    model = Muscle
    fields = '__all__'
    success_url = reverse_lazy('exercise:muscle:admin-list')
    permission_required = 'exercises.change_muscle'

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(MuscleUpdateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('exercise:muscle:edit', kwargs={'pk': self.object.id})
        context['title'] = _(u'Edit {0}').format(self.object.name)
        return context


class MuscleDeleteView(WgerDeleteMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    '''
    Generic view to delete an existing muscle
    '''

    model = Muscle
    fields = ('name', 'is_front')
    success_url = reverse_lazy('exercise:muscle:admin-list')
    permission_required = 'exercises.delete_muscle'
    messages = ugettext_lazy('Successfully deleted')

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(MuscleDeleteView, self).get_context_data(**kwargs)
        context['title'] = _(u'Delete {0}?').format(self.object.name)
        context['form_action'] = reverse('exercise:muscle:delete', kwargs={'pk': self.kwargs['pk']})
        return context
