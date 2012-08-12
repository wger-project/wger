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

import datetime

from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.forms import ModelForm
from django.core.context_processors import csrf

from weight.models import WeightEntry

class WeightForm(ModelForm):
    class Meta:
        model = WeightEntry

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

def overview(request):
    """Shows an overview of weight data
    """
    template_data = {}
    
    template_data['weights'] = WeightEntry.objects.all()
    
    return render_to_response('overview.html', template_data)