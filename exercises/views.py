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
import json

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.forms import ModelForm
from django.forms import Textarea
from django.forms import ModelChoiceField
from django.core.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import permission_required
from django.utils.translation import ugettext as _
from django.utils import translation

from django.views.generic import DeleteView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic.edit import ModelFormMixin

from manager.utils import load_language

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
    
    return HttpResponseRedirect(reverse('exercises.views.exercise_view', kwargs= {'id': exercise_id}))
    
    

# ************************
# Exercise functions
# ************************
class ExerciseCommentForm(ModelForm):
    class Meta:
        model = ExerciseComment
        exclude=('exercise',)



class ExerciseCategoryForm(ModelForm):
    class Meta:
        model = ExerciseCategory
        exclude=('language',)
        

def exercise_overview(request):
    """Overview with all exercises
    """
    language = load_language()
    
    template_data = {}
    template_data.update(csrf(request))
    
    template_data['categories'] = ExerciseCategory.objects.filter(language = language.id)
    template_data['active_tab'] = 'exercises'
    
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
    template_data['active_tab'] = 'exercises'
    
    #
    # We can create and edit comments from this page, so look for Posts
    template_data.update(csrf(request))
    
    # Create the backgrounds that show what muscles the exercise works on
    backgrounds_back = []
    backgrounds_front = []
    
    for muscle in exercise.muscles.all():
        if muscle.is_front:
            backgrounds_front.append('images/muscles/main/muscle-%s.svg' % muscle.id)
        else:
            backgrounds_back.append('images/muscles/main/muscle-%s.svg' % muscle.id)
        
    # Append the "main" background, with the silhouette of the human body
    # This has to happen as the last step, so it is rendered behind the muscles.
    if backgrounds_front: 
        backgrounds_front.append('images/muscles/muscular_system_front.svg')
  
    if backgrounds_back:
        backgrounds_back.append('images/muscles/muscular_system_back.svg')
    
    template_data['muscle_backgrounds_front'] = backgrounds_front
    template_data['muscle_backgrounds_back'] = backgrounds_back
    
    # Only users with the appropriate permissions can work with comments
    if request.user.has_perm('exercises.add_exercisecomment'):
        
        # Adding a new comment
        if request.method == 'POST' and not comment_id:
            comment_form = ExerciseCommentForm(request.POST)
            comment_form.exercise = exercise
            
            # If the data is valid, save and redirect
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.exercise = exercise
                new_comment.save()
                return HttpResponseRedirect(reverse('exercises.views.exercise_view', kwargs= {'id': id}))
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
                    return HttpResponseRedirect(reverse('exercises.views.exercise_view', kwargs= {'id': id}))
            
        
        template_data['comment_form'] = comment_form
    
    # Render
    return render_to_response('view.html',
                              template_data,
                              context_instance=RequestContext(request))


class YamlFormMixin(ModelFormMixin):
    template_name = 'form.html'
    
    active_tab = ''
    form_fields = []
    active_tab = ''
    select_lists = []
    static_files = []
    custom_js = ''
    
    def get_context_data(self, **kwargs):
        '''
        Set necessary template data to correctly render the form
        '''
        
        # Call the base implementation first to get a context
        context = super(YamlFormMixin, self).get_context_data(**kwargs)
        
        # CSRF token
        context.update(csrf(self.request))
        
        # Active tab, on top navigation
        context['active_tab'] = self.active_tab
    
        # Form fields are listed here, otherwise the order from the model is
        # used. The list comprehension is to avoid weird problems with django's
        # template when accessing the fields with "form.fieldname"
        context['form_fields'] = [kwargs['form'][i] for i in self.form_fields]
        
        # Drop down lists get a special CSS class, there doesn't seem to be
        # another way of detecting them
        context['select_lists'] = self.select_lists
    
        # List of additional JS static files, will be passed to {% static %}
        context['static_files'] = self.static_files
       
        # Custom JS code on form (autocompleter, editor, etc.)
        context['custom_js'] = self.custom_js
        
        return context

class ExercisesUpdateView(YamlFormMixin, UpdateView):
    active_tab = 'exercises'
    
class ExercisesCreateView(YamlFormMixin, CreateView):
    active_tab = 'exercises'

class ExercisesDeleteView(YamlFormMixin, DeleteView):
    active_tab = 'exercises'
    #template_name = ''
    success_url = reverse('exercises.views.exercise_overview')


class ExerciseUpdateView(ExercisesUpdateView):
    model = Exercise
    
    form_fields = ['name',
                   'category',
                   'muscles',
                   'description']
    
    select_lists = ['category']
    static_files = ['js/tinymce/tiny_mce.js', 
                    'js/workout-manager.js']
        
    custom_js = 'init_tinymce();'
        
