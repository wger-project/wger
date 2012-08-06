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
import logging

from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.forms import ModelForm
from django.core.context_processors import csrf

from manager.models import TrainingSchedule
from manager.models import Exercise
from manager.models import ExerciseComment


logger = logging.getLogger('workout_manager.custom')

class WorkoutForm(ModelForm):
    class Meta:
        model = TrainingSchedule


def index(request):
    latest_trainings = TrainingSchedule.objects.all().order_by('-creation_date')[:5]
    return render_to_response('index.html', {'latest_workouts_list': latest_trainings})

    
# ************************
# Workout functions
# ************************
    
def view_workout(request, id):
    p = get_object_or_404(TrainingSchedule, pk=id)
    return render_to_response('detail.html', {'workout': p})
    
def add(request):
    template_data = {}
    template_data.update(csrf(request))
    
    if request.method == 'POST':
        workout_form = WorkoutForm(request.POST)
        new_workout = workout_form.save()
        return HttpResponseRedirect('/workout/add/step/2')
    else:
        workout_form = WorkoutForm()
    
    exercises = Exercise.objects.all()
    template_data['exercises'] = exercises
    
    
    template_data['workout_form'] = workout_form
    
    return render_to_response('add.html', template_data)

def add_step_2(request):
    template_data = {}
    
    return render_to_response('add.html', template_data)

def add_step_3(request):
    template_data = {}
    
    return render_to_response('add.html', template_data)

def add_step_4(request):
    template_data = {}
    
    return render_to_response('add.html', template_data)




# ************************
# Exercise functions
# ************************

class ExerciseCommentForm(ModelForm):
    class Meta:
        model = ExerciseComment
        exclude=('exercise',)

def exercise_overview(request):
    """Overview with all exercises
    """
    
    
    template_data = {}
    ex_data = {}
    
    # Gather all exercises and group them by category
    for i in Exercise.objects.all().order_by('category'):
        if not ex_data.get(i.category.id):
            ex_data[i.category.id] = {'category': i.category, 'exercises': []}
        
        ex_data[i.category.id]['exercises'].append(i)

    template_data['exercises'] = ex_data
    logger.debug(template_data)
    
    return render_to_response('exercise/overview.html', template_data)

    
def exercise_view(request, id):
    """ Detail view for an exercise
    """
    template_data = {}
    
    # Load the exercise itself
    exercise = get_object_or_404(Exercise, pk=id)
    template_data['exercise'] = exercise
    
    # We can create comments from this page, so look for Posts
    template_data.update(csrf(request))
    if request.method == 'POST':
        
        comment_form = ExerciseCommentForm(request.POST)
        comment_form.exercise = exercise
        #logger.debug(comment_form)
        #logger.debug(comment_form.errors)
        new_comment = comment_form.save(commit=False)
        new_comment.exercise = exercise
        new_comment.save()
        return HttpResponseRedirect('/exercise/view/%s' % id)
    else:
        comment_form = ExerciseCommentForm()
    
    template_data['comment_form'] = comment_form
    
    # Render
    return render_to_response('exercise/view.html', template_data)


def exercise_edit(request, id):
    exercise = get_object_or_404(Exercise, pk=id)
    return render_to_response('exercise/edit.html', {'exercise': exercise})