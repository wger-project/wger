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

# Standard Library
import logging

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login as django_login,
    logout as django_logout
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin
)
from django.contrib.auth.models import User
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView
)
from django.http import (
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseRedirect
)
from django.shortcuts import (
    get_object_or_404,
    render
)
from django.template.context_processors import csrf
from django.urls import (
    reverse,
    reverse_lazy
)
from django.utils import translation
from django.utils.translation import (
    gettext as _,
    gettext_lazy
)
from django.views.generic import (
    DetailView,
    ListView,
    RedirectView,
    UpdateView
)

# Third Party
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    ButtonHolder,
    Column,
    Layout,
    Row,
    Submit
)
from rest_framework.authtoken.models import Token

# wger
from wger.config.models import GymConfig
from wger.core.forms import (
    PasswordConfirmationForm,
    RegistrationForm,
    RegistrationFormNoCaptcha,
    UserLoginForm,
    UserPersonalInformationForm,
    UserPreferencesForm
)
from wger.core.models import Language
from wger.gym.models import (
    AdminUserNote,
    Contract,
    GymUserConfig
)
from wger.manager.models import (
    Workout,
    WorkoutLog,
    WorkoutSession
)
from wger.nutrition.models import NutritionPlan
from wger.utils.api_token import create_token
from wger.utils.generic_views import (
    WgerFormMixin,
    WgerMultiplePermissionRequiredMixin
)
from wger.weight.models import WeightEntry


logger = logging.getLogger(__name__)


def login(request):
    """
    Small wrapper around the django login view
    """

    next_url = "?next=" + request.GET.get('next') if request.GET.get('next') else ''

    form = UserLoginForm
    form.helper.form_action = reverse('core:user:login') + next_url

    return LoginView.as_view(template_name='user/login.html',
                             authentication_form=form)


@login_required()
def delete(request, user_pk=None):
    """
    Delete a user account and all his data, requires password confirmation first

    If no user_pk is present, the user visiting the URL will be deleted, otherwise
    a gym administrator is deleting a different user
    """

    if user_pk:
        user = get_object_or_404(User, pk=user_pk)

        # Forbidden if the user has not enough rights, doesn't belong to the
        # gym or is an admin as well. General admins can delete all users.
        if not request.user.has_perm('gym.manage_gyms') \
                and (not request.user.has_perm('gym.manage_gym')
                     or request.user.userprofile.gym_id != user.userprofile.gym_id
                     or user.has_perm('gym.manage_gym')
                     or user.has_perm('gym.gym_trainer')
                     or user.has_perm('gym.manage_gyms')):
            return HttpResponseForbidden()
    else:
        user = request.user

    form = PasswordConfirmationForm(user=request.user)

    if request.method == 'POST':
        form = PasswordConfirmationForm(data=request.POST, user=request.user)
        if form.is_valid():

            user.delete()
            messages.success(request,
                             _('Account "{0}" was successfully deleted').format(user.username))

            if not user_pk:
                django_logout(request)
                return HttpResponseRedirect(reverse('software:features'))
            else:
                gym_pk = request.user.userprofile.gym_id
                return HttpResponseRedirect(reverse('gym:gym:user-list', kwargs={'pk': gym_pk}))
    form.helper.form_action = request.path
    context = {'form': form,
               'user_delete': user}

    return render(request, 'user/delete_account.html', context)