class ExerciseAddView(ExercisesCreateView):
    model = Exercise
    
    form_fields = ['name',
                   'category',
                   'muscles',
                   'description']
    
    select_lists = ['category']
    static_files = ['js/tinymce/tiny_mce.js', 
                    'js/workout-manager.js']
        
    custom_js = 'init_tinymce();'

class ExerciseDeleteView(ExercisesDeleteView):
    model = Exercise

    

@permission_required('exercises.change_exercise')
def exercise_edit(request, id=None):
    
    # Define the exercise form here because only at this point during the request have we access to
    # the currently used language. In other places Django defaults to 'en-us'. Since we only use it
    # here, it's OK 
    class ExerciseForm(ModelForm):
        language = load_language()
        category = ModelChoiceField(queryset=ExerciseCategory.objects.filter(language = language.id))
            
        class Meta:
            model = Exercise
    
    template_data = {}
    template_data.update(csrf(request))
    template_data['active_tab'] = 'exercises'
    
    # If the object is new, we will receice a 'None' (string) as the ID
    # from the template, so we check for it (ValueError) and for an actual
    # None (TypeError)
    try:
        int(id)
        exercise = get_object_or_404(Exercise, pk=id)
    except ValueError, TypeError:
        exercise = Exercise()
    
    template_data['exercise'] = exercise
    
    if request.method == 'POST':
        exercise_form = ExerciseForm(request.POST, instance=exercise)
        
        # If the data is valid, save and redirect
        if exercise_form.is_valid():
            exercise = exercise_form.save()
            id = exercise.id
            return HttpResponseRedirect(reverse('exercises.views.exercise_view', kwargs= {'id': id}))
    else:
        exercise_form = ExerciseForm(instance=exercise)
    
    #template_data['edit_form'] = exercise_form
    
    #
    # Pass settings to the form template
    #
    if exercise.id:
        template_data['title'] = _('Edit %(exercisename)s') % {'exercisename': exercise.name}
    else:
        template_data['title'] = _('New exercise')
    
    template_data['form_action'] = reverse('exercises.views.exercise_edit',
                                           kwargs = {'id': exercise.id})
    
    # Form fields are listed here, otherwise the order from the model is
    # used. The list comprehension is to avoid weird problems with django's
    # template when accessing the fields with "form.fieldname"
    template_data['form_fields'] = [exercise_form[i] for i in [
                                        'name',
                                        'category',
                                        'muscles',
                                        'description'
                                        ]
                                    ]
    
    # Drop down lists get a special CSS class
    template_data['select_lists'] = ['category']
    
    template_data['static_files'] = ['js/tinymce/tiny_mce.js', 
                                     'js/workout-manager.js']
    
    # Custom JS code on form (autocompleter, editor, etc.)
    template_data['custom_js'] = 'init_tinymce();'
    
    return render_to_response('form.html',
                              template_data,
                              context_instance=RequestContext(request))

@permission_required('exercises.delete_exercise')
def exercise_delete(request, id):
    # Load the exercise
    exercise = get_object_or_404(Exercise, pk=id)
    exercise.delete()
    
    return HttpResponseRedirect(reverse('exercises.views.exercise_overview'))

@permission_required('exercises.change_exercisecategory')
def exercise_category_edit(request, id):
    template_data = {}
    template_data.update(csrf(request))
    template_data['active_tab'] = 'exercises'
    
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
            language = load_language()
            
            # Save the category
            category = category_form.save(commit=False)
            category.language = language
            category.save()
            
            return HttpResponseRedirect(reverse('exercises.views.exercise_overview'))
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
    
    return HttpResponseRedirect(reverse('exercises.views.exercise_overview'))

def exercise_search(request):
    """Search an exercise, return the result as a JSON list
    """
    
    # Perform the search
    q = request.GET.get('term', '')
    user_language = load_language()
    exercises = Exercise.objects.filter(name__icontains = q, category__language_id = user_language )
    
    # AJAX-request, this comes from the autocompleter. Create a list and send it back as JSON
    if request.is_ajax():
        
        results = []
        for exercise in exercises:
            exercise_json = {}
            exercise_json['id'] = exercise.id
            exercise_json['name'] = exercise.name
            exercise_json['value'] = exercise.name
            results.append(exercise_json)
        data = json.dumps(results)
        
        # Return the results to the server
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)
    
    # Usual search (perhaps JS disabled), present the results as normal HTML page
    else:
        template_data = {}
        template_data.update(csrf(request))
        template_data['exercises'] = exercises
        template_data['search_term'] = q
        return render_to_response('exercise_search.html',
                                  template_data,
                                  context_instance=RequestContext(request))
