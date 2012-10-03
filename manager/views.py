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
import uuid
import datetime

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.forms import ModelForm
from django.forms.models import modelformset_factory
from django.forms import SelectMultiple
from django.core.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User as Django_User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm

from workout_manager import get_version

from manager.models import DaysOfWeek
from manager.models import TrainingSchedule
from manager.models import Day
from manager.models import Set
from manager.models import Setting
from manager.models import UserProfile

from exercises.models import Exercise

from nutrition.models import NutritionPlan

from weight.models import WeightEntry

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4, cm, landscape, portrait
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table
from reportlab.lib import colors

logger = logging.getLogger('workout_manager.custom')

# ************************
# Misc functions
# ************************

@login_required
def index(request):
    """Show the index page, in our case, the last workout and nutritional plan
    and the current weight
    """
    
    template_data = {}
    template_data['active_tab'] = 'user'
    
    # Load the last workout, if one exists
    try:
        current_workout = TrainingSchedule.objects.filter(user=request.user).latest('creation_date')
        template_data['current_workout'] = current_workout
    except ObjectDoesNotExist:
        current_workout = False
    template_data['current_workout'] = current_workout
    
    # Load the last nutritional plan, if one exists
    try:
        plan = NutritionPlan.objects.filter(user = request.user).latest('creation_date')
    except ObjectDoesNotExist:
        plan = False
    template_data['plan'] = plan
    
    # Load the last logged weight entry, if one exists
    try:
        weight  = WeightEntry.objects.filter(user = request.user).latest('creation_date')
    except ObjectDoesNotExist:
        weight = False
    template_data['weight'] = weight
    
    
    if current_workout:
        
        # Format a bit the days so it doesn't have to be done in the template
        week_day_result = []
        for week in DaysOfWeek.objects.all():
            day_has_workout = False
            for day in current_workout.day_set.select_related():
                for day_of_week in day.day.select_related():
                    if day_of_week.id == week.id:
                        day_has_workout = True
                        week_day_result.append((_(week.day_of_week), day.description, True))
                        break
                
                
            if not day_has_workout:
                week_day_result.append((_(week.day_of_week), _('Rest day'), False))
        
        template_data['weekdays'] = week_day_result
        
        
    if plan:
        
        # Load the nutritional info
        template_data['nutritional_info'] = plan.get_nutritional_values()
    
    
    return render_to_response('index.html',
                              template_data,
                              context_instance=RequestContext(request))
# ************************
# User functions
# ************************

class UserPreferencesForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user',)

def login(request):
    """Login the user and redirect it
    """
    
    template_data = {}
    template_data.update(csrf(request))
    template_data['active_tab'] = 'user'
    
    template_data['form'] = AuthenticationForm()
    
    # Read out where the user came from so we can redirect him after logging in
    redirect_target = request.GET.get('next', '')
    
    if request.method == 'POST':
        redirect_target = request.POST.get('redirect_target')
        authentication_form = AuthenticationForm(data=request.POST)
        template_data['form'] = authentication_form
        
        # Default redirection target is the index page
        if not redirect_target:
            redirect_target = reverse('manager.views.index')
        
        # If the data is valid, log in and redirect
        if authentication_form.is_valid():
            username = authentication_form.cleaned_data['username']
            password = authentication_form.cleaned_data['password']
            
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    django_login(request, user)
                    
                    # Redirect to where the user came from
                    return HttpResponseRedirect(redirect_target)
                else:
                    # Return a disabled account error message
                    pass
            else:
                # Return an invalid login error message.
                pass
    
    template_data['redirect_target'] = redirect_target
    
    return render_to_response('login.html',
                              template_data,
                              context_instance=RequestContext(request))

def change_password(request):
    """Change the user's password
    """
    
    template_data = {}
    template_data.update(csrf(request))
    template_data['active_tab'] = 'user'
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, data=request.POST)
        
        # If the data is valid, change the password redirect
        if form.is_valid():
            request.user.set_password('new password')
            request.user.save()
        
            return HttpResponseRedirect(reverse('manager.views.index'))
    else:
        form = PasswordChangeForm(request.user)

    template_data['form'] = form
    
    return render_to_response('user/change_password.html',
                              template_data,
                              context_instance=RequestContext(request))