@login_required()
def trainer_login(request, user_pk):
    """
    Allows a trainer to 'log in' as the selected user
    """
    user = get_object_or_404(User, pk=user_pk)
    orig_user_pk = request.user.pk

    # No changing if identity is not set
    if not request.user.has_perm('gym.gym_trainer') \
            and not request.session.get('trainer.identity'):
        return HttpResponseForbidden()

    # Changing between trainers or managers is not allowed
    if request.user.has_perm('gym.gym_trainer') \
            and (user.has_perm('gym.gym_trainer')
                 or user.has_perm('gym.manage_gym')
                 or user.has_perm('gym.manage_gyms')):
        return HttpResponseForbidden()

    # Changing is only allowed between the same gym
    if request.user.userprofile.gym != user.userprofile.gym:
        return HttpResponseNotFound(
            'There are no users in gym "{}" with user ID "{}".'.format(
                request.user.userprofile.gym, user_pk,
            ))

    # Check if we're switching back to our original account
    own = False
    if (user.has_perm('gym.gym_trainer')
            or user.has_perm('gym.manage_gym')
            or user.has_perm('gym.manage_gyms')):
        own = True

    # Note: when logging without authenticating, it is necessary to set the
    # authentication backend
    if own:
        del(request.session['trainer.identity'])
    django_login(request, user, 'django.contrib.auth.backends.ModelBackend')

    if not own:
        request.session['trainer.identity'] = orig_user_pk
        if request.GET.get('next'):
            return HttpResponseRedirect(request.GET['next'])
        else:
            return HttpResponseRedirect(reverse('core:index'))
    else:
        return HttpResponseRedirect(reverse('gym:gym:user-list',
                                            kwargs={'pk': user.userprofile.gym_id}))


def logout(request):
    """
    Logout the user. For temporary users, delete them.
    """
    user = request.user
    django_logout(request)
    if user.is_authenticated and user.userprofile.is_temporary:
        user.delete()
    return HttpResponseRedirect(reverse('core:user:login'))


def registration(request):
    """
    A form to allow for registration of new users
    """

    # If global user registration is deactivated, redirect
    if not settings.WGER_SETTINGS['ALLOW_REGISTRATION']:
        return HttpResponseRedirect(reverse('software:features'))

    template_data = {}
    template_data.update(csrf(request))

    # Don't show captcha if the global parameter is false
    FormClass = RegistrationForm if settings.WGER_SETTINGS['USE_RECAPTCHA'] \
        else RegistrationFormNoCaptcha

    # Redirect regular users, in case they reached the registration page
    if request.user.is_authenticated and not request.user.userprofile.is_temporary:
        return HttpResponseRedirect(reverse('core:dashboard'))

    if request.method == 'POST':
        form = FormClass(data=request.POST)

        # If the data is valid, log in and redirect
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            email = form.cleaned_data['email']
            user = User.objects.create_user(username,
                                            email,
                                            password)
            user.save()

            # Pre-set some values of the user's profile
            language = Language.objects.get(short_name=translation.get_language())
            user.userprofile.notification_language = language

            # Set default gym, if needed
            gym_config = GymConfig.objects.get(pk=1)
            if gym_config.default_gym:
                user.userprofile.gym = gym_config.default_gym

                # Create gym user configuration object
                config = GymUserConfig()
                config.gym = gym_config.default_gym
                config.user = user
                config.save()

            user.userprofile.save()

            user = authenticate(username=username, password=password)
            django_login(request, user)
            messages.success(request, _('You were successfully registered'))
            return HttpResponseRedirect(reverse('core:dashboard'))
    else:
        form = FormClass()

    template_data['form'] = form
    template_data['title'] = _('Register')

    return render(request, 'form.html', template_data)


