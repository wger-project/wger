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
# You should have received a copy of the GNU Affero General Public License
#

# Standard Library
from datetime import datetime

# Django
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import (
    reverse,
    reverse_lazy,
)
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    UpdateView,
)

# wger
from wger.gallery.forms import ImageForm
from wger.gallery.models.image import Image
from wger.utils.generic_views import (
    WgerDeleteMixin,
    WgerFormMixin,
)


@login_required
def overview(request):
    """
    An overview of all the user's images
    """

    images = Image.objects.filter(user=request.user)
    context = {'images': images}

    return render(request, 'images/overview.html', context)


class ImageAddView(WgerFormMixin, CreateView):
    """
    Generic view to add a new weight entry
    """

    model = Image
    form_class = ImageForm
    title = _('Add')
    template_name = 'form_content.html'

    def get_initial(self):
        """
        Set the initial data for the form.

        Read the comment on weight/models.py WeightEntry about why we need
        to pass the user here.
        """
        return {'user': self.request.user, 'date': datetime.today()}

    def form_valid(self, form):
        """
        Set the owner of the entry here
        """
        form.instance.user = self.request.user
        return super(ImageAddView, self).form_valid(form)

    def get_success_url(self):
        """
        Return to overview
        """
        return reverse('gallery:images:overview')


class ImageUpdateView(WgerFormMixin, LoginRequiredMixin, UpdateView):
    """
    Generic view to edit an existing weight entry
    """

    model = Image
    form_class = ImageForm
    template_name = 'form_content.html'

    def get_context_data(self, **kwargs):
        context = super(ImageUpdateView, self).get_context_data(**kwargs)
        context['title'] = _('Edit')

        return context

    def get_success_url(self):
        """
        Return to overview
        """
        return reverse('gallery:images:overview')


class ImageDeleteView(WgerDeleteMixin, LoginRequiredMixin, DeleteView):
    """
    View to delete an existing image
    """

    model = Image
    success_url = reverse_lazy('gallery:images:overview')

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        context = super(ImageDeleteView, self).get_context_data(**kwargs)
        context['title'] = _('Delete {0}?').format(self.object)
        return context
