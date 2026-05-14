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
    login as django_login,
    logout as django_logout,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.contrib.auth.models import User
from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from django.http import (
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseRedirect,
)
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.template.context_processors import csrf
from django.urls import (
    reverse,
    reverse_lazy,
)
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import (
    gettext as _,
    gettext_lazy,
)
from django.views.decorators.http import require_POST
from django.views.generic import (
    DetailView,
    ListView,
    RedirectView,
    UpdateView,
)

# Third Party
from allauth.account.mixins import RedirectAuthenticatedUserMixin
from allauth.account.views import (
    LoginView as AllauthLoginView,
    SignupView as AllauthSignupView,
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    ButtonHolder,
    Column,
    Layout,
    Row,
    Submit,
)
from rest_framework.authtoken.models import Token

# wger
from wger.core.forms import (
    PasswordConfirmationForm,
    PasswordResetFormCaptcha,
    UserPersonalInformationForm,
    UserPreferencesForm,
)
from wger.gym.helpers import is_same_gym
from wger.gym.models import (
    AdminUserNote,
    Contract,
)
from wger.manager.models import (
    Routine,
    WorkoutLog,
    WorkoutSession,
)
from wger.nutrition.models import NutritionPlan
from wger.utils.api_token import (
    blacklist_jwt_refresh_tokens,
    count_active_jwt_refresh_tokens,
    create_token,
)
from wger.utils.generic_views import (
    WgerFormMixin,
    WgerMultiplePermissionRequiredMixin,
)
from wger.weight.models import WeightEntry


logger = logging.getLogger(__name__)


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
        if not request.user.has_perm('gym.manage_gyms') and (
            not request.user.has_perm('gym.manage_gym')
            or not is_same_gym(request.user, user)
            or user.has_perm('gym.manage_gym')
            or user.has_perm('gym.gym_trainer')
            or user.has_perm('gym.manage_gyms')
        ):
            return HttpResponseForbidden()
    else:
        user = request.user

    form = PasswordConfirmationForm(user=request.user)

    if request.method == 'POST':
        form = PasswordConfirmationForm(data=request.POST, user=request.user)
        if form.is_valid():
            user.delete()
            messages.success(
                request, _('Account "{0}" was successfully deleted').format(user.username)
            )

            if not user_pk:
                django_logout(request)
                return HttpResponseRedirect(reverse('software:features'))
            else:
                gym_pk = request.user.userprofile.gym_id
                if gym_pk is None:
                    return HttpResponseRedirect(reverse('core:dashboard'))
                return HttpResponseRedirect(reverse('gym:gym:user-list', kwargs={'pk': gym_pk}))
    form.helper.form_action = request.path
    context = {'form': form, 'user_delete': user}

    return render(request, 'user/delete_account.html', context)


@login_required()
@require_POST
def trainer_login(request, user_pk):
    """
    Allows a trainer to 'log in' as the selected user.

    POST-only: rebinding the session is a state change and must go through
    Django's CSRF protection, which only applies to unsafe HTTP methods.
    """
    user = get_object_or_404(User, pk=user_pk)
    orig_user_pk = request.user.pk
    trainer_identity_pk = request.session.get('trainer.identity')

    # If the request user is not a trainer themselves they may only act within
    # an established trainer session and only ever to switch back to that
    # original trainer.
    if not request.user.has_perm('gym.gym_trainer'):
        if not trainer_identity_pk:
            return HttpResponseForbidden()
        original_trainer = get_object_or_404(User, pk=trainer_identity_pk)
        if not original_trainer.has_perm('gym.gym_trainer'):
            return HttpResponseForbidden()
        if user.pk != trainer_identity_pk:
            return HttpResponseForbidden()

    # Direct trainer-login: target must not itself be a privileged account.
    if request.user.has_perm('gym.gym_trainer') and (
        user.has_perm('gym.gym_trainer')
        or user.has_perm('gym.manage_gym')
        or user.has_perm('gym.manage_gyms')
    ):
        return HttpResponseForbidden()

    # Changing is only allowed between the same gym
    if not is_same_gym(request.user, user):
        return HttpResponseNotFound(
            f'There are no users in gym "{request.user.userprofile.gym}" with user ID "{user_pk}".'
        )

    # Check if we're switching back to our original account
    own = False
    if (
        user.has_perm('gym.gym_trainer')
        or user.has_perm('gym.manage_gym')
        or user.has_perm('gym.manage_gyms')
    ):
        own = True

    # Note: when logging without authenticating, it is necessary to set the
    # authentication backend
    if own:
        del request.session['trainer.identity']
    django_login(request, user, 'django.contrib.auth.backends.ModelBackend')

    if not own:
        request.session['trainer.identity'] = orig_user_pk
        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return HttpResponseRedirect(next_url)
        return HttpResponseRedirect(reverse('core:index'))
    else:
        return HttpResponseRedirect(
            reverse('gym:gym:user-list', kwargs={'pk': user.userprofile.gym_id})
        )


