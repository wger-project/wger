#  This file is part of wger Workout Manager <https://github.com/wger-project>.
#  Copyright (C) 2013 - 2021 wger Team
#
#  wger Workout Manager is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  wger Workout Manager is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Standard Library
import logging

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import (
    reverse,
    reverse_lazy,
)
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    DeleteView,
    ListView,
)

# wger
from wger.exercises.models import Exercise
from wger.favorites.models import Favorite


logger = logging.getLogger(__name__)


class FavoritesOverview(LoginRequiredMixin, ListView):
    """
    View to display all favorite exercises for the current user.
    """

    model = Favorite
    template_name = 'favorites/overview.html'
    context_object_name = 'favorites'
    paginate_by = 20

    def get_queryset(self):
        """
        Return only the current user's favorites, ordered by creation date.
        """
        return Favorite.objects.filter(
            user=self.request.user
        ).select_related(
            'exercise'
        ).prefetch_related(
            'exercise__translations',
            'exercise__exerciseimage_set',
        ).order_by('-created')

    def get_context_data(self, **kwargs):
        """
        Add additional context data.
        """
        context = super().get_context_data(**kwargs)
        context['title'] = _('My Favorites')
        return context


class FavoriteDeleteView(LoginRequiredMixin, DeleteView):
    """
    View to remove an exercise from favorites.
    """

    model = Favorite
    success_url = reverse_lazy('favorites:overview')

    def get_queryset(self):
        """
        Ensure users can only delete their own favorites.
        """
        return Favorite.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        """
        Add exercise information to context.
        """
        context = super().get_context_data(**kwargs)
        context['exercise'] = self.object.exercise
        context['title'] = _('Remove from Favorites')
        return context
