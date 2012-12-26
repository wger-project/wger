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

from django.views.generic import TemplateView

from workout_manager.constants import SOFTWARE_TAB


class IssuesTemplateView(TemplateView):
    template_name = "issues.html"

    def get_context_data(self, **kwargs):
        context = super(IssuesTemplateView, self).get_context_data(**kwargs)
        context['active_tab'] = SOFTWARE_TAB
        return context