@login_required
def preferences(request):
    """
    An overview of all user preferences
    """
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
        data = {'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email}

        form = UserPreferencesForm(initial=data, instance=request.user.userprofile)

    # Process the email form
    if request.method == 'POST':
        email_form = UserPersonalInformationForm(data=request.POST, instance=request.user)

        if email_form.is_valid() and redirect:
            email_form.save()
            redirect = True
        else:
            redirect = False

    template_data['form'] = form

    if redirect:
        messages.success(request, _('Settings successfully updated'))
        return HttpResponseRedirect(reverse('core:user:preferences'))
    else:
        return render(request, 'user/preferences.html', template_data)


class UserDeactivateView(LoginRequiredMixin,
                         WgerMultiplePermissionRequiredMixin,
                         RedirectView):
    """
    Deactivates a user
    """
    permanent = False
    model = User
    permission_required = ('gym.manage_gym', 'gym.manage_gyms', 'gym.gym_trainer')

    def dispatch(self, request, *args, **kwargs):
        """
        Only managers and trainers for this gym can access the members
        """
        edit_user = get_object_or_404(User, pk=self.kwargs['pk'])

        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        if (request.user.has_perm('gym.manage_gym') or request.user.has_perm('gym.gym_trainer')) \
                and edit_user.userprofile.gym_id != request.user.userprofile.gym_id:
            return HttpResponseForbidden()

        return super(UserDeactivateView, self).dispatch(request, *args, **kwargs)

    def get_redirect_url(self, pk):
        edit_user = get_object_or_404(User, pk=pk)
        edit_user.is_active = False
        edit_user.save()
        messages.success(self.request, _('The user was successfully deactivated'))
        return reverse('core:user:overview', kwargs=({'pk': pk}))


class UserActivateView(LoginRequiredMixin,
                       WgerMultiplePermissionRequiredMixin,
                       RedirectView):
    """
    Activates a previously deactivated user
    """
    permanent = False
    model = User
    permission_required = ('gym.manage_gym', 'gym.manage_gyms', 'gym.gym_trainer')

    def dispatch(self, request, *args, **kwargs):
        """
        Only managers and trainers for this gym can access the members
        """
        edit_user = get_object_or_404(User, pk=self.kwargs['pk'])

        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        if (request.user.has_perm('gym.manage_gym') or request.user.has_perm('gym.gym_trainer')) \
                and edit_user.userprofile.gym_id != request.user.userprofile.gym_id:
            return HttpResponseForbidden()

        return super(UserActivateView, self).dispatch(request, *args, **kwargs)

    def get_redirect_url(self, pk):
        edit_user = get_object_or_404(User, pk=pk)
        edit_user.is_active = True
        edit_user.save()
        messages.success(self.request, _('The user was successfully activated'))
        return reverse('core:user:overview', kwargs=({'pk': pk}))


class UserEditView(WgerFormMixin,
                   LoginRequiredMixin,
                   WgerMultiplePermissionRequiredMixin,
                   UpdateView):
    """
    View to update the personal information of an user by an admin
    """

    model = User
    title = gettext_lazy('Edit user')
    permission_required = ('gym.manage_gym', 'gym.manage_gyms')
    form_class = UserPersonalInformationForm

    def dispatch(self, request, *args, **kwargs):
        """
        Check permissions

        - Managers can edit members of their own gym
        - General managers can edit every member
        """
        user = request.user
        if not user.is_authenticated:
            return HttpResponseForbidden()

        if user.has_perm('gym.manage_gym') \
                and not user.has_perm('gym.manage_gyms') \
                and user.userprofile.gym != self.get_object().userprofile.gym:
            return HttpResponseForbidden()

        return super(UserEditView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('core:user:overview', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        context = super(UserEditView, self).get_context_data(**kwargs)
        context['title'] = _('Edit {0}'.format(self.object))
        return context


@login_required
def api_key(request):
    """
    Allows the user to generate an API key for the REST API
    """

    context = {}
    context.update(csrf(request))

    try:
        token = Token.objects.get(user=request.user)
    except Token.DoesNotExist:
        token = None

    if request.GET.get('new_key'):
        token = create_token(request.user, request.GET.get('new_key'))

        # Redirect to get rid of the GET parameter
        return HttpResponseRedirect(reverse('core:user:api-key'))

    context['token'] = token

    return render(request, 'user/api_key.html', context)


class UserDetailView(LoginRequiredMixin, WgerMultiplePermissionRequiredMixin, DetailView):
    """
    User overview for gyms
    """
    model = User
    permission_required = ('gym.manage_gym', 'gym.manage_gyms', 'gym.gym_trainer')
    template_name = 'user/overview.html'
    context_object_name = 'current_user'

    def dispatch(self, request, *args, **kwargs):
        """
        Check permissions

        - Only managers for this gym can access the members
        - General managers can access the detail page of all users
        """
        user = request.user

        if not user.is_authenticated:
            return HttpResponseForbidden()

        if (user.has_perm('gym.manage_gym') or user.has_perm('gym.gym_trainer')) \
                and not user.has_perm('gym.manage_gyms') \
                and user.userprofile.gym != self.get_object().userprofile.gym:
            return HttpResponseForbidden()

        return super(UserDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        context = super(UserDetailView, self).get_context_data(**kwargs)
        out = []
        workouts = Workout.objects.filter(user=self.object).all()
        for workout in workouts:
            logs = WorkoutLog.objects.filter(workout=workout)
            out.append({'workout': workout,
                        'logs': logs.dates('date', 'day').count(),
                        'last_log': logs.last()})
        context['workouts'] = out
        context['weight_entries'] = WeightEntry.objects.filter(user=self.object)\
            .order_by('-date')[:5]
        context['nutrition_plans'] = NutritionPlan.objects.filter(user=self.object)\
            .order_by('-creation_date')[:5]
        context['session'] = WorkoutSession.objects.filter(user=self.object).order_by('-date')[:10]
        context['admin_notes'] = AdminUserNote.objects.filter(member=self.object)[:5]
        context['contracts'] = Contract.objects.filter(member=self.object)[:5]

        page_user = self.object  # type: User
        request_user = self.request.user  # type: User
        same_gym_id = request_user.userprofile.gym_id == page_user.userprofile.gym_id
        context['enable_login_button'] = request_user.has_perm('gym.gym_trainer') and same_gym_id
        context['gym_name'] = request_user.userprofile.gym.name
        return context


class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    Overview of all users in the instance
    """
    model = User
    permission_required = ('gym.manage_gyms',)
    template_name = 'user/list.html'

    def get_queryset(self):
        """
        Return a list with the users, not really a queryset.
        """
        out = {'admins': [],
               'members': []}

        for u in User.objects.select_related('usercache', 'userprofile__gym').all():
            out['members'].append({'obj': u,
                                   'last_log': u.usercache.last_activity})

        return out

    def get_context_data(self, **kwargs):
        """
        Pass other info to the template
        """
        context = super(UserListView, self).get_context_data(**kwargs)
        context['show_gym'] = True
        context['user_table'] = {'keys': [_('ID'),
                                          _('Username'),
                                          _('Name'),
                                          _('Last activity'),
                                          _('Gym')],
                                 'users': context['object_list']['members']}
        return context


class WgerPasswordChangeView(PasswordChangeView):
    template_name = 'form.html'
    success_url = reverse_lazy('core:user:preferences')
    title = gettext_lazy("Change password")

    def get_form(self, form_class=None):
        form = super(WgerPasswordChangeView, self).get_form(form_class)
        form.helper = FormHelper()
        form.helper.form_class = 'wger-form'
        form.helper.layout = Layout(
            'old_password',
            Row(
                Column('new_password1', css_class='form-group col-6 mb-0'),
                Column('new_password2', css_class='form-group col-6 mb-0'),
                css_class='form-row'
            ),
            ButtonHolder(Submit('submit', _("Save"), css_class='btn-success btn-block'))
        )
        return form


class WgerPasswordResetView(PasswordResetView):
    template_name = 'form.html'
    email_template_name = 'registration/password_reset_email.html'
    success_url = reverse_lazy('core:user:password_reset_done')
    from_email = settings.WGER_SETTINGS['EMAIL_FROM']

    def get_form(self, form_class=None):
        form = super(WgerPasswordResetView, self).get_form(form_class)
        form.helper = FormHelper()
        form.helper.form_class = 'wger-form'
        form.helper.add_input(Submit('submit', _("Save"), css_class='btn-success btn-block'))
        return form


class WgerPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'form.html'
    success_url = reverse_lazy('core:user:login')

    def get_form(self, form_class=None):
        form = super(WgerPasswordResetConfirmView, self).get_form(form_class)
        form.helper = FormHelper()
        form.helper.form_class = 'wger-form'
        form.helper.add_input(Submit('submit', _("Save"), css_class='btn-success btn-block'))
        return form
