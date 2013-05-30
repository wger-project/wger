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

from django.forms import ModelForm
from django.template import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from django.contrib import messages
from django.views.generic import ListView
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import DeleteView
from django.views.generic import UpdateView

from wger.exercises.models import Language

from wger.config.models import LanguageConfig

from wger.utils.generic_views import YamlDeleteMixin
from wger.utils.generic_views import YamlFormMixin
from wger.utils.generic_views import WgerPermissionMixin
from wger.utils.language import load_language

logger = logging.getLogger('workout_manager.custom')


class LanguageConfigUpdateView(YamlFormMixin, UpdateView):
    '''
    Generic view to edit a language config
    '''
    model = LanguageConfig
    permission_required = 'config.change_languageconfig'

    def get_success_url(self):
        '''
        Return to the language page
        '''
        return reverse_lazy('config:language-view', kwargs={'pk': self.object.language_target_id})

    def get_context_data(self, **kwargs):
        context = super(LanguageConfigUpdateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('config:languageconfig-edit',
                                         kwargs={'pk': self.object.id})
        context['title'] = _('Edit')

        return context
