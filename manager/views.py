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
from manager.models import ExerciseCategory
from manager.models import Day
from manager.models import Set
from manager.models import Setting


logger = logging.getLogger('workout_manager.custom')

def index(request):
    latest_trainings = TrainingSchedule.objects.all().order_by('-creation_date')[:5]
    return render_to_response('index.html', {'latest_workouts_list': latest_trainings})

    
# ************************
# Workout functions
# ************************
class WorkoutForm(ModelForm):
    class Meta:
        model = TrainingSchedule

def view_workout(request, id):
    p = get_object_or_404(TrainingSchedule, pk=id)
    return render_to_response('workout/view.html', {'workout': p})
    
def add(request):
    
    workout = TrainingSchedule()
    workout.save()
    
    return HttpResponseRedirect('/workout/%s/view/' % workout.id)
    
    template_data = {}
    template_data.update(csrf(request))
    
    
    
    if request.method == 'POST':
        day_form = DayForm(request.POST)
        new_days = day_form.save()
        #return HttpResponseRedirect('/workout/add/step/2')
    else:
        day_form = DayForm()
    template_data['day_form'] = day_form
    
    if request.method == 'POST':
        workout_form = WorkoutForm(request.POST)
        new_workout = workout_form.save()
        return HttpResponseRedirect('/workout/add/step/2')
    else:
        workout_form = WorkoutForm()
    
    exercises = Exercise.objects.all()
    template_data['exercises'] = exercises
    
    
    template_data['workout_form'] = workout_form
    
    return render_to_response('workout/add.html', template_data)



# ************************
# Day functions
# ************************
class DayForm(ModelForm):
    class Meta:
        model = Day
        exclude=('training',)

def edit_day(request, id, day_id=None):
    template_data = {}
    template_data.update(csrf(request))
    
    # Load workout
    workout = get_object_or_404(TrainingSchedule, pk=id)
    template_data['workout'] = workout
    
    # Load day
    if not day_id:
        day = Day()
    else:
        day = get_object_or_404(Day, pk=day_id)
    template_data['day'] = day
    
    # Process request
    if request.method == 'POST':
        day_form = DayForm(request.POST, instance=day)
        day = day_form.save(commit=False)
        day.training = workout
        day.save()
        
        return HttpResponseRedirect('/workout/%s/view/' % id)
    else:
        day_form = DayForm(instance=day)
    template_data['day_form'] = day_form
    
    return render_to_response('day/edit.html', template_data)

def delete_day(request, id, day_id):
    # Load the day
    day = get_object_or_404(Day, pk=day_id)
    day.delete()
    
    return HttpResponseRedirect('/workout/%s/view/' % id)


# ************************
# Set functions
# ************************
class SetForm(ModelForm):
    class Meta:
        model = Set
        exclude = ('exerciseday', )

def edit_set(request, id, day_id, set_id=None):
    template_data = {}
    template_data.update(csrf(request))
    
    # Load workout
    workout = get_object_or_404(TrainingSchedule, pk=id)
    template_data['workout'] = workout
    
    # Load day
    day = get_object_or_404(Day, pk=day_id)
    template_data['day'] = day
    
    # Load set
    if not set_id:
        workout_set = Set()
    else:
        workout_set = get_object_or_404(Set, pk=set_id)
    template_data['set'] = workout_set
    
    # Process request
    if request.method == 'POST':
        set_form = SetForm(request.POST, instance=workout_set)
        workout_set = set_form.save(commit=False)
        workout_set.exerciseday = day
        workout_set.save()
        
        # The exercises are ManyToMany in DB, so we have to save with this function
        set_form.save_m2m()
        
        return HttpResponseRedirect('/workout/%s/view/' % id)
    else:
        set_form = SetForm(instance=workout_set)
    template_data['set_form'] = set_form
    
    return render_to_response('set/edit.html', template_data)

def delete_set(request, id, day_id, set_id):
    # Load the set
    set_obj = get_object_or_404(Set, pk=set_id)
    set_obj.delete()
    
    return HttpResponseRedirect('/workout/%s/view/' % id)

# ************************
# Exercise comment functions
# ************************

def exercisecomment_delete(request, id):
    # Load the comment
    comment = get_object_or_404(ExerciseComment, pk=id)
    exercise_id = comment.exercise.id
    comment.delete()
    
    return HttpResponseRedirect('/exercise/view/%s' % exercise_id)
    
    

# ************************
# Exercise functions
# ************************

class ExerciseCommentForm(ModelForm):
    class Meta:
        model = ExerciseComment
        exclude=('exercise',)

class ExerciseForm(ModelForm):
    class Meta:
        model = Exercise

class ExerciseCategoryForm(ModelForm):
    class Meta:
        model = ExerciseCategory

