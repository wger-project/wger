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
import csv
import datetime

from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils import formats
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.db.models import Min
from django.db.models import Max
from django.views.generic import CreateView
from django.views.generic import UpdateView

from rest_framework.response import Response
from rest_framework.decorators import api_view

from formtools.preview import FormPreview

from wger.weight.forms import WeightForm
from wger.weight.models import WeightEntry
from wger.weight import helpers
from wger.utils.helpers import check_access
from wger.utils.generic_views import WgerFormMixin


logger = logging.getLogger(__name__)


class WeightAddView(WgerFormMixin, CreateView):
    '''
    Generic view to add a new weight entry
    '''
    model = WeightEntry
    form_class = WeightForm
    title = ugettext_lazy('Add weight entry')
    form_action = reverse_lazy('weight:add')

    def get_initial(self):
        '''
        Set the initial data for the form.

        Read the comment on weight/models.py WeightEntry about why we need
        to pass the user here.
        '''
        return {'user': self.request.user,
                'date': datetime.date.today()}

    def form_valid(self, form):
        '''
        Set the owner of the entry here
        '''
        form.instance.user = self.request.user
        return super(WeightAddView, self).form_valid(form)

    def get_success_url(self):
        '''
        Return to overview with username
        '''
        return reverse('weight:overview', kwargs={'username': self.object.user.username})


class WeightUpdateView(WgerFormMixin, UpdateView):
    '''
    Generic view to edit an existing weight entry
    '''
    model = WeightEntry
    form_class = WeightForm

    def get_context_data(self, **kwargs):
        context = super(WeightUpdateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('weight:edit', kwargs={'pk': self.object.id})
        context['title'] = _('Edit weight entry for the %s') % self.object.date

        return context

    def get_success_url(self):
        '''
        Return to overview with username
        '''
        return reverse('weight:overview', kwargs={'username': self.object.user.username})


@login_required
def export_csv(request):
    '''
    Exports the saved weight data as a CSV file
    '''

    # Prepare the response headers
    response = HttpResponse(content_type='text/csv')

    # Convert all weight data to CSV
    writer = csv.writer(response)

    weights = WeightEntry.objects.filter(user=request.user)
    writer.writerow([_('Weight').encode('utf8'), _('Date').encode('utf8')])

    for entry in weights:
        writer.writerow([entry.weight, entry.date])

    # Send the data to the browser
    response['Content-Disposition'] = 'attachment; filename=Weightdata.csv'
    response['Content-Length'] = len(response.content)
    return response


def overview(request, username=None):
    '''
    Shows a plot with the weight data

    More info about the D3 library can be found here:
        * https://github.com/mbostock/d3
        * http://d3js.org/
    '''
    is_owner, user = check_access(request.user, username)

    template_data = {}

    min_date = WeightEntry.objects.filter(user=user).\
        aggregate(Min('date'))['date__min']
    max_date = WeightEntry.objects.filter(user=user).\
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

    last_weight_entries = helpers.get_last_entries(user)

    template_data['is_owner'] = is_owner
    template_data['owner_user'] = user
    template_data['show_shariff'] = is_owner
    template_data['last_five_weight_entries_details'] = last_weight_entries
    return render(request, 'overview.html', template_data)


@api_view(['GET'])
def get_weight_data(request, username=None):
    '''
    Process the data to pass it to the JS libraries to generate an SVG image
    '''

    is_owner, user = check_access(request.user, username)

    date_min = request.GET.get('date_min', False)
    date_max = request.GET.get('date_max', True)

    if date_min and date_max:
        weights = WeightEntry.objects.filter(user=user,
                                             date__range=(date_min, date_max))
    else:
        weights = WeightEntry.objects.filter(user=user)

    chart_data = []

    for i in weights:
        chart_data.append({'date': i.date,
                           'weight': i.weight})

    # Return the results to the client
    return Response(chart_data)


class WeightCsvImportFormPreview(FormPreview):
    preview_template = 'import_csv_preview.html'
    form_template = 'import_csv_form.html'

    def get_context(self, request, form):
        '''
        Context for template rendering.
        '''

        return {'form': form,
                'stage_field': self.unused_name('stage'),
                'state': self.state,
                'form_action': reverse('weight:import-csv')}

    def process_preview(self, request, form, context):
        context['weight_list'], context['error_list'] = helpers.parse_weight_csv(request,
                                                                                 form.cleaned_data)
        return context

    def done(self, request, cleaned_data):
        weight_list, error_list = helpers.parse_weight_csv(request, cleaned_data)
        WeightEntry.objects.bulk_create(weight_list)
        return HttpResponseRedirect(reverse('weight:overview',
                                            kwargs={'username': request.user.username}))
