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

from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.forms import ModelForm
from django.forms.models import modelformset_factory
from django.core.context_processors import csrf
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import permission_required, login_required
from django.utils.translation import ugettext as _


from manager.models import TrainingSchedule
from manager.models import Exercise
from manager.models import ExerciseComment
from manager.models import ExerciseCategory
from manager.models import Day
from manager.models import Set
from manager.models import Setting

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4, cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Table
from reportlab.lib import colors

logger = logging.getLogger('workout_manager.custom')

# ************************
# Misc functions
# ************************
@login_required
def index(request):
    """Show the index page, in our case, a list of workouts
    """
    latest_trainings = TrainingSchedule.objects.all().order_by('-creation_date')[:5]
    return render_to_response('index.html', {'latest_workouts_list': latest_trainings})

def login(request):
    """Login the user and redirect it
    """
    pass

def logout(request):
    """Logout the
    """
    logout(request)

# ************************
# Workout functions
# ************************
class WorkoutForm(ModelForm):
    class Meta:
        model = TrainingSchedule

@login_required
def view_workout(request, id):
    """Show the workout with the given ID
    """
    template_data = {}
    
    workout = get_object_or_404(TrainingSchedule, pk=id)
    template_data['workout'] = workout
    
    return render_to_response('workout/view.html', template_data)