def logout(request):
    """Logout the user
    """
    django_logout(request)
    return HttpResponseRedirect(reverse('manager.views.login'))


def registration(request):
    """A form to allow for registration of new users
    """
    template_data = {}
    template_data.update(csrf(request))
    template_data['active_tab'] = 'user'
    
    if request.method == 'POST':
        form = UserCreationForm(data=request.POST)
        
        # If the data is valid, log in and redirect
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = Django_User.objects.create_user(username,
                                                   '',
                                                   password)
            user.save()
            user = authenticate(username=username, password=password)
            django_login(request, user)
            return HttpResponseRedirect(reverse('manager.views.index'))
    else:
        form = UserCreationForm()

    template_data['form'] = form
    
    return render_to_response('user/registration.html',
                              template_data,
                              context_instance=RequestContext(request))

def preferences(request):
    """An overview of all user preferences
    """
    template_data = {}
    template_data.update(csrf(request))
    template_data['active_tab'] = 'user'
    
    if request.method == 'POST':
    
        form = UserPreferencesForm(data=request.POST, instance=request.user.get_profile())
        form.user = request.user
        
        # Save the data if it validates
        if form.is_valid():
            form.save()
    else:
        form = UserPreferencesForm(instance=request.user.get_profile())
   
    template_data['form'] = form
   
    return render_to_response('user/preferences.html',
                              template_data,
                              context_instance=RequestContext(request))


# ************************
# Workout functions
# ************************
class WorkoutForm(ModelForm):
    class Meta:
        model = TrainingSchedule
        exclude = ('user',)


@login_required
def overview(request):
    """An overview of all the user's workouts
    """
    
    template_data = {}
    template_data['active_tab'] = 'workout'
    
    latest_trainings = TrainingSchedule.objects.filter(user=request.user)
    template_data['workouts'] = latest_trainings
    
    return render_to_response('workout/overview.html',
                              template_data,
                              context_instance=RequestContext(request))

@login_required
def view_workout(request, id):
    """Show the workout with the given ID
    """
    template_data = {}
    template_data['active_tab'] = 'workout'
    
    workout = get_object_or_404(TrainingSchedule, pk=id, user=request.user)
    template_data['workout'] = workout
    
    
    # TODO: this can't be performant, see if it makes problems
    # Create the backgrounds that show what muscles the workout will work on
    backgrounds_front = []
    backgrounds_back = []
    is_front = True
    for day in workout.day_set.select_related():
        for set in day.set_set.select_related():
            for exercise in set.exercises.select_related():
                for muscle in exercise.muscles.all():
                    
                    if muscle.is_front:
                        backgrounds_front.append('images/muscles/main/muscle-%s.svg' % muscle.id)
                    else:
                        backgrounds_back.append('images/muscles/main/muscle-%s.svg' % muscle.id)
    
    # Append the correct "main" background, with the silhouette of the human body
    backgrounds_front.append('images/muscles/muscular_system_front.svg')
    backgrounds_back.append('images/muscles/muscular_system_back.svg')
    
    template_data['muscle_backgrounds_front'] = backgrounds_front
    template_data['muscle_backgrounds_back'] = backgrounds_back
    
    
    return render_to_response('workout/view.html', 
                              template_data,
                              context_instance=RequestContext(request))

