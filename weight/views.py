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
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

from weight.models import WeightEntry


logger = logging.getLogger('workout_manager.custom')

class WeightForm(ModelForm):
    class Meta:
        model = WeightEntry
        exclude=('user',)

@login_required
def add(request, id=None):
    """Add a weight entry
    """
    
    template_data = {}
    template_data.update(csrf(request))
    template_data['active_tab'] = 'weight'
    
    # Load weight
    if id and id != 'None':
        weight = get_object_or_404(WeightEntry, pk=id, user=request.user)
    else:
        weight = WeightEntry()
    template_data['weight'] = weight
    
    # Process request
    if request.method == 'POST':
        weight_form = WeightForm(request.POST, instance=weight)
        
        # If the data is valid, save and redirect
        if weight_form.is_valid():
            weight = weight_form.save(commit=False)
            weight.user = request.user
            weight.save()
            
            return HttpResponseRedirect(reverse('weight.views.overview'))
    else:
        weight_form = WeightForm(instance=weight)
    template_data['weight_form'] = weight_form
    
    return render_to_response('edit.html',
                              template_data,
                              context_instance=RequestContext(request))

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
    weights = WeightEntry.objects.filter(user = request.user)
    template_data['weights'] = weights
    template_data['active_tab'] = 'weight'
    
    # Process the data to pass it to the JS libraries to generate an SVG image
    chart_data = "[\n"
    
    for i in weights:
        chart_data += '{x: "%(month)s/%(day)s/%(year)s", y: %(weight)s, id: %(id)s},\n' % {
                            'year': i.creation_date.year,
                            'month': i.creation_date.month,
                            'day': i.creation_date.day,
                            'weight': i.weight,
                            'id': '"entry-%s"' % i.id}
    
    chart_data = chart_data.rstrip(',')
    chart_data += "]"
    template_data['chart_data'] = chart_data
    
    return render_to_response('weight_overview.html',
                              template_data,
                              context_instance=RequestContext(request))
