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
import datetime

from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.forms import ModelForm
from django.core.context_processors import csrf
from django.contrib.auth.decorators import permission_required, login_required

from weight.models import WeightEntry


logger = logging.getLogger('workout_manager.custom')

class WeightForm(ModelForm):
    class Meta:
        model = WeightEntry

@login_required
def add(request, id=None):
    """Add a weight entry
    """
    
    template_data = {}
    template_data.update(csrf(request))
    
    # Load weight
    if id:
        weight = get_object_or_404(WeightEntry, pk=id)
    else:
        weight = WeightEntry()
    template_data['weight'] = weight
    
    # Process request
    if request.method == 'POST':
        weight_form = WeightForm(request.POST, instance=weight)
        
        # If the data is valid, save and redirect
        if weight_form.is_valid():
            weight = weight_form.save(commit=False)
            
            weight.save()
            
            return HttpResponseRedirect('/weight/overview/')
    else:
        weight_form = WeightForm()
    template_data['weight_form'] = weight_form
    
    return render_to_response('edit.html', template_data)

@login_required
def overview(request):
    """Shows an overview of weight data
    
    More info about the JS can be found here:
        * http://wijmo.com/wiki/index.php/Scatterchart
    """
    template_data = {}
    weights = WeightEntry.objects.all()
    template_data['weights'] = weights
    
    # Process the data to pass it to the JS libraries to generate an SVG image
    data_y = ', '.join([str(i.weight) for i in weights])
    data_x = ', '.join(["new Date(%s, %s, %s)" % (i.creation_date.year,
                                                  i.creation_date.month,
                                                  i.creation_date.day) for i in weights])
    
    template_data['data_x'] = data_x
    template_data['data_y'] = data_y
    
    return render_to_response('weight_overview.html', template_data)