def exercise_overview(request):
    """Overview with all exercises
    """
    
    template_data = {}
    template_data['categories'] = ExerciseCategory.objects.all()
    
    return render_to_response('exercise/overview.html', template_data)

    
def exercise_view(request, id, comment_id=None):
    """ Detail view for an exercise
    """
    template_data = {}
    template_data['comment_edit'] = False
    
    # Load the exercise itself
    exercise = get_object_or_404(Exercise, pk=id)
    template_data['exercise'] = exercise
    
    #
    # We can create and edit comments from this page, so look for Posts
    template_data.update(csrf(request))
    
    # Adding a new comment
    if request.method == 'POST' and not comment_id:
        comment_form = ExerciseCommentForm(request.POST)
        comment_form.exercise = exercise
        new_comment = comment_form.save(commit=False)
        new_comment.exercise = exercise
        new_comment.save()
        return HttpResponseRedirect('/exercise/view/%s' % id)
    else:
        comment_form = ExerciseCommentForm()

    # Editing a comment
    if comment_id:
        exercise_comment = get_object_or_404(ExerciseComment, pk=comment_id)
        template_data['comment_edit'] = exercise_comment
        
        comment_edit_form = ExerciseCommentForm(instance=exercise_comment)
        template_data['comment_edit_form'] = comment_edit_form
        
        if request.method == 'POST':
            logger.debug(exercise_comment.id)
            comment_form = ExerciseCommentForm(request.POST, instance=exercise_comment)
            comment = comment_form.save(commit=False)
            comment.save()
            return HttpResponseRedirect('/exercise/view/%s' % id)
        
    
    template_data['comment_form'] = comment_form
    
    # Render
    return render_to_response('exercise/view.html', template_data)


def exercise_edit(request, id=None):
    template_data = {}
    template_data.update(csrf(request))
    
    if not id:
        exercise = Exercise()
    else:
        exercise = get_object_or_404(Exercise, pk=id)
    template_data['exercise'] = exercise
    
    if request.method == 'POST':
        exercise_form = ExerciseForm(request.POST, instance=exercise)
        if exercise_form.is_valid():
            exercise = exercise_form.save()
            id = exercise.id
            return HttpResponseRedirect('/exercise/view/%s' % id)
    else:
        exercise_form = ExerciseForm(instance=exercise)
    
    template_data['edit_form'] = exercise_form
    
    return render_to_response('exercise/edit.html', template_data)


def exercise_delete(request, id):
    # Load the exercise
    exercise = get_object_or_404(Exercise, pk=id)
    exercise.delete()
    
    return HttpResponseRedirect('/exercise/overview/')

def exercise_category_edit(request, id):
    template_data = {}
    template_data.update(csrf(request))
    
    if not id:
        category = ExerciseCategory()
    else:
        category = get_object_or_404(ExerciseCategory, pk=id)
    template_data['category'] = category
    
    if request.method == 'POST':
        category_form = ExerciseCategoryForm(request.POST, instance=category)
        
        # If the data is valid, save and redirect
        if category_form.is_valid():
            category = category_form.save()
            return HttpResponseRedirect('/exercise/overview/')
    else:
        category_form = ExerciseCategoryForm(instance=category)
    
    template_data['category_form'] = category_form
    
    return render_to_response('exercise/edit_category.html', template_data)


def exercise_category_delete(request, id):
    # Load the category
    category = get_object_or_404(ExerciseCategory, pk=id)
    category.delete()
    
    return HttpResponseRedirect('/exercise/overview/')

# ************************
# Settings functions
# ************************
class SettingForm(ModelForm):
    class Meta:
        model = Setting
        #exclude = ('exerciseday', )




def edit_setting(request, id, set_id, setting_id=None):
    template_data = {}
    template_data.update(csrf(request))
    
    # Load workout
    workout = get_object_or_404(TrainingSchedule, pk=id)
    template_data['workout'] = workout
    
    # Load set
    set_obj = get_object_or_404(Set, pk=day_id)
    template_data['set'] = set_obj
    
    # Load setting
    if not setting_id:
        setting = Setting()
    else:
        setting = get_object_or_404(Setting, pk=setting_id)
    template_data['setting'] = setting
    
    # Process request
    if request.method == 'POST':
        setting_form = SettingForm(request.POST, instance=setting)
        setting = setting_form.save(commit=False)
        #setting.exerciseday = day
        setting.save()
        
        # The exercises are ManyToMany in DB, so we have to save with this function
        #set_form.save_m2m()
        
        return HttpResponseRedirect('/workout/%s/view/' % id)
    else:
        setting_form = SettingForm(instance=setting)
    template_data['setting_form'] = setting_form
    
    return render_to_response('setting/edit.html', template_data)