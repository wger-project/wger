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
from django.core.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from django.forms import Form
from django.forms import ModelForm
from django.forms import EmailField
from django.forms import CharField
from django.forms import SelectMultiple
from django.forms import ValidationError
from django.forms.models import modelformset_factory


from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User as Django_User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import login as django_loginview
from django.contrib.auth.views import password_change as django_pwchange

from django.views.generic import DeleteView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DetailView

from manager.models import DaysOfWeek
from manager.models import TrainingSchedule
from manager.models import Day
from manager.models import Set
from manager.models import Setting
from manager.models import UserProfile
from manager.models import WorkoutLog

from exercises.models import Exercise

from nutrition.models import NutritionPlan

from weight.models import WeightEntry

from workout_manager import get_version
from workout_manager.constants import WORKOUT_TAB
from workout_manager.constants import USER_TAB
from workout_manager.generic_views import YamlFormMixin
from workout_manager.generic_views import YamlDeleteMixin
from workout_manager.widgets import ExerciseAjaxSelect
from workout_manager.widgets import TranslatedSelectMultiple


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
    template_data['active_tab'] = USER_TAB
    
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
    """
    Small wrapper around the django login view
    """
    
    return django_loginview(request,
                            template_name = 'user/login.html',
                            extra_context = {'active_tab': USER_TAB})

def logout(request):
    """Logout the user
    """
    django_logout(request)
    return HttpResponseRedirect(reverse('login'))

class UserEmailForm(ModelForm):
    email = EmailField(label=_("Email"),
                       help_text = _("Completely optional, but needed to reset your password "
                                     "in case you forget it."),
                       required = False)
    
    def clean_email(self):
        # Email must be unique systemwide
        email = self.cleaned_data["email"]
        logger.debug(email)
        if not email:
            logger.debug(11111)
            return email
        try:
            Django_User.objects.get(email=email)
        except Django_User.DoesNotExist:
            return email
        raise ValidationError(_("This email is already used."))

class RegistrationForm(UserCreationForm, UserEmailForm):
    pass

def registration(request):
    """A form to allow for registration of new users
    """
    template_data = {}
    template_data.update(csrf(request))
    template_data['active_tab'] = USER_TAB
    
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        
        # If the data is valid, log in and redirect
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            email = form.cleaned_data['email']
            user = Django_User.objects.create_user(username,
                                                   email,
                                                   password)
            user.save()
            user = authenticate(username=username, password=password)
            django_login(request, user)
            return HttpResponseRedirect(reverse('index'))
    else:
        form = RegistrationForm()

    template_data['form'] = form
    
    return render_to_response('user/registration.html',
                              template_data,
                              context_instance=RequestContext(request))



