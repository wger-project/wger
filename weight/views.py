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
import csv
import json

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.forms import ModelForm
from django.forms import DateField
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.db.models import Min
from django.db.models import Max

from django.views.generic import DeleteView
from django.views.generic import CreateView
from django.views.generic import UpdateView

from weight.models import WeightEntry

from workout_manager.generic_views import YamlFormMixin
from workout_manager.constants import WEIGHT_TAB
from workout_manager.constants import DATE_FORMATS


logger = logging.getLogger('workout_manager.custom')

class WeightForm(ModelForm):
    creation_date = DateField(input_formats=DATE_FORMATS)
    class Meta:
        model = WeightEntry
        exclude=('user',)

class WeightAddView(YamlFormMixin, CreateView):
    """
    Generic view to add a new weight entry
    """
    active_tab = WEIGHT_TAB
    model = WeightEntry
    form_class = WeightForm   
    custom_js = '''$(document).ready(function () {
        init_weight_datepicker();
    });'''
    title = ugettext_lazy('Add weight entry')
    form_action = reverse_lazy('weight-add')
    success_url = reverse_lazy('weight.views.overview')
      
  
    def form_valid(self, form):
        """
        Set the owner of the entry here
        """
        
        form.instance.user = self.request.user
        return super(WeightAddView, self).form_valid(form)


class WeightUpdateView(YamlFormMixin, UpdateView):
    """
    Generic view to edit an existing weight entry
    """
    active_tab = WEIGHT_TAB
    model = WeightEntry
    form_class = WeightForm
    custom_js = '''$(document).ready(function () {
        init_weight_datepicker();
    });'''
    success_url = reverse_lazy('weight.views.overview')
      
  
    def get_context_data(self, **kwargs):
        context = super(WeightUpdateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('weight-edit', kwargs={'pk': self.object.id})
        context['title'] = _('Edit weight entry for the %s') % self.object.creation_date
        
        return context

@login_required
def export_csv(request):
    """Exports the saved weight data as a CSV file
    """
    
    # Prepare the response headers
    filename = "%s-%s" % (_('weightdata'), request.user.username)
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % filename
    
    # Convert all weight data to CSV
    writer = csv.writer(response)
    
    weights = WeightEntry.objects.filter(user = request.user)
    writer.writerow([_('Weight'), _('Date')]) 
    
    for entry in weights:
        writer.writerow([entry.weight, entry.creation_date])
    
    # Send the data to the browser
    return response
    
@login_required
def overview(request):
    """Shows a plot with the weight data
    
    More info about the D3 library can be found here:
        * https://github.com/mbostock/d3
        * http://d3js.org/
    """
    template_data = {}
    template_data['active_tab'] = WEIGHT_TAB
    
    min_date = WeightEntry.objects.filter(user = request.user).aggregate(Min('creation_date'))['creation_date__min']
    max_date = WeightEntry.objects.filter(user = request.user).aggregate(Max('creation_date'))['creation_date__max']
    if min_date:
        template_data['min_date'] = 'new Date(%(year)s, %(month)s, %(day)s)' % {'year': min_date.year,
                                                                                'month': min_date.month,
                                                                                'day': min_date.day}
    if max_date:
        template_data['max_date'] = 'new Date(%(year)s, %(month)s, %(day)s)' % {'year': max_date.year,
                                                                                'month': max_date.month,
                                                                                'day': max_date.day}
    return render_to_response('weight_overview.html',
                              template_data,
                              context_instance=RequestContext(request))

@login_required
def get_weight_data(request):
    # Process the data to pass it to the JS libraries to generate an SVG image
    
    if request.is_ajax():
        date_min = request.GET.get('date_min', False)
        date_max = request.GET.get('date_max', True)
        
        if date_min and date_max:
            weights = WeightEntry.objects.filter(user = request.user,
                                                 creation_date__range=(date_min, date_max))
        else:
            weights = WeightEntry.objects.filter(user = request.user)
        
        chart_data = []
        
        for i in weights:
            chart_data.append({'x': "%(month)s/%(day)s/%(year)s" % {
                                    'year': i.creation_date.year,
                                    'month': i.creation_date.month,
                                    'day': i.creation_date.day},
                               'y': i.weight,
                               'id': i.id})
        
        
        # Return the results to the server
        mimetype = 'application/json'
        return HttpResponse(json.dumps(chart_data), mimetype)
