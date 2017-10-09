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

# Third Party
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import (
    reverse,
    reverse_lazy
)
from django.db.models import (
    Max,
    Min
)
from django.http import (
    HttpResponse,
    HttpResponseRedirect
)
from django.shortcuts import render
from django.utils.translation import (
    ugettext as _,
    ugettext_lazy
)
from django.views.generic import (
    CreateView,
    UpdateView
)
from formtools.preview import FormPreview
from rest_framework.decorators import api_view
from rest_framework.response import Response

# wger
from wger.utils.generic_views import WgerFormMixin
from wger.utils.helpers import check_access
from wger.body_measurements import helpers
from wger.body_measurements.forms import BodyMeasurementsEntryForm
from wger.body_measurements.models import BodyMeasurementsEntry


logger = logging.getLogger(__name__)


class BodyMeasurementsAddView(WgerFormMixin, CreateView):
    '''
    Generic view to add a new BodyMeasurements entry
    '''
    model = BodyMeasurementsEntry
    form_class = BodyMeasurementsEntryForm
    title = ugettext_lazy('Add BodyMeasurements entry')
    form_action = reverse_lazy('BodyMeasurements:add')

    def get_initial(self):
        '''
        Set the initial data for the form.

        Read the comment on BodyMeasurements/models.py BodyMeasurementsEntry about why we need
        to pass the user here.
        '''
        return {'user': self.request.user,
                'date': datetime.date.today()}

    def form_valid(self, form):
        '''
        Set the owner of the entry here
        '''
        form.instance.user = self.request.user
        return super(BodyMeasurementsAddView, self).form_valid(form)

    def get_success_url(self):
        '''
        Return to overview with username
        '''
        return reverse('BodyMeasurements:overview', kwargs={'username': self.object.user.username})


class BodyMeasurementsUpdateView(WgerFormMixin, UpdateView):
    '''
    Generic view to edit an existing BodyMeasurements entry
    '''
    model = BodyMeasurementsEntry
    form_class = BodyMeasurementsEntryForm

    def get_context_data(self, **kwargs):
        context = super(BodyMeasurementsUpdateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('BodyMeasurements:edit', kwargs={'pk': self.object.id})
        context['title'] = _('Edit BodyMeasurements entry for the %s') % self.object.date

        return context

    def get_success_url(self):
        '''
        Return to overview with username
        '''
        return reverse('BodyMeasurements:overview', kwargs={'username': self.object.user.username})


@login_required
def export_csv(request):
    '''
    Exports the saved BodyMeasurements data as a CSV file
    '''

    # Prepare the response headers
    response = HttpResponse(content_type='text/csv')

    # Convert all BodyMeasurements data to CSV
    writer = csv.writer(response)

    BodyMeasurementss = BodyMeasurementsEntry.objects.filter(user=request.user)
    writer.writerow([_('BodyMeasurements').encode('utf8'), _('Date').encode('utf8')])

    for entry in BodyMeasurementss:
        writer.writerow([entry.BodyMeasurements, entry.date])

    # Send the data to the browser
    response['Content-Disposition'] = 'attachment; filename=BodyMeasurementsdata.csv'
    response['Content-Length'] = len(response.content)
    return response


def overview(request, username=None):
    '''
    Shows a plot with the body measurements data

    More info about the D3 library can be found here:
        * https://github.com/mbostock/d3
        * http://d3js.org/
    '''
    is_owner, user = check_access(request.user, username)

    template_data = {}

    min_date = BodyMeasurementsEntry.objects.filter(user=user).\
        aggregate(Min('date'))['date__min']
    max_date = BodyMeasurementsEntry.objects.filter(user=user).\
        aggregate(Max('date'))['date__max']
    if min_date:
        template_data['min_date'] = 'new Date(%(year)s, %(month)s, %(day)s)' % \
                                    {'year': min_date.year,
                                     'month': min_date.month,
                                     'day': min_date.day}
    if max_date:
        template_data['max_date'] = 'new Date(%(year)s, %(month)s, %(day)s)' % \
                                    {'year': max_date.year,
                                     'month': max_date.month,
                                     'day': max_date.day}

    last_body_measurements_entries = helpers.get_last_entries(user)

    template_data['is_owner'] = is_owner
    template_data['owner_user'] = user
    template_data['show_shariff'] = is_owner
    template_data['last_five_body_measurements_entries_details'] = last_body_measurements_entries
    return render(request, 'overview.html', template_data)


@api_view(['GET'])
def get_body_measurements_data(request, username=None):
    '''
    Process the data to pass it to the JS libraries to generate an SVG image
    '''

    is_owner, user = check_access(request.user, username)

    date_min = request.GET.get('date_min', False)
    date_max = request.GET.get('date_max', True)

    if date_min and date_max:
        BodyMeasurementss = BodyMeasurementsEntry.objects.filter(user=user,
                                             date__range=(date_min, date_max))
    else:
        BodyMeasurementss = BodyMeasurementsEntry.objects.filter(user=user)

    chart_data = []

    for i in BodyMeasurementss:
        chart_data.append({'date': i.date,
                           'BodyMeasurements': i.BodyMeasurements})

    # Return the results to the client
    return Response(chart_data)


class BodyMeasurementsCsvImportFormPreview(FormPreview):
    preview_template = 'import_csv_preview.html'
    form_template = 'import_csv_form.html'

    def get_context(self, request, form):
        '''
        Context for template rendering.
        '''

        return {'form': form,
                'stage_field': self.unused_name('stage'),
                'state': self.state,
                'form_action': reverse('BodyMeasurements:import-csv')}

    def process_preview(self, request, form, context):
        context['body_measurements_list'], context['error_list'] = helpers.parse_body_measurements_csv(request,
                                                                                 form.cleaned_data)
        return context

    def done(self, request, cleaned_data):
        body_measurements_list, error_list = helpers.parse_body_measurements_csv(request, cleaned_data)
        BodyMeasurementsEntry.objects.bulk_create(body_measurements_list)
        return HttpResponseRedirect(reverse('BodyMeasurements:overview',
                                            kwargs={'username': request.user.username}))
