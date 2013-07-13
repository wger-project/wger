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

from django.views.generic import TemplateView
from django.core.urlresolvers import reverse


class ContextTemplateView(TemplateView):
    '''
    Overwrite TemplateView so we can use 'contribute' within a
    blocktrans block.
    '''
    def get_context_data(self, **kwargs):
        context = super(ContextTemplateView, self).get_context_data(**kwargs)
        context.update({'contribute': reverse('software:contribute')})
        return context