def logout(request):
    """
    Logout the user. For temporary users, delete them.
    """
    user = request.user
    django_logout(request)
    if user.is_authenticated and user.userprofile.is_temporary:
        user.delete()
    return HttpResponseRedirect(reverse('core:user:login'))


class WgerSignupView(AllauthSignupView):
    """
    allauth's signup view, with two wger carve-outs: registration disabled
    globally redirects to the features page (instead of allauth's "signup
    closed" page), and temporary (guest) users may still reach the
    registration page so they can create a real account.

    The wger-specific profile setup (notification language, default gym) lives
    in WgerAccountAdapter.save_user().
    """

    def dispatch(self, request, *args, **kwargs):
        if not settings.WGER_SETTINGS['ALLOW_REGISTRATION']:
            return HttpResponseRedirect(reverse('software:features'))
        if request.user.is_authenticated and request.user.userprofile.is_temporary:
            # Skip RedirectAuthenticatedUserMixin's "already logged in" redirect
            return super(RedirectAuthenticatedUserMixin, self).dispatch(
                request, *args, **kwargs
            )
        return super().dispatch(request, *args, **kwargs)


@login_required
def preferences(request):
    """
    An overview of all user preferences
    """
    context = {}
    context.update(csrf(request))

    if request.method == 'POST':
        form = UserPreferencesForm(data=request.POST, instance=request.user.userprofile)
        form.user = request.user

        if form.is_valid():
            form.save()
            messages.success(request, _('Settings successfully updated'))
            return HttpResponseRedirect(reverse('core:user:preferences'))

        messages.error(request, _('Please correct the errors below.'))
    else:
        data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        }
        form = UserPreferencesForm(initial=data, instance=request.user.userprofile)

    context['form'] = form
    context['email_verified'] = request.user.userprofile.is_verified

    return render(request, 'user/preferences.html', context)


class UserDeactivateView(
    LoginRequiredMixin,
    WgerMultiplePermissionRequiredMixin,
    RedirectView,
):
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

        if (
            request.user.has_perm('gym.manage_gym') or request.user.has_perm('gym.gym_trainer')
        ) and not is_same_gym(request.user, edit_user):
            return HttpResponseForbidden()

        # A user with only the trainer permission must not be able to (de)activate
        # other gym staff (managers, fellow trainers, general managers). Group
        # membership is checked directly so the rule still applies when the
        # target account is currently deactivated (``has_perm`` returns ``False``
        # for inactive users).
        if (
            request.user.has_perm('gym.gym_trainer')
            and not request.user.has_perm('gym.manage_gym')
            and not request.user.has_perm('gym.manage_gyms')
            and edit_user.groups.filter(
                name__in=('gym_trainer', 'gym_manager', 'general_gym_manager')
            ).exists()
        ):
            return HttpResponseForbidden()

        return super(UserDeactivateView, self).dispatch(request, *args, **kwargs)

    def get_redirect_url(self, pk):
        edit_user = get_object_or_404(User, pk=pk)
        edit_user.is_active = False
        edit_user.save()
        messages.success(self.request, _('The user was successfully deactivated'))
        return reverse('core:user:overview', kwargs=({'pk': pk}))


class UserActivateView(
    LoginRequiredMixin,
    WgerMultiplePermissionRequiredMixin,
    RedirectView,
):
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

        if (
            request.user.has_perm('gym.manage_gym') or request.user.has_perm('gym.gym_trainer')
        ) and not is_same_gym(request.user, edit_user):
            return HttpResponseForbidden()

        # A user with only the trainer permission must not be able to
        # (de)activate other gym staff (managers, fellow trainers,
        # general managers). Group membership is checked directly so the
        # rule still applies when the target account is currently
        # deactivated (``has_perm`` returns ``False`` for inactive users).
        if (
            request.user.has_perm('gym.gym_trainer')
            and not request.user.has_perm('gym.manage_gym')
            and not request.user.has_perm('gym.manage_gyms')
            and edit_user.groups.filter(
                name__in=('gym_trainer', 'gym_manager', 'general_gym_manager')
            ).exists()
        ):
            return HttpResponseForbidden()

        return super(UserActivateView, self).dispatch(request, *args, **kwargs)

    def get_redirect_url(self, pk):
        edit_user = get_object_or_404(User, pk=pk)
        edit_user.is_active = True
        edit_user.save()
        messages.success(self.request, _('The user was successfully activated'))
        return reverse('core:user:overview', kwargs=({'pk': pk}))


