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
from django.views.generic import UpdateView

from wger.config.models import GymConfig
from wger.utils.generic_views import WgerFormMixin


logger = logging.getLogger(__name__)


class GymConfigUpdateView(WgerFormMixin, UpdateView):
    '''
    Generic view to edit the gym config table
    '''
    model = GymConfig
    fields = '__all__'
    permission_required = 'config.change_gymconfig'
    success_url = reverse_lazy('gym:gym:list')

    def get_object(self):
        '''
        Return the only gym config object
        '''
        return GymConfig.objects.get(pk=1)

    def get_context_data(self, **kwargs):
        context = super(GymConfigUpdateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('config:gym_config:edit')
        context['title'] = _('Edit')
        return context