def preferences(request):
    """An overview of all user preferences
    """
    template_data = {}
    template_data.update(csrf(request))
    template_data['active_tab'] = USER_TAB
    
    # Process the preferences form
    if request.method == 'POST':
    
        form = UserPreferencesForm(data=request.POST, instance=request.user.get_profile())
        form.user = request.user
        
        # Save the data if it validates
        if form.is_valid():
            form.save()
    else:
        form = UserPreferencesForm(instance=request.user.get_profile())
   
   
    # Process the email form
    #
    # this is a bit ugly, but we need to take special care here, only instatiating
    # the form when the user changes its password, otherwise the email form will
    # check the adress for uniqueness and fail, because it will find one user (the
    # current one) using it. But if he changes it, we want to check that nobody else
    # has that email
    if request.method == 'POST' and request.POST["email"] != request.user.email:
        email_form = UserEmailForm(data=request.POST, instance=request.user)
        if email_form.is_valid():
            request.user.email = email_form.cleaned_data['email']
            request.user.save()
    else:
        email_form = UserEmailForm(instance=request.user)
   
    template_data['form'] = form
    template_data['email_form'] = email_form
   
    return render_to_response('user/preferences.html',
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
    template_data['active_tab'] = WORKOUT_TAB
    
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
    template_data['active_tab'] = WORKOUT_TAB
    
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
                    muscle_bg = 'images/muscles/main/muscle-%s.svg' % muscle.id
                    
                    # Add the muscles to the background list, but only once.
                    #
                    # While the combining effect (the more often a muscle gets
                    # added, the more intense the colour) is interesting, the
                    # end result is a very unnatural, very bright colour.
                    if muscle.is_front and muscle_bg not in backgrounds_front:
                        backgrounds_front.append(muscle_bg)
                    elif not muscle.is_front and muscle_bg not in backgrounds_back:
                        backgrounds_back.append(muscle_bg)
    
    # Append the correct "main" background, with the silhouette of the human body
    backgrounds_front.append('images/muscles/muscular_system_front.svg')
    backgrounds_back.append('images/muscles/muscular_system_back.svg')
    
    template_data['muscle_backgrounds_front'] = backgrounds_front
    template_data['muscle_backgrounds_back'] = backgrounds_back
    
    
    return render_to_response('workout/view.html', 
                              template_data,
                              context_instance=RequestContext(request))


class WorkoutCopyForm(Form):
    comment = CharField(max_length = 100,
                        help_text  = _('The goal or description of the new workout.'),
                        required   = False)

@login_required
def copy_workout(request, pk):
    """
    Makes a copy of a workout
    """
    
    workout = get_object_or_404(TrainingSchedule, pk=pk, user=request.user)
    
    # Process request
    if request.method == 'POST':
        workout_form = WorkoutCopyForm(request.POST)
        
        if workout_form.is_valid():
        
            # Copy workout
            days = workout.day_set.all()
            
            workout_copy = workout
            workout_copy.pk = None
            workout_copy.comment = workout_form.cleaned_data['comment']
            workout_copy.save()
            
            # Copy the days
            for day in days:
                sets = day.set_set.all()
                
                day_copy = day
                day_copy.pk = None
                day_copy.training = workout_copy
                day_copy.save()
                
                # Copy the sets
                for current_set in sets:
                    current_set_id = current_set.id
                    exercises = current_set.exercises.all()
                    
                    current_set_copy = current_set
                    current_set_copy.pk = None
                    current_set_copy.exerciseday = day_copy
                    current_set_copy.save()
                    
                    # Exercises has Many2Many relationship
                    current_set_copy.exercises = exercises
                    
                    # Go through the exercises
                    for exercise in exercises:
                        settings = exercise.setting_set.filter(set_id=current_set_id)
                    
                        # Copy the settings
                        for setting in settings:
                            setting_copy = setting
                            setting_copy.pk = None
                            setting_copy.set = current_set_copy
                            setting_copy.save()
                            
            return HttpResponseRedirect(reverse('manager.views.view_workout', kwargs= {'id': workout.id}))
    else:
        workout_form = WorkoutCopyForm({'comment' : workout.comment})
        
        template_data = {}
        template_data.update(csrf(request))
        template_data['title']       = _('Copy workout')
        template_data['form']        = workout_form
        template_data['form_action'] = reverse('workout-copy', kwargs= {'pk': workout.id})
        template_data['form_fields'] = [workout_form['comment']]
    
        return render_to_response('form.html',
                              template_data,
                              context_instance=RequestContext(request))

    


@login_required
def add(request):
    """Add a new workout and redirect to its page
    """
    workout = TrainingSchedule()
    workout.user = request.user
    workout.save()
    
    return HttpResponseRedirect(reverse('manager.views.view_workout', kwargs= {'id': workout.id}))


class WorkoutDeleteView(YamlDeleteMixin, DeleteView):
    """
    Generic view to delete a workout routine
    """
    
    active_tab = WORKOUT_TAB
    model = TrainingSchedule
    success_url = reverse_lazy('manager.views.overview')
    title = ugettext_lazy('Delete workout')
    form_action_urlname = 'workout-delete'
    
    
class WorkoutEditView(YamlFormMixin, UpdateView):
    """
    Generic view to update an existing workout routine
    """
    
    active_tab = WORKOUT_TAB
    model = TrainingSchedule
    form_class = WorkoutForm
    title = ugettext_lazy('Edit workout')
    form_action_urlname = 'workout-edit'
    
    
# ************************
# Day functions
# ************************
class DayForm(ModelForm):
    class Meta:
        model = Day
        exclude=('training',)
        
        widgets = {
                    'day': TranslatedSelectMultiple()
        }
        

class DayView(YamlFormMixin):
    """
    Base generic view for exercise day
    """
    
    active_tab = WORKOUT_TAB
    model = Day
    form_class = DayForm
    
    def get_success_url(self):
        return reverse('manager.views.view_workout', kwargs ={'id': self.object.training.id})

    
    def get_form(self, form_class):
        """
        Filter the days of the week that are alreeady used by other days"""
        
        # Get the form
        form  = super(DayView, self).get_form(form_class)
        
        # Calculate the used days ('used' by other days in the same workout)
        if self.object:
            workout = self.object.training
        else:
            workout = TrainingSchedule.objects.get(pk = self.kwargs['workout_pk'])
        
        used_days = []
        for day in workout.day_set.all():
            for weekday in day.day.all():
                if not self.object or day.id != self.object.id:
                    used_days.append(weekday.id)        
        used_days.sort()
        
        # Set the queryset for day
        form.fields['day'].queryset = DaysOfWeek.objects.exclude(id__in=used_days)
        
        return form 




class DayEditView(DayView, UpdateView):
    """
    Generic view to update an existing exercise day
    """
    
    title = ugettext_lazy('Edit workout day')
    form_action_urlname = 'day-edit'
    

class DayCreateView(DayView, CreateView):
    """
    Generic view to add a new exercise day
    """
    
    title = ugettext_lazy('Add workout day')
    owner_object = {'pk': 'workout_pk', 'class': TrainingSchedule}
    
    
    
    def form_valid(self, form):
        """
        Set the workout this day belongs to
        """
        form.instance.training = TrainingSchedule.objects.get(pk = self.kwargs['workout_pk'])
        return super(DayCreateView, self).form_valid(form)
    
    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(DayCreateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('day-add',
                                         kwargs={'workout_pk': self.kwargs['workout_pk']}) 
        return context

    

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
        widgets = {
                'exercises': ExerciseAjaxSelect(),
        }
        
    # We need to overwrite the init method here because otherwise Django
    # will outut a default help text, regardless of the widget used
    # https://code.djangoproject.com/ticket/9321 
    def __init__(self, *args, **kwargs):
        super(SetForm, self).__init__(*args, **kwargs)
        self.fields['exercises'].help_text = _('You can search for more than one exercise, '
                                            'they will be grouped together for a superset.')

@login_required
def edit_set(request, id, day_id, set_id=None):
    """ Edits/creates a set
    """
    
    template_data = {}
    template_data.update(csrf(request))
    template_data['active_tab'] = WORKOUT_TAB
    
    # Load workout
    workout = get_object_or_404(TrainingSchedule, pk=id, user=request.user)
    template_data['workout'] = workout
    
    # Load day
    day = get_object_or_404(Day, pk=day_id)
    template_data['day'] = day
    
    # Load set
    
    # If the object is new, we will receice a 'None' (string) as the ID
    # from the template, so we check for it (ValueError) and for an actual
    # None (TypeError)
    try:
        int(set_id)
        workout_set = get_object_or_404(Set, pk=set_id)
        
        # Check if all objects belong to the workout
        if workout_set.exerciseday.id != day.id:  
            return HttpResponseForbidden()
    except ValueError, TypeError:
        workout_set = Set()
    
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
    template_data['active_tab'] = WORKOUT_TAB
    
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



# ************************
# Log functions
# ************************

WorkoutLogFormSet = modelformset_factory(WorkoutLog,
                                         exclude=('user',
                                                 'workout'),
                                         extra = 4)


def workout_log_add(request, pk):
    '''
    Add a new workout log
    '''
    template_data = {}
    template_data.update(csrf(request))
    template_data['active_tab'] = WORKOUT_TAB
    
    day = get_object_or_404(Day, pk=pk)
    if day.get_owner_object().user != request.user:
        return HttpResponseForbidden()
    
    nr_of_exercises = 0
    for exercise_set in day.set_set.all():
        nr_of_exercises = nr_of_exercises + len(exercise_set.exercises.all())
    
    logger.debug(nr_of_exercises)
    
    if request.method == 'POST':
        formset = WorkoutLogFormSet(data=request.POST)
        
        # If the data is valid, log in and redirect
        if formset.is_valid():
            instances = formset.save(commit = False)
            for instance in instances:
                instance.user = request.user
                instance.workout = day.training
                instance.save()
            
            return HttpResponseRedirect(reverse('workout-view', kwargs={'pk': day.training.id}))
        else:
            logger.debug(formset.errors)
    else:
        formset = WorkoutLogFormSet(queryset=WorkoutLog.objects.filter(exercise = -1),
                                    initial = [{'date': datetime.date.today()},
                                               {'date': datetime.date.today()},
                                               {'date': datetime.date.today()},
                                               {'date': datetime.date.today()},
                                              ]
                                   )

    template_data['formset'] = formset
    
    return render_to_response('day/log.html',
                              template_data,
                              context_instance=RequestContext(request))

    
class WorkoutLogCreateView(YamlFormMixin, CreateView):
    '''
    Add a new workout log
    '''
    
    model = WorkoutLog
    #form_class = WorkoutLogFormSet
    template_name = 'form.html'
    

class WorkoutLogDetailView(DetailView):
    '''
    An overview of the workout's log
    '''
    
    # TODO: check ownership
    
    model = TrainingSchedule
    template_name = 'workout/log.html'
    context_object_name = 'workout'