class UserEditView(
    WgerFormMixin,
    LoginRequiredMixin,
    WgerMultiplePermissionRequiredMixin,
    UpdateView,
):
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

        if (
            user.has_perm('gym.manage_gym')
            and not user.has_perm('gym.manage_gyms')
            and not is_same_gym(user, self.get_object())
        ):
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

    if request.method == 'POST' and request.POST.get('new_key'):
        token = create_token(request.user, request.POST.get('new_key'))

        # Redirect so a refresh doesn't try to rotate again
        return HttpResponseRedirect(reverse('core:user:api-key'))

    if request.method == 'POST' and request.POST.get('delete_key'):
        Token.objects.filter(user=request.user).delete()
        messages.success(request, _('API key was deleted'))
        return HttpResponseRedirect(reverse('core:user:api-key'))

    if request.method == 'POST' and request.POST.get('revoke_jwt_sessions'):
        blacklist_jwt_refresh_tokens(request.user)
        messages.success(request, _('All API sessions were revoked'))
        return HttpResponseRedirect(reverse('core:user:api-key'))

    context['token'] = token
    context['active_jwt_sessions'] = count_active_jwt_refresh_tokens(request.user)

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

        if (
            (user.has_perm('gym.manage_gym') or user.has_perm('gym.gym_trainer'))
            and not user.has_perm('gym.manage_gyms')
            and not is_same_gym(user, self.get_object())
        ):
            return HttpResponseForbidden()

        return super(UserDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        context = super(UserDetailView, self).get_context_data(**kwargs)
        out = []
        routines = Routine.objects.filter(user=self.object).all()
        for routine in routines:
            logs = WorkoutLog.objects.filter(routine=routine)
            out.append(
                {
                    'routine': routine,
                    'logs': logs.dates('date', 'day').count(),
                    'last_log': logs.last(),
                }
            )
        context['routine_data'] = out
        context['weight_entries'] = WeightEntry.objects.filter(user=self.object).order_by('-date')[
            :5
        ]
        context['nutrition_plans'] = NutritionPlan.objects.filter(user=self.object).order_by(
            '-creation_date'
        )[:5]
        context['session'] = WorkoutSession.objects.filter(user=self.object).order_by('-date')[:10]
        context['admin_notes'] = AdminUserNote.objects.filter(member=self.object)[:5]
        context['contracts'] = Contract.objects.filter(member=self.object)[:5]

        page_user = self.object  # type: User
        request_user = self.request.user  # type: User
        context['enable_login_button'] = request_user.has_perm('gym.gym_trainer') and is_same_gym(
            request_user, page_user
        )
        context['gym_name'] = None  # request_user.userprofile.gym.name
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
        out = {'admins': [], 'members': []}

        for u in User.objects.select_related('usercache', 'userprofile__gym').all():
            out['members'].append({'obj': u, 'last_log': None})  # u.usercache.last_activity

        return out

    def get_context_data(self, **kwargs):
        """
        Pass other info to the template
        """
        context = super(UserListView, self).get_context_data(**kwargs)
        context['show_gym'] = True
        context['user_table'] = {
            'keys': [
                _('ID'),
                _('Username'),
                _('Name'),
                _('Last activity'),
                _('Gym'),
            ],
            'users': context['object_list']['members'],
        }
        return context


class WgerPasswordChangeView(PasswordChangeView):
    template_name = 'form_content.html'
    success_url = reverse_lazy('core:user:preferences')
    title = gettext_lazy('Change password')

    def get_form(self, form_class=None):
        form = super(WgerPasswordChangeView, self).get_form(form_class)
        form.helper = FormHelper()
        form.helper.form_class = 'wger-form'
        form.helper.layout = Layout(
            'old_password',
            Row(
                Column('new_password1', css_class='col-6'),
                Column('new_password2', css_class='col-6'),
                css_class='form-row',
            ),
            ButtonHolder(Submit('submit', _('Save'), css_class='btn-success btn-block')),
        )
        return form


class WgerPasswordResetView(PasswordResetView):
    template_name = 'form_content.html'
    email_template_name = 'registration/password_reset_email.html'
    success_url = reverse_lazy('core:user:password_reset_done')
    from_email = settings.WGER_SETTINGS['EMAIL_FROM']

    def get_form_class(self):
        if settings.WGER_SETTINGS['USE_RECAPTCHA']:
            return PasswordResetFormCaptcha

        # From django
        return PasswordResetForm

    def get_form(self, form_class=None):
        # Massage django's default form. Our form already has a helper.
        if not settings.WGER_SETTINGS['USE_RECAPTCHA']:
            form = super().get_form(form_class)
            form.helper = FormHelper()
            form.helper.form_class = 'wger-form'
            form.helper.add_input(Submit('submit', _('Save'), css_class='btn-success btn-block'))
            return form

        return super().get_form(form_class)


class WgerPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'form_content.html'
    success_url = reverse_lazy('core:user:login')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.form_class = 'wger-form'
        form.helper.add_input(Submit('submit', _('Save'), css_class='btn-success btn-block'))
        return form


class WgerLoginView(AllauthLoginView):
    """
    allauth's login view, with one wger carve-out: temporary (guest) users are
    still allowed to reach the login page so they can sign in as a real
    account. allauth would otherwise redirect every authenticated user away.
    """

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.userprofile.is_temporary:
            # Skip RedirectAuthenticatedUserMixin's "already logged in" redirect
            return super(RedirectAuthenticatedUserMixin, self).dispatch(
                request, *args, **kwargs
            )
        return super().dispatch(request, *args, **kwargs)