@login_required
def pdf_workout(request, id):
    """Generates a PDF with the contents of the given workout
    
    See also
    * http://www.blog.pythonlibrary.org/2010/09/21/reportlab-tables-creating-tables-in-pdfs-with-python/
    * http://www.reportlab.com/apis/reportlab/dev/platypus.html
    """
    
    #Load the workout
    workout = get_object_or_404(TrainingSchedule, pk=id, user=request.user)
    
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=%s.pdf' % _('Workout')
    
    # Create the PDF object, using the response object as its "file."
    doc = SimpleDocTemplate(response,
                            pagesize = A4,
                            #pagesize = landscape(A4),
                            leftMargin = cm,
                            rightMargin = cm,
                            topMargin = 0.5 * cm,
                            bottomMargin = 0.5 * cm,
                            title = _('Workout'),
                            author = _('Workout Manager'),
                            subject = _('Workout for %s') % request.user.username)

    # container for the 'Flowable' objects
    elements = []
    
    # stylesheet
    styleSheet = getSampleStyleSheet()
    
    style = ParagraphStyle(
        name = 'Normal',
        #fontName='Helvetica-Bold',
        fontSize = 8,
        )
    
    # Set the widths and heights of rows and columns
    # TODO: if the height is set here, there is no automatic scaling when e.g.
    #       the exercise names are too long. This should be fixed, till then set
    #       to None for automatic scaling
    #rowheights = (13)
    colwidths = None
    rowheights = None
    
    
    # table data, here we will put the workout info
    data = []
    
    
    # Init several counters and markers, this will be used after the iteration to
    # set different borders and colours
    day_markers = []
    exercise_markers = {}
    row_count = 1
    group_exercise_marker = {}
    group_day_marker = {}
    
    # Set the number of weeks for this workout
    # (sets number of columns for the weight/date log)
    nr_of_weeks = 7
    
    # Set the first column of the weight log, depends on design
    first_weight_column = 3
    
    # Background color for days
    # Reportlab doesn't use the HTML hexadecimal format, but has a range of
    # 0 till 1, so we have to convert here.
    header_colour = colors.Color(int('73', 16) / 255.0,
                                 int('8a', 16) / 255.0,
                                 int('5f', 16) / 255.0)
    
    
    #
    # Iterate through the Workout
    #
    
    # Days
    for day in workout.day_set.select_related():
        set_count = 1
        day_markers.append(len(data))
        group_day_marker[day.id] = {'start': row_count, 'end': row_count}
        
        if not exercise_markers.get(day.id):
            exercise_markers[day.id] = []
        
        days_of_week = [_(day_of_week.day_of_week) for day_of_week in day.day.select_related()]
        
        P = Paragraph('<para align="center">%(days)s: <strong>%(description)s</strong></para>' %
                                        {'days' : ', '.join(days_of_week),
                                         'description': day.description},
                      styleSheet["Normal"])
        
        data.append([P])
        
        # Note: the _('Date') will be on the 3rd cell, but since we make a span
        #       over 3 cells, the value has to be on the 1st one
        data.append([_('Date') + ' ', '', ''] + [''] * nr_of_weeks)
        data.append([_('Nr.'), _('Exercise'), _('Reps')] + [_('Weight')] * nr_of_weeks)
        row_count += 3
        
        # Sets
        for set_obj in day.set_set.select_related():
            group_exercise_marker[set_obj.id] = {'start': row_count, 'end': row_count}
            
            # Exercises
            for exercise in set_obj.exercises.select_related():
                
                group_exercise_marker[set_obj.id]['end'] = row_count
                
                exercise_markers[day.id].append(row_count)
                setting_data = []
                
                
                # Settings
                for setting in exercise.setting_set.filter(set_id = set_obj.id):
                    if setting.reps == 99:
                        repetitions = '∞'
                    else:
                        repetitions = str(setting.reps)
                    setting_data.append(repetitions)
                    

                # If there are more than 1 settings, don't output the repetitions
                # e.g. "4 x 8 8 10 10" is shown only as "8 8 10 10", after all
                # those 4 sets are not done four times!
                if len(setting_data) == 0:
                    out = '' # nothing set
                    
                elif len(setting_data) == 1:
                    out = str(set_obj.sets) + ' × ' + setting_data[0]
                    
                elif len(setting_data) > 1:
                    out = ', '.join(setting_data)
                
                data.append([set_count, Paragraph(exercise.name, style), out] + [''] * nr_of_weeks)
                row_count += 1
            set_count += 1
        
        # Note: as above with _('Date'), the _('Impression') has to be here on
        #       the 1st cell so it is shown after adding a span
        #data.append([_('Impression'), '', ''])
        #row_count += 1
        
        set_count += 1
        group_day_marker[day.id]['end'] =  row_count
        
        #data.append([''])
        #row_count += 1
    
    # Set general table styles
    table_style = [
                    ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                    ('BOX', (0,0), (-1,-1), 1.25, colors.black),
                    ('FONT', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('VALIGN',(0, 0),(-1, -1),'MIDDLE'),
                    
                    #Note: a padding of 3 seems to be the default
                    ('LEFTPADDING', (0, 0), (-1, -1), 2), 
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                   ]
    
    # Set specific styles, e.g. background for title cells
    previous_marker = 0
    for marker in day_markers:
        # Set background colour for headings
        table_style.append(('BACKGROUND', (0, marker), (-1, marker), header_colour))
        table_style.append(('BOX', (0, marker), (-1, marker), 1.25, colors.black))
        table_style.append(('BOX', (0, marker), (-1, marker + 2), 1.25, colors.black))
        
        # Make the headings span the whole width
        table_style.append(('SPAN', (0, marker), (-1, marker)))
        
        # Make the date span 3 cells and align it to the right
        table_style.append(('ALIGN', (0, marker + 1), (2, marker +1), 'RIGHT'))
        table_style.append(('SPAN', (0, marker +1), (2, marker + 1)))
        

    # Combine the cells for exercises on the same set
    for marker in group_exercise_marker:
        start_marker = group_exercise_marker[marker]['start'] -1
        end_marker = group_exercise_marker[marker]['end'] -1
        
        table_style.append(('VALIGN',(0, start_marker),(0, end_marker),'MIDDLE'))
        table_style.append(('SPAN', (0, start_marker), (0, end_marker)))
    
    # Set an alternating background colour for rows
    for i in exercise_markers:
        counter = 1
        for j in exercise_markers[i]:
            if not j % 2:
                table_style.append(('BACKGROUND', (1, j -1), (-1, j -1), colors.lavender))
            counter += 1
    
    
    # Make the 'impression' span 3 cells and align it to the right
    for marker in group_day_marker:
        start_marker = group_day_marker[marker]['start']
        end_marker = group_day_marker[marker]['end']
        
        #table_style.append(('ALIGN', (0, end_marker - 2), (2, end_marker - 2), 'RIGHT'))
    
    #  TODO: this only makes sense if the "empty" cells can be made less high
    #       than the others, otherwise it takes too much space!
    # Draw borders and grids around the daystable_style.append(('SPAN', (0, end_marker - 2), (2, end_marker - 2)))
    #    
    #    table_style.append(('INNERGRID', (0, start_marker), (-1,end_marker -2 ), 0.25, colors.black))
    #    table_style.append(('BOX', (0, start_marker), (-1, end_marker -2), 1.25, colors.black))
        
    
    # Set the table data
    t = Table(data, colwidths, rowheights, style = table_style)
    
    # Manually set the width of the columns
    for i in range(first_weight_column, nr_of_weeks + first_weight_column):
        t._argW[i] = 1.8 * cm # Columns for entering the log
    
    t._argW[0] = 0.6 * cm # Exercise numbering
    t._argW[1] = 3.5 * cm # Name of exercise
    t._argW[2] = 1.9 * cm # Repetitions

    #
    # Add all elements to the document
    # 
    
    # Set the title (if available)
    if workout.comment:
        P = Paragraph('<para align="center"><strong>%(description)s</strong></para>' %
                                            {'description' : workout.comment},
                          styleSheet["Normal"])
        elements.append(P)
    
        # Filler
        P = Paragraph('<para> </para>', styleSheet["Normal"])
        elements.append(P)

    # Append the table
    elements.append(t)
    
    # Footer, add filler paragraph
    P = Paragraph('<para> </para>', styleSheet["Normal"])
    elements.append(P)
    
    # Print date and info
    P = Paragraph('<para align="left">%(date)s - %(created)s v%(version)s</para>' %
                    {'date' : _("Created on the <b>%s</b>") % workout.creation_date.strftime("%d.%m.%Y"),
                     'created' : _("Workout Manager"),
                     'version': get_version()},
                  styleSheet["Normal"])
    elements.append(P)
    

    # write the document and send the response to the browser
    doc.build(elements)

    return response

@login_required
def add(request):
    """Add a new workout and redirect to its page
    """
    workout = TrainingSchedule()
    workout.user = request.user
    workout.save()
    
    return HttpResponseRedirect(reverse('manager.views.view_workout', kwargs= {'id': workout.id}))

@login_required
def delete_workout(request, id):
    """Deletes the workout with ID id
    """
    
    # Load the workout
    workout = get_object_or_404(TrainingSchedule, pk=id, user=request.user)
    workout.delete()
    
    return HttpResponseRedirect(reverse('manager.views.index'))


def edit_workout(request, id):
    """Edits a workout
    """
    template_data = {}
    template_data.update(csrf(request))
    template_data['active_tab'] = 'workout'
    
    # Load workout
    workout = get_object_or_404(TrainingSchedule, pk=id, user=request.user)
    template_data['workout'] = workout
    
    # Process request
    if request.method == 'POST':
        form = WorkoutForm(request.POST, instance=workout)
        form.user = request.user
        
        # If the data is valid, save and redirect
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('manager.views.view_workout', kwargs= {'id': id}))
    else:
        form = WorkoutForm(instance=workout)
    
    template_data['form'] = form
    
    return render_to_response('workout/edit.html',
                              template_data,
                              context_instance=RequestContext(request))



