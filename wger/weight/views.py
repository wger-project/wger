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
import csv
import datetime
import logging

# Django
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
)
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import (
    gettext as _,
    gettext_lazy,
)
from django.views.generic import (
    CreateView,
    DeleteView,
    UpdateView,
)

# Third Party
from formtools.preview import FormPreview

# wger
from wger.utils.generic_views import (
    WgerDeleteMixin,
    WgerFormMixin,
)
from wger.utils.helpers import check_access
from wger.weight import helpers
from wger.weight.forms import WeightForm
from wger.weight.models import WeightEntry


logger = logging.getLogger(__name__)


class WeightAddView(WgerFormMixin, CreateView):
    """
    Generic view to add a new weight entry
    """

    model = WeightEntry
    form_class = WeightForm
    title = gettext_lazy('Add weight entry')

    def get_initial(self):
        """
        Set the initial data for the form.

        Read the comment on weight/models.py WeightEntry about why we need
        to pass the user here.
        """
        return {'user': self.request.user, 'date': datetime.date.today()}

    def form_valid(self, form):
        """
        Set the owner of the entry here
        """
        form.instance.user = self.request.user
        return super(WeightAddView, self).form_valid(form)

    def get_success_url(self):
        """
        Return to overview with username
        """
        return reverse('weight:overview')


class WeightUpdateView(WgerFormMixin, LoginRequiredMixin, UpdateView):
    """
    Generic view to edit an existing weight entry
    """

    model = WeightEntry
    form_class = WeightForm

    def get_context_data(self, **kwargs):
        context = super(WeightUpdateView, self).get_context_data(**kwargs)
        context['title'] = _('Edit weight entry for the %s') % self.object.date

        return context

    def get_success_url(self):
        """
        Return to overview with username
        """
        return reverse('weight:overview')


class WeightDeleteView(WgerDeleteMixin, LoginRequiredMixin, DeleteView):
    """
    Generic view to delete a weight entry
    """

    model = WeightEntry
    messages = gettext_lazy('Successfully deleted.')

    def get_context_data(self, **kwargs):
        context = super(WeightDeleteView, self).get_context_data(**kwargs)
        context['title'] = _('Delete weight entry for the %s') % self.object.date
        return context

    def get_success_url(self):
        """
        Return to overview with username
        """
        return reverse('weight:overview')


@login_required
def export_csv(request):
    """
    Exports the saved weight data as a CSV file
    """

    # Prepare the response headers
    response = HttpResponse(content_type='text/csv')

    # Convert all weight data to CSV
    writer = csv.writer(response)

    weights = WeightEntry.objects.filter(user=request.user)
    writer.writerow([_('Date'), _('Weight')])

    for entry in weights:
        writer.writerow([entry.date, entry.weight])

    # Send the data to the browser
    response['Content-Disposition'] = 'attachment; filename=Weightdata.csv'
    response['Content-Length'] = len(response.content)
    return response


class WeightCsvImportFormPreview(FormPreview):
    preview_template = 'import_csv_preview.html'
    form_template = 'import_csv_form.html'

    def get_context(self, request, form):
        """
        Context for template rendering.
        """

        return {
            'form': form,
            'stage_field': self.unused_name('stage'),
            'state': self.state,
        }

    def process_preview(self, request, form, context):
        context['weight_list'], context['error_list'] = helpers.parse_weight_csv(
            request, form.cleaned_data
        )
        return context

    def done(self, request, cleaned_data):
        weight_list, error_list = helpers.parse_weight_csv(request, cleaned_data)
        WeightEntry.objects.bulk_create(weight_list)
        return HttpResponseRedirect(reverse('weight:overview'))
