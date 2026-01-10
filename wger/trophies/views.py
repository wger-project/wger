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
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.views.generic import ListView

# wger
from wger.trophies.models import Trophy


logger = logging.getLogger(__name__)


class TrophiesOverview(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    All available trophies (even hidden ones).

    This is mainly to check that the descriptions, images, etc. are correct without having
    to earn them.
    """

    model = Trophy
    template_name = 'trophies/overview.html'
    permission_required = 'trophies.change_trophy'

    def get_queryset(self):
        """
        Return only the weight entries for the current user
        """
        return Trophy.objects.all()