@login_required
def api_user_preferences(request):
    """ Allows the user to edit its preferences via AJAX calls
    """
    
    if request.is_ajax():
    
        # Show comments on workout view
        if request.GET.get('do') == 'set_show-comments':
            new_value = int(request.GET.get('show'))
            
            profile = request.user.get_profile()
            profile.show_comments = new_value
            profile.save()
                
            return HttpResponse(_('Success'))
        
        # Show ingredients in english
        elif request.GET.get('do') == 'set_english-ingredients':
            new_value = int(request.GET.get('show'))
            
            profile = request.user.get_profile()
            profile.show_english_ingredients = new_value
            profile.save()
                
            return HttpResponse(_('Success'))


# ************************
# Day functions
# ************************
class DayForm(ModelForm):
    class Meta:
        model = Day
        exclude=('training',)
        

@login_required
def edit_day(request, id, day_id=None):
    """Edits/creates a day
    """
    template_data = {}
    template_data.update(csrf(request))
    template_data['active_tab'] = 'workout'
    
    # Load workout
    workout = get_object_or_404(TrainingSchedule, pk=id, user=request.user)
    template_data['workout'] = workout
    
    # Calculate the used days
    used_days = []
    for day in workout.day_set.all():
        for weekday in day.day.all():
            try:
                if day.id != int(day_id):
                    used_days.append(weekday.id)
            # We didnt' get a valid integer as id (perhaps because this is a new day)
            except ValueError:
                pass
    used_days.sort()

    
    
    
    # Load day
    # We check for string 'None' because we might get this from the template
    if not day_id or day_id == 'None':
        day = Day()
    else:
        day = get_object_or_404(Day, pk=day_id)
        
        # Check that the day belongs to the workout
        if day.training.id != workout.id:  
            return HttpResponseForbidden()
    template_data['day'] = day
    
    
    # Process request
    if request.method == 'POST':
        day_form = DayForm(request.POST, instance=day)
        
        # If the data is valid, save and redirect
        if day_form.is_valid():
            day = day_form.save(commit=False)
            day.training = workout
            day.save()
            
            day_form.save_m2m()
            
            return HttpResponseRedirect(reverse('manager.views.view_workout', kwargs= {'id': id}))
    else:
        day_form = DayForm(instance=day)
    
    # Set here the query set to filter out used days of the week
    # (used in the sense that other training days on the same workout already have them set)
    day_form.fields['day'].queryset=DaysOfWeek.objects.exclude(id__in=used_days)
        
    template_data['day_form'] = day_form
    
    return render_to_response('day/edit.html',
                              template_data,
                              context_instance=RequestContext(request))

