# -*- coding: utf-8 -*-

# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

import logging

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils import translation

from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User as Django_User
from django.contrib.auth.views import login as django_loginview
from django.contrib import messages

from tastypie.models import ApiKey

from wger.exercises.models import Language
from wger.manager.forms import UserPreferencesForm
from wger.manager.forms import UserEmailForm
from wger.manager.forms import RegistrationForm
from wger.utils.constants import USER_TAB
from wger.utils.user_agents import check_request_amazon, check_request_android

logger = logging.getLogger('wger.custom')


def login(request):
    '''
    Small wrapper around the django login view
    '''

    context = {'hide_persona': check_request_amazon(request) or check_request_android(request),
               'active_tab': USER_TAB}
    return django_loginview(request,
                            template_name='user/login.html',
                            extra_context=context)


def logout(request):
    '''
    Logout the user. For temporary users, delete them.
    '''
    user = request.user
    django_logout(request)
    if user.is_authenticated() and user.userprofile.is_temporary:
        user.delete()
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

            # Save the notification language
            language = Language.objects.get(short_name=translation.get_language())
            user.userprofile.notification_language = language
            user.userprofile.save()

            user = authenticate(username=username, password=password)
            django_login(request, user)
            messages.success(request, _('You were successfully registered'))
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

        form = UserPreferencesForm(data=request.POST, instance=request.user.userprofile)
        form.user = request.user

        # Save the data if it validates
        if form.is_valid():
            form.save()
            redirect = True
    else:
        form = UserPreferencesForm(instance=request.user.userprofile)

    # Process the email form
    #
    # this is a bit ugly, but we need to take special care here, only instatiating
    # the form when the user changes its password, otherwise the email form will
    # check the adress for uniqueness and fail, because it will find one user (the
    # current one) using it. But if he changes it, we want to check that nobody else
    # has that email
    if request.method == 'POST' and request.POST["email"] != request.user.email:
        email_form = UserEmailForm(data=request.POST, instance=request.user)
        if email_form.is_valid() and redirect:
            request.user.email = email_form.cleaned_data['email']
            request.user.save()
            redirect = True
    else:
        email_form = UserEmailForm(instance=request.user)

    template_data['form'] = form
    template_data['email_form'] = email_form
    template_data['select_lists'] = ('notification_language',)

    if redirect:
        messages.success(request, _('Settings successfully updated'))
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

            profile = request.user.userprofile
            profile.show_comments = new_value
            profile.save()

            return HttpResponse(_('Success'))

        # Show ingredients in english
        elif request.GET.get('do') == 'set_english-ingredients':
            new_value = int(request.GET.get('show'))

            profile = request.user.userprofile
            profile.show_english_ingredients = new_value
            profile.save()

            return HttpResponse(_('Success'))


@login_required
def api_key(request):
    '''
    Allows the user to generate an API key for the REST API
    '''

    context = {}
    context.update(csrf(request))

    try:
        key = ApiKey.objects.get(user=request.user)
    except ApiKey.DoesNotExist:
        key = False
    if request.GET.get('new_key'):
        if key:
            key.delete()

        key = ApiKey()
        key.user = request.user
        key.save()

        # Redirect to get rid of the GET parameter
        return HttpResponseRedirect(reverse('api-key'))

    context['key'] = key

    return render_to_response('user/api_key.html',
                              context,
                              context_instance=RequestContext(request))