@login_required
def pdf_workout(request, id):
    """Generates a PDF with the contents of the given workout
    
    See also
    * http://www.blog.pythonlibrary.org/2010/09/21/reportlab-tables-creating-tables-in-pdfs-with-python/
    * http://www.reportlab.com/apis/reportlab/dev/platypus.html
    """
    
    #Load the workout
    workout = get_object_or_404(TrainingSchedule, pk=id)
    
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=workout.pdf'
    
    # Create the PDF object, using the response object as its "file."
    doc = SimpleDocTemplate(response,
                            pagesize = A4,
                            title = _('Workout'),
                            author = _('Workout Manager'),
                            subject = _('Workout for XYZ'))

    # container for the 'Flowable' objects
    elements = []
    
    styleSheet = getSampleStyleSheet()
    data = []
    
    # Iterate through the Workout
    day_markers = []
    set_markers = []
    exercise_markers = []
    nr_of_weeks = 7
    first_weight_column = 3
    
    
    # Days
    for day in workout.day_set.select_related():
        day_markers.append(len(data))
        
        P = Paragraph('<para align="center"><strong>%s</strong></para>' % day.description,
                      styleSheet["Normal"])
        
        data.append([P])
        data.append([_('Nr.'), _('Exercise'), _('Reps')] + [_('Weight')] * nr_of_weeks)
        
        # Sets
        for set_obj in day.set_set.select_related():
            set_markers.append(len(data))
            
            # Exercises
            for exercise in set_obj.exercises.select_related():
                exercise_markers.append(len(data))
                setting_data = []
                
                
                # Settings
                for setting in exercise.setting_set.filter(sets_id = set_obj.id):
                    setting_data.append(setting.reps)
               
                
                out = set_obj.sets + 'x ' + ', '.join(setting_data)
                data.append([set_obj.order, Paragraph(exercise.name, styleSheet["Normal"]), out] + [''] * nr_of_weeks)
        data.append(['', '', _('Impression')])
    
    # Set general table styles
    table_style = []
    table_style = [('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                   ('BOX', (0,0), (-1,-1), 0.25, colors.black)]
    
    # Set specific styles, e.g. background for title cells
    previous_marker = 0
    for marker in day_markers:
        # Set background colour for headings
        table_style.append(('BACKGROUND', (0, marker), (-1, marker), colors.green))
        table_style.append(('BOX', (0, marker), (-1, marker), 1.25, colors.black))
        
        # Make the headings span the whole width
        table_style.append(('SPAN', (0, marker), (-1, marker)))

    
    table_style.append
    t = Table(data, style = table_style)
    
    # Manually set the width of thecolumns
    for i in range(first_weight_column, nr_of_weeks + first_weight_column):
        t._argW[i] = 1.8 * cm
    
    t._argW[0] = 0.7 * cm
    t._argW[1] = 3.1 * cm
    t._argW[2] = 2.5 * cm

    elements.append(t)
    #t=Table(data,style=[('GRID',(1,1),(-2,-2),1,colors.green),
                        #('BOX',(0,0),(1,-1),2,colors.red),
                        #('LINEABOVE',(1,2),(-2,2),1,colors.blue),
                        #('LINEBEFORE',(2,1),(2,-2),1,colors.pink),
                        #('BACKGROUND', (0, 0), (0, 1), colors.pink),
                        #('BACKGROUND', (1, 1), (1, 2), colors.lavender),
                        #('BACKGROUND', (2, 2), (2, 3), colors.orange),
                        #('BOX',(0,0),(-1,-1),2,colors.black),
                        #('GRID',(0,0),(-1,-1),0.5,colors.black),
                        #('VALIGN',(3,0),(3,0),'BOTTOM'),
                        #('BACKGROUND',(3,0),(3,0),colors.limegreen),
                        #('BACKGROUND',(3,1),(3,1),colors.khaki),
                        #('ALIGN',(3,1),(3,1),'CENTER'),
                        #('BACKGROUND',(3,2),(3,2),colors.beige),
                        #('ALIGN',(3,2),(3,2),'LEFT'),
    #])
    #t._argW[3]=1.5*cm
    
    
    # write the document and send the response to the browser
    doc.build(elements)

    return response

@permission_required('manager.change_trainingschedule')
def add(request):
    """Add a new workout and redirect to its page
    """
    workout = TrainingSchedule()
    workout.save()
    
    return HttpResponseRedirect('/workout/%s/view/' % workout.id)

@permission_required('manager.delete_trainingschedule')
def delete_workout(request, id):
    """Deletes the workout with ID id
    """
    
    # Load the workout
    workout = get_object_or_404(TrainingSchedule, pk=id)
    workout.delete()
    
    return HttpResponseRedirect('/')


# ************************
# Day functions
# ************************
class DayForm(ModelForm):
    class Meta:
        model = Day
        exclude=('training',)

@permission_required('manager.change_day')
def edit_day(request, id, day_id=None):
    """Edits/creates a day
    """
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
        
        # If the data is valid, save and redirect
        if day_form.is_valid():
            day = day_form.save(commit=False)
            day.training = workout
            day.save()
            
            return HttpResponseRedirect('/workout/%s/view/' % id)
    else:
        day_form = DayForm(instance=day)
    template_data['day_form'] = day_form
    
    return render_to_response('day/edit.html', template_data)

@permission_required('manager.delete_day')
def delete_day(request, id, day_id):
    """Deletes the day with ID day_id belonging to workout with ID id
    """
    
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

@permission_required('manager.change_set')
def edit_set(request, id, day_id, set_id=None):
    """ Edits/creates a set
    """
    
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
        
        # If the data is valid, save and redirect
        if set_form.is_valid():
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

@permission_required('manager.delete_set')
def delete_set(request, id, day_id, set_id):
    """ Deletes the given set
    """
    
    # Load the set
    set_obj = get_object_or_404(Set, pk=set_id)
    set_obj.delete()
    
    return HttpResponseRedirect('/workout/%s/view/' % id)

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
    return render_to_response('exercise/view.html', template_data)

@permission_required('manager.change_exercise')
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
    
    return render_to_response('exercise/edit.html', template_data)

@permission_required('manager.delete_exercise')
def exercise_delete(request, id):
    # Load the exercise
    exercise = get_object_or_404(Exercise, pk=id)
    exercise.delete()
    
    return HttpResponseRedirect('/exercise/overview/')

@permission_required('manager.change_exercisecategory')
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

@permission_required('manager.delete_exercisecategory')
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


# ************************
# Settings functions
# ************************
class SettingForm(ModelForm):
    class Meta:
        model = Setting
        exclude = ('sets', 'exercises')

@permission_required('manager.change_setting')
def edit_setting(request, id, set_id, exercise_id, setting_id=None):
    template_data = {}
    template_data.update(csrf(request))
    
    # Load workout
    workout = get_object_or_404(TrainingSchedule, pk=id)
    template_data['workout'] = workout
    
    # Load set and the FormSet
    set_obj = get_object_or_404(Set, pk=set_id)
    template_data['set'] = set_obj
    
    SettingFormSet = modelformset_factory(Setting,
                                          exclude = ('sets', 'exercises'),
                                          max_num = int(set_obj.sets),
                                          extra = int(set_obj.sets))
    
    # Load exercise
    exercise = get_object_or_404(Exercise, pk=exercise_id)
    template_data['exercise'] = exercise
    
    
    # Load setting
    if not setting_id:
        setting = Setting()
    else:
        setting = get_object_or_404(Setting, pk=setting_id)
    template_data['setting'] = setting
    
    # Process request
    if request.method == 'POST':
        
        # Process the FormSet, setting the set and the exercise
        setting_form = SettingFormSet(request.POST)
        if setting_form.is_valid():
            instances = setting_form.save(commit=False)
            for setting_instance in instances:
                setting_instance.sets = set_obj
                setting_instance.exercises = exercise
                setting_instance.save()
            
            return HttpResponseRedirect('/workout/%s/view/' % id)
    else:
        setting_form = SettingFormSet(queryset=Setting.objects.filter(exercises_id=exercise.id, sets_id=set_obj.id))
    template_data['setting_form'] = setting_form
    
    return render_to_response('setting/edit.html', template_data)

@permission_required('manager.delete_setting')
def delete_setting(request, id, set_id, exercise_id):
    """Deletes all the settings belonging to set_id and exercise_id
    """
    
    # Load the workout
    workout = get_object_or_404(TrainingSchedule, pk=id)
    
    # Delete all settings
    settings = Setting.objects.filter(exercises_id=exercise_id, sets_id=set_id)
    settings.delete()
    
    return HttpResponseRedirect('/workout/%s/view/' % id)