@login_required
def delete_day(request, id, day_id):
    """Deletes the day with ID day_id belonging to workout with ID id
    """
    
    # Load the day
    day = get_object_or_404(Day, pk=day_id)
    
    # Check if the user is the owner of the object
    if day.training.user == request.user:
        day.delete()
        return HttpResponseRedirect(reverse('manager.views.view_workout', kwargs= {'id': id}))
    else:
        return HttpResponseForbidden()


@login_required
def view_day(request, id):
    """Renders a day as shown in the workout overview.
    
    This function is to be used with AJAX calls.
    """
    template_data = {}
    
    # Load day and check if its workout belongs to the user
    day = get_object_or_404(Day, pk=id)
    if day.training.user != request.user:
        return HttpResponseForbidden()
    
    template_data['day'] = day
    
    return render_to_response('day/view.html',
                              template_data,
                              context_instance=RequestContext(request))

# ************************
# Set functions
# ************************
class SetForm(ModelForm):
    class Meta:
        model = Set
        exclude = ('exerciseday', 'order',)

@login_required
def edit_set(request, id, day_id, set_id=None):
    """ Edits/creates a set
    """
    
    template_data = {}
    template_data.update(csrf(request))
    template_data['active_tab'] = 'workout'
    
    # Load workout
    workout = get_object_or_404(TrainingSchedule, pk=id, user=request.user)
    template_data['workout'] = workout
    
    # Load day
    day = get_object_or_404(Day, pk=day_id)
    template_data['day'] = day
    
    # Load set
    if not set_id or set_id == 'None':
        workout_set = Set()
    else:
        workout_set = get_object_or_404(Set, pk=set_id)
        
        # Check if all objects belong to the workout
        if workout_set.exerciseday.id != day.id:  
            return HttpResponseForbidden()
    
    template_data['set'] = workout_set
    
    # Check if all objects belong to the workout
    if day.training.id != workout.id:
        return HttpResponseForbidden()
    
    
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
            
            return HttpResponseRedirect(reverse('manager.views.view_workout', kwargs= {'id': id}))
    else:
        set_form = SetForm(instance=workout_set)
    template_data['set_form'] = set_form
    
    return render_to_response('set/edit.html',
                              template_data,
                              context_instance=RequestContext(request))

