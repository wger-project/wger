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
import calendar
import json

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.forms import ModelForm
from django.forms import Textarea
from django.forms.models import modelformset_factory
from django.core.context_processors import csrf
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import permission_required, login_required
from django.utils.translation import ugettext as _
from django.utils import translation


from exercises.models import Language
from exercises.models import Exercise
from exercises.models import ExerciseComment
from exercises.models import ExerciseCategory

logger = logging.getLogger('workout_manager.custom')

# ************************
# Exercise comment functions
# ************************
@permission_required('manager.add_exercisecomment')
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
        
        widgets = {
            'description': Textarea(attrs={'cols': 80, 'rows': 10}),
        }

class ExerciseCategoryForm(ModelForm):
    class Meta:
        model = ExerciseCategory
        exclude=('language',)
        

def exercise_overview(request):
    """Overview with all exercises
    """
    #TODO: check that this works on edge cases
    language = get_object_or_404(Language, short_name = translation.get_language())
    
    template_data = {}
    template_data['categories'] = ExerciseCategory.objects.filter(language = language.id)
    
    return render_to_response('overview.html',
                              template_data,
                              context_instance=RequestContext(request))

    
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
        
        # If the data is valid, save and redirect
        if comment_form.is_valid():
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
            comment_form = ExerciseCommentForm(request.POST, instance=exercise_comment)
            
            # If the data is valid, save and redirect
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.save()
                return HttpResponseRedirect('/exercise/view/%s' % id)
        
    
    template_data['comment_form'] = comment_form
    
    # Render
    return render_to_response('view.html',
                              template_data,
                              context_instance=RequestContext(request))

@permission_required('exercises.change_exercise')
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
        
        # If the data is valid, save and redirect
        if exercise_form.is_valid():
            exercise = exercise_form.save()
            id = exercise.id
            return HttpResponseRedirect('/exercise/view/%s' % id)
    else:
        exercise_form = ExerciseForm(instance=exercise)
    
    template_data['edit_form'] = exercise_form
    
    return render_to_response('edit_exercise.html',
                              template_data,
                              context_instance=RequestContext(request))

@permission_required('exercises.delete_exercise')
def exercise_delete(request, id):
    # Load the exercise
    exercise = get_object_or_404(Exercise, pk=id)
    exercise.delete()
    
    return HttpResponseRedirect('/exercise/overview/')

@permission_required('exercises.change_exercisecategory')
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
            
            # Load the language
            language = get_object_or_404(Language, short_name = translation.get_language())
            language_obj = get_object_or_404(Language, pk=language.id)
            
            # Save the category
            category = category_form.save(commit=False)
            category.language = language_obj
            category.save()
            
            return HttpResponseRedirect('/exercise/overview/')
        else:
            pass
            #logger.debug(category_form.errors)
    else:
        category_form = ExerciseCategoryForm(instance=category)
    
    template_data['category_form'] = category_form
    
    return render_to_response('edit_category.html',
                              template_data,
                              context_instance=RequestContext(request))

@permission_required('exercises.delete_exercisecategory')
def exercise_category_delete(request, id):
    # Load the category
    category = get_object_or_404(ExerciseCategory, pk=id)
    category.delete()
    
    return HttpResponseRedirect('/exercise/overview/')

def exercise_search(request):
    """Search an exercise, return the result as a JSON list
    """
    
    if request.is_ajax():
        q = request.GET.get('term', '')
        
        # Perform the search
        exercises = Exercise.objects.filter(name__icontains = q )[:20]
        results = []
        for exercise in exercises:
            exercise_json = {}
            exercise_json['id'] = exercise.id
            exercise_json['name'] = exercise.name
            exercise_json['value'] = exercise.name
            results.append(exercise_json)
        data = json.dumps(results)
    else:
        data = 'fail'

    # Return the results to the server
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)
