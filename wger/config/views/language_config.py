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

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext as _
from django.views.generic import UpdateView

from wger.config.models import LanguageConfig
from wger.utils.generic_views import WgerFormMixin


logger = logging.getLogger(__name__)


class LanguageConfigUpdateView(WgerFormMixin,
                               LoginRequiredMixin,
                               PermissionRequiredMixin,
                               UpdateView):
    '''
    Generic view to edit a language config
    '''
    model = LanguageConfig
    fields = ['show']
    permission_required = 'config.change_languageconfig'

    def get_success_url(self):
        '''
        Return to the language page
        '''
        return reverse_lazy('core:language:view', kwargs={'pk': self.object.language_id})

    def get_context_data(self, **kwargs):
        context = super(LanguageConfigUpdateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('config:language_config:edit',
                                         kwargs={'pk': self.object.id})
        context['title'] = _('Edit')

        return context
