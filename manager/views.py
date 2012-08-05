# This file is part of Workout Manager.
# 
# Foobar is free software: you can redistribute it and/or modify
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

from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import Http404
from manager.models import TrainingSchedule


def index(request):
    latest_trainings = TrainingSchedule.objects.all().order_by('-creation_date')[:5]
    return render_to_response('index.html', {'latest_workouts_list': latest_trainings})
    

def add(request):
    return render_to_response('add.html')

def view_workout(request, id):
    p = get_object_or_404(TrainingSchedule, pk=id)
    return render_to_response('detail.html', {'workout': p})