@login_required
def delete_set(request, id, day_id, set_id):
    """ Deletes the given set
    """
    
    # Load the set
    set_obj = get_object_or_404(Set, pk=set_id)
    
    # Check if the user is the owner of the object
    if set_obj.exerciseday.training.user == request.user:
        set_obj.delete()
        return HttpResponseRedirect(reverse('manager.views.view_workout', kwargs= {'id': id}))
    else:
        return HttpResponseForbidden()
    
@login_required
def api_edit_set(request):
    """ Allows to edit the order of the sets via an AJAX call
    """
    
    if request.is_ajax():
        
        # Set the order of the reps
        if request.GET.get('do') == 'set_order':
            day_id = request.GET.get('day_id')
            new_set_order = request.GET.get('order')
            
            data = new_set_order
            order = 0
            for i in new_set_order.strip(',').split(','):
                set_id = i.split('-')[1]
                order += 1
                
                set_obj = get_object_or_404(Set, pk=set_id, exerciseday=day_id)
                
                # Check if the user is the owner of the object
                if set_obj.exerciseday.training.user == request.user:
                    set_obj.order = order
                    set_obj.save()
                else:
                    return HttpResponseForbidden()
                 
                
            return HttpResponse(_('Success'))
        
        # This part is responsible for the in-place editing of the sets and settings
        if request.GET.get('do') == 'edit_set':
            template_data = {}
            template_data.update(csrf(request))
            
            # Load the objects
            set_id = request.GET.get('set')
            workout_set = get_object_or_404(Set, pk=set_id)
            template_data['set'] = workout_set
            
            exercise_id = request.GET.get('exercise')
            exercise = get_object_or_404(Exercise, pk=exercise_id)
            
            
            # Allow editing settings/repetitions that are not yet associated with the set
            #
            # We calculate here how many are there already [.filter(...)] and how many there could
            # be at all (workout_set.sets)
            current_settings = exercise.setting_set.filter(set_id=set_id).count()
            diff = int(workout_set.sets) - current_settings
            
            # If there are 'free slots', create some UUIDs for them, this gives them unique form
            # names in the HTML and makes our lifes easier
            new_settings = []
            if diff > 0:
                
                # Note: use UUIDs version 1 because they are monotonously increasing
                #       and the order of the fields later is important
                new_settings = [uuid.uuid1() for i in range(0, diff)]
            template_data['new_settings'] = new_settings
            
            
            # Process request
            if request.method == 'POST':
                
                new_exercise_id = request.POST.get('current_exercise')
                new_exercise = get_object_or_404(Exercise, pk=new_exercise_id)
                
                # When there is more than one exercise per set, we need to manually set and replace
                # the IDs here, otherwise they get lost
                request_copy = request.POST
                request_copy = request_copy.copy()
                
                exercise_list = [ i for i in request_copy.getlist('exercises') if i != exercise_id]
                request_copy.setlist('exercises', exercise_list)
                request_copy.update({'exercises': new_exercise_id})
                
                
                set_form = SetForm(request_copy, instance=workout_set)
                
                if set_form.is_valid():
                    set_form.save()
                
                # Init a counter for the order in case we have to set it for new settings
                # We don't actually care how hight the counter actually is, as long as the new
                # settings get a number that puts them at the end
                order_counter = 1
                new_settings = []
                
                # input fields for settings  'setting-x, setting-y, etc.',
                #              new settings: 'new-setting-UUID1, new-setting-UUID2, etc.'
                for i in request.POST:
                    order_counter += 1
                    
                    # old settings, update
                    if i.startswith('setting'):
                        setting_id = int(i.split('-')[-1])
                        setting = get_object_or_404(Setting, pk=setting_id)
                        
                        
                        # Check if the new value is empty (the user wants the setting deleted)
                        # We don't check more, if the user enters a string, it won't be converted
                        # and nothing will happen
                        if request.POST[i] == '':
                            setting.delete()
                        else:
                            reps = int(request.POST[i])
                            setting.reps = reps
                            setting.exercise = new_exercise
                            setting.save()
                            
                    
                    # New settings, put in a list, see below
                    if i.startswith('new-setting') and request.POST[i]:
                        
                        new_settings.append(i)
                
                # new settings, sort by name (important to keep the order as
                # it was inputted in the website),create object and save
                new_settings.sort()
                for i in new_settings:
                    reps = int(request.POST[i])
                        
                    setting = Setting()
                    setting.exercise = new_exercise
                    setting.set = workout_set
                    setting.reps = reps
                    setting.order = order_counter
                    setting.save()
            
            template_data['exercise'] = exercise
            
            return render_to_response('setting/ajax_edit.html',
                              template_data,
                              context_instance=RequestContext(request))

    

