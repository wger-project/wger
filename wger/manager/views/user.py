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
import random


from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User as Django_User
from django.contrib.auth.views import login as django_loginview
from django.contrib import messages

from wger.manager.models import DaysOfWeek
from wger.manager.models import Workout
from wger.manager.models import Day
from wger.manager.models import Set
from wger.manager.models import Setting
from wger.manager.models import WorkoutLog

from wger.exercises.models import Exercise

from wger.weight.models import WeightEntry

from wger.manager.forms import UserPreferencesForm
from wger.manager.forms import UserEmailForm
from wger.manager.forms import RegistrationForm
from wger.manager.forms import DemoUserForm

from wger.utils.language import load_language


logger = logging.getLogger('workout_manager.custom')


def login(request):
    '''
    Small wrapper around the django login view
    '''

    return django_loginview(request,
                            template_name='user/login.html')


def logout(request):
    '''
    Logout the user
    '''
    django_logout(request)
    return HttpResponseRedirect(reverse('login'))


def registration(request):
    '''
    A form to allow for registration of new users
    '''
    template_data = {}
    template_data.update(csrf(request))

    if request.method == 'POST':

        # If the user is already logged in, redirect
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('dashboard'))

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
            messages.success(request, _('You were sucessfully registered'))
            return HttpResponseRedirect(reverse('dashboard'))
    else:
        form = RegistrationForm()

    template_data['form'] = form
    template_data['title'] = _('Register')
    template_data['form_fields'] = [i for i in form]
    template_data['form_action'] = reverse('registration')
    template_data['submit_text'] = _('Register')

    return render_to_response('form.html',
                              template_data,
                              context_instance=RequestContext(request))


def create_demo_user(request):
    '''
    Creates a demo user and adds some initial data
    '''

    template_data = {}
    template_data.update(csrf(request))

    if request.method == 'POST':
        form = DemoUserForm(data=request.POST)

        # If the data is valid, create a user, log in and redirect
        if form.is_valid():
            username = uuid.uuid4().hex[:-2]
            password = uuid.uuid4().hex[:-2]
            email = ''
            user = Django_User.objects.create_user(username,
                                                   email,
                                                   password)
            user.save()
            user_profile = user.get_profile()
            user_profile.is_temporary = True
            user_profile.save()

            #
            # Create some initial data
            # (this is a bit ugly...)
            #

            # Workout and exercises
            workout = Workout(user=user, comment=_('Sample workout'))
            workout.save()
            monday = DaysOfWeek.objects.get(pk=1)
            wednesday = DaysOfWeek.objects.get(pk=3)
            day = Day(training=workout, description=_('Sample day'))
            day.save()
            day.day.add(monday)

            day2 = Day(training=workout, description=_('Another sample day'))
            day2.save()
            day2.day.add(wednesday)

            # Biceps curls with dumbbell
            if(load_language().short_name == 'de'):
                exercise = Exercise.objects.get(pk=26)
            else:
                exercise = Exercise.objects.get(pk=81)
            day_set = Set(exerciseday=day,
                          sets=4,
                          order=2)
            day_set.save()
            day_set.exercises.add(exercise)

            setting = Setting(set=day_set,
                              exercise=exercise,
                              reps=8,
                              order=1)
            setting.save()

            # Weight log entries
            for reps in (7, 8, 9, 10):
                for i in range(1, 8):
                    log = WorkoutLog(user=user,
                                     exercise=exercise,
                                     workout=workout,
                                     reps=reps,
                                     weight=30 - reps + random.randint(1, 5),
                                     date=datetime.date.today() - datetime.timedelta(weeks=i))
                    log.save()

            # French press
            if(load_language().short_name == 'de'):
                exercise = Exercise.objects.get(pk=25)
            else:
                exercise = Exercise.objects.get(pk=84)
            day_set = Set(exerciseday=day,
                          sets=4,
                          order=2)
            day_set.save()
            day_set.exercises.add(exercise)

            setting = Setting(set=day_set,
                              exercise=exercise,
                              reps=8,
                              order=1)
            setting.save()

            # Squats
            if(load_language().short_name == 'de'):
                exercise = Exercise.objects.get(pk=6)
            else:
                exercise = Exercise.objects.get(pk=111)
            day_set = Set(exerciseday=day,
                          sets=4,
                          order=3)
            day_set.save()
            day_set.exercises.add(exercise)

            setting = Setting(set=day_set,
                              exercise=exercise,
                              reps=10,
                              order=1)
            setting.save()

            # Crunches
            if(load_language().short_name == 'de'):
                exercise = Exercise.objects.get(pk=4)
            else:
                exercise = Exercise.objects.get(pk=91)
            day_set = Set(exerciseday=day,
                          sets=4,
                          order=4)
            day_set.save()
            day_set.exercises.add(exercise)

            setting = Setting(set=day_set,
                              exercise=exercise,
                              reps=30,
                              order=1)
            setting.save()

            setting = Setting(set=day_set,
                              exercise=exercise,
                              reps=99,
                              order=2)
            setting.save()

            setting = Setting(set=day_set,
                              exercise=exercise,
                              reps=35,
                              order=3)
            setting.save()

            # (Body) weight entries
            for i in range(1, 20):
                creation_date = datetime.date.today() - datetime.timedelta(days=i)
                entry = WeightEntry(user=user,
                                    weight=80 + 0.5*i + random.randint(1, 3),
                                    creation_date=creation_date)
                entry.save()

            user = authenticate(username=username, password=password)
            django_login(request, user)
            return HttpResponseRedirect(reverse('dashboard'))
    else:
        form = DemoUserForm()

    template_data['form'] = form
    template_data['submit_text'] = _('Register')

    return render_to_response('user/demo.html',
                              template_data,
                              context_instance=RequestContext(request))


@login_required
def preferences(request):
    '''
    An overview of all user preferences
    '''
    template_data = {}
    template_data.update(csrf(request))
    redirect = False

    # Process the preferences form
    if request.method == 'POST':

        form = UserPreferencesForm(data=request.POST, instance=request.user.get_profile())
        form.user = request.user

        # Save the data if it validates
        if form.is_valid():
            form.save()
            redirect = True
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
            redirect = True
    else:
        email_form = UserEmailForm(instance=request.user)

    template_data['form'] = form
    template_data['email_form'] = email_form

    if redirect:
        messages.success(request, _('Settings sucessfully updated'))
        return HttpResponseRedirect(reverse('preferences'))
    else:
        return render_to_response('user/preferences.html',
                                  template_data,
                                  context_instance=RequestContext(request))


@login_required
def api_user_preferences(request):
    '''
    Allows the user to edit its preferences via AJAX calls
    '''

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
