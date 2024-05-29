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

# Standard Library
import logging

# Django
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy
from django.views.generic import UpdateView

# wger
from wger.config.models import GymConfig
from wger.utils.generic_views import WgerFormMixin


logger = logging.getLogger(__name__)


class GymConfigUpdateView(WgerFormMixin, UpdateView):
    """
    Generic view to edit the gym config table
    """

    model = GymConfig
    fields = ['default_gym']
    permission_required = 'config.change_gymconfig'
    success_url = reverse_lazy('gym:gym:list')
    title = gettext_lazy('Edit')

    def get_object(self):
        """
        Return the only gym config object
        """
        return GymConfig.objects.get(pk=1)