# ************************
# Settings functions
# ************************
class SettingForm(ModelForm):
    class Meta:
        model = Setting
        exclude = ('set', 'exercise')

@login_required
def edit_setting(request, id, set_id, exercise_id, setting_id=None):
    template_data = {}
    template_data.update(csrf(request))
    template_data['active_tab'] = 'workout'
    
    # Load workout
    workout = get_object_or_404(TrainingSchedule, pk=id, user=request.user)
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
    
    
    # Check that the set belongs to the workout
    if set_obj.exerciseday.training.id != workout.id:  
        return HttpResponseForbidden()
    
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
            
            order = 1
            instances = setting_form.save(commit=False)
            for setting_instance in instances:
                setting_instance.set = set_obj
                setting_instance.exercise = exercise
                
                # Manualy set the order, the user can later use drag&drop to change this
                if not setting_instance.order:
                    setting_instance.order = order
                
                setting_instance.save()
                
                order += 1
            
            return HttpResponseRedirect(reverse('manager.views.view_workout', kwargs= {'id': id}))
    else:
        setting_form = SettingFormSet(queryset=Setting.objects.filter(exercise_id=exercise.id, set_id=set_obj.id))
    template_data['setting_form'] = setting_form
    
    return render_to_response('setting/edit.html',
                              template_data,
                              context_instance=RequestContext(request))

@login_required
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
                
                # Check if the user is the owner of the object
                if setting_obj.set.exerciseday.training.user == request.user:
                    setting_obj.order = order
                    setting_obj.save()
                else:
                    return HttpResponseForbidden()
                
                
            return HttpResponse(_('Success'))


@login_required
def delete_setting(request, id, set_id, exercise_id):
    """Deletes all the settings belonging to set_id and exercise_id
    """
    
    # Load the workout
    workout = get_object_or_404(TrainingSchedule, pk=id, user=request.user)
    
    # Delete all settings
    settings = Setting.objects.filter(exercise_id=exercise_id, set_id=set_id)
    settings.delete()
    
    return HttpResponseRedirect(reverse('manager.views.view_workout', kwargs= {'id': id}))

