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

from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.forms import ModelForm
from django.forms.models import modelformset_factory
from django.core.context_processors import csrf
from django.contrib.auth.decorators import permission_required, login_required
from django.utils.translation import ugettext as _

from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.forms import AuthenticationForm

from manager.models import TrainingSchedule
from manager.models import Day
from manager.models import Set
from manager.models import Setting

from exercises.models import Exercise
from exercises.models import ExerciseComment
from exercises.models import ExerciseCategory

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
    template_data = {}
    template_data.update(csrf(request))
    
    template_data['form'] = AuthenticationForm()
    
    if request.method == 'POST':
        authentication_form = AuthenticationForm(data=request.POST)
        
        # If the data is valid, log in and redirect
        if authentication_form.is_valid():
            username = authentication_form.cleaned_data['username']
            password = authentication_form.cleaned_data['password']
            
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    django_login(request, user)
                    
                    # Redirect to the start page.
                    return HttpResponseRedirect('/')
                else:
                    # Return a disabled account error message
                    pass
            else:
                # Return an invalid login error message.
                pass

    return render_to_response('login.html', template_data)

def logout(request):
    """Logout the user
    """
    django_logout(request)
    return HttpResponseRedirect('/login')

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
                for setting in exercise.setting_set.filter(set_id = set_obj.id):
                    setting_data.append(str(setting.reps))
                    

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
    workout.user = request.user
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
# Settings functions
# ************************
class SettingForm(ModelForm):
    class Meta:
        model = Setting
        exclude = ('set', 'exercise')

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
                                          exclude = ('set', 'exercise'),
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
                setting_instance.set = set_obj
                setting_instance.exercise = exercise
                setting_instance.save()
            
            return HttpResponseRedirect('/workout/%s/view/' % id)
        else:
            pass
            #logger.debug(setting_form.errors)
    else:
        setting_form = SettingFormSet(queryset=Setting.objects.filter(exercise_id=exercise.id, set_id=set_obj.id))
    template_data['setting_form'] = setting_form
    
    return render_to_response('setting/edit.html', template_data)

@permission_required('manager.change_setting')
def api_edit_set(request):
    """ Allows to edit the order of the sets via an AJAX call
    """
    
    if request.is_ajax():
        if request.GET.get('do') == 'set_order':
            day_id = request.GET.get('day_id')
            new_set_order = request.GET.get('order')
            
            data = new_set_order
            order = 0
            for i in new_set_order.strip(',').split(','):
                set_id = i.split('-')[1]
                order += 1
                
                set_obj = get_object_or_404(Set, pk=set_id, exerciseday=day_id)
                set_obj.order = order
                set_obj.save()
                
                
            return HttpResponse(_('Success'))

@permission_required('manager.change_setting')
def api_edit_setting(request):
    """ Allows to edit the order of the setting inside a set via an AJAX call
    """
    
    if request.is_ajax():
        if request.GET.get('do') == 'set_order':
            new_setting_order = request.GET.get('order')
            
            order = 0
            for i in new_setting_order.strip(',').split(','):
                setting_id = i.split('-')[1]
                order += 1
                
                setting_obj = get_object_or_404(Setting, pk=setting_id)
                setting_obj.order = order
                setting_obj.save()
                
                
            return HttpResponse(_('Success'))


@permission_required('manager.delete_setting')
def delete_setting(request, id, set_id, exercise_id):
    """Deletes all the settings belonging to set_id and exercise_id
    """
    
    # Load the workout
    workout = get_object_or_404(TrainingSchedule, pk=id)
    
    # Delete all settings
    settings = Setting.objects.filter(exercise_id=exercise_id, set_id=set_id)
    settings.delete()
    
    return HttpResponseRedirect('/workout/%s/view/' % id)
