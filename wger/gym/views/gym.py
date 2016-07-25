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
import csv
import datetime
import logging

from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import (
    Group,
    User
)
from django.core.urlresolvers import reverse, reverse_lazy
from django.http.response import (
    HttpResponseForbidden,
    HttpResponse,
    HttpResponseRedirect
)
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.views.generic import (
    ListView,
    DeleteView,
    CreateView,
    UpdateView
)

from wger.gym.forms import GymUserAddForm, GymUserPermisssionForm
from wger.gym.helpers import (
    get_user_last_activity,
    is_any_gym_admin,
    get_permission_list
)
from wger.gym.models import (
    Gym,
    GymAdminConfig,
    GymUserConfig
)
from wger.config.models import GymConfig as GlobalGymConfig
from wger.utils.generic_views import (
    WgerFormMixin,
    WgerDeleteMixin,
    WgerMultiplePermissionRequiredMixin)
from wger.utils.helpers import password_generator


logger = logging.getLogger(__name__)


class GymListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    '''
    Overview of all available gyms
    '''
    model = Gym
    permission_required = 'gym.manage_gyms'
    template_name = 'gym/list.html'

    def get_context_data(self, **kwargs):
        '''
        Pass other info to the template
        '''
        context = super(GymListView, self).get_context_data(**kwargs)
        context['global_gym_config'] = GlobalGymConfig.objects.all().first()
        return context


class GymUserListView(LoginRequiredMixin, WgerMultiplePermissionRequiredMixin, ListView):
    '''
    Overview of all users for a specific gym
    '''
    model = User
    permission_required = ('gym.manage_gym', 'gym.gym_trainer', 'gym.manage_gyms')
    template_name = 'gym/member_list.html'

    def dispatch(self, request, *args, **kwargs):
        '''
        Only managers and trainers for this gym can access the members
        '''
        if request.user.has_perm('gym.manage_gyms') \
            or ((request.user.has_perm('gym.manage_gym')
                or request.user.has_perm('gym.gym_trainer'))
                and request.user.userprofile.gym_id == int(self.kwargs['pk'])):
            return super(GymUserListView, self).dispatch(request, *args, **kwargs)
        return HttpResponseForbidden()

    def get_queryset(self):
        '''
        Return a list with the users, not really a queryset.
        '''
        out = {'admins': [],
               'members': []}

        for u in Gym.objects.get_members(self.kwargs['pk']).select_related('usercache'):
            out['members'].append({'obj': u,
                                   'last_log': u.usercache.last_activity})

        # admins list
        for u in Gym.objects.get_admins(self.kwargs['pk']):
            out['admins'].append({'obj': u,
                                  'perms': {'manage_gym': u.has_perm('gym.manage_gym'),
                                            'manage_gyms': u.has_perm('gym.manage_gyms'),
                                            'gym_trainer': u.has_perm('gym.gym_trainer'),
                                            'any_admin': is_any_gym_admin(u)}
                                  })
        return out

    def get_context_data(self, **kwargs):
        '''
        Pass other info to the template
        '''
        context = super(GymUserListView, self).get_context_data(**kwargs)
        context['gym'] = Gym.objects.get(pk=self.kwargs['pk'])
        context['admin_count'] = len(context['object_list']['admins'])
        context['user_count'] = len(context['object_list']['members'])
        context['user_table'] = {'keys': [_('ID'), _('Username'), _('Name'), _('Last activity')],
                                 'users': context['object_list']['members']}
        return context


class GymAddView(WgerFormMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    '''
    View to add a new gym
    '''

    model = Gym
    fields = '__all__'
    title = ugettext_lazy('Add new gym')
    form_action = reverse_lazy('gym:gym:add')
    permission_required = 'gym.add_gym'


@login_required
def gym_new_user_info(request):
    '''
    Shows info about a newly created user
    '''
    if not request.user.is_authenticated():
        return HttpResponseForbidden()

    if not request.session.get('gym.user'):
        return HttpResponseRedirect(reverse('gym:gym:list'))

    if not request.user.has_perm('gym.manage_gyms') \
            and not request.user.has_perm('gym.manage_gym'):
        return HttpResponseForbidden()

    context = {'new_user': get_object_or_404(User, pk=request.session['gym.user']['user_pk']),
               'password': request.session['gym.user']['password']}
    return render(request, 'gym/new_user.html', context)


@login_required
def gym_new_user_info_export(request):
    '''
    Exports the info of newly created user
    '''
    if not request.user.is_authenticated():
        return HttpResponseForbidden()

    if not request.session.get('gym.user'):
        return HttpResponseRedirect(reverse('gym:gym:list'))

    if not request.user.has_perm('gym.manage_gyms') \
            and not request.user.has_perm('gym.manage_gym'):
        return HttpResponseForbidden()

    new_user = get_object_or_404(User, pk=request.session['gym.user']['user_pk'])
    new_username = new_user.username
    password = request.session['gym.user']['password']

    # Crease CSV 'file'
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow([_('Username'), _('First name'), _('Last name'), _('Gym'), _('Password')])
    writer.writerow([new_username,
                     new_user.first_name,
                     new_user.last_name,
                     new_user.userprofile.gym.name,
                     password])

    # Send the data to the browser
    today = datetime.date.today()
    filename = 'User-data-{t.year}-{t.month:02d}-{t.day:02d}-{user}.csv'.format(t=today,
                                                                                user=new_username)
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    response['Content-Length'] = len(response.content)
    return response


def reset_user_password(request, user_pk):
    '''
    Resets the password of the selected user to random password
    '''

    user = get_object_or_404(User, pk=user_pk)

    if not request.user.is_authenticated():
        return HttpResponseForbidden()

    if not request.user.has_perm('gym.manage_gyms') \
            and not request.user.has_perm('gym.manage_gym'):
        return HttpResponseForbidden()

    if request.user.has_perm('gym.manage_gym') \
            and request.user.userprofile.gym != user.userprofile.gym:
        return HttpResponseForbidden()

    password = password_generator()
    user.set_password(password)
    user.save()

    context = {'mod_user': user,
               'password': password}
    return render(request, 'gym/reset_user_password.html', context)


def gym_permissions_user_edit(request, user_pk):
    '''
    Edits the permissions of a gym member
    '''
    member = get_object_or_404(User, pk=user_pk)
    user = request.user

    if not user.is_authenticated():
        return HttpResponseForbidden()

    if not user.has_perm('gym.manage_gyms') and not user.has_perm('gym.manage_gym'):
        return HttpResponseForbidden()

    if user.has_perm('gym.manage_gym') and user.userprofile.gym != member.userprofile.gym:
        return HttpResponseForbidden()

    # Calculate available user permissions
    form_group_permission = get_permission_list(user)

    if request.method == 'POST':
        form = GymUserPermisssionForm(request.POST,
                                      available_roles=form_group_permission)

        if form.is_valid():

            # Remove the user from all gym permission groups
            member.groups.remove(Group.objects.get(name='gym_member'))
            member.groups.remove(Group.objects.get(name='gym_trainer'))
            member.groups.remove(Group.objects.get(name='gym_manager'))
            member.groups.remove(Group.objects.get(name='general_gym_manager'))

            # Set appropriate permission groups
            if 'user' in form.cleaned_data['role']:
                member.groups.add(Group.objects.get(name='gym_member'))
            if 'trainer' in form.cleaned_data['role']:
                member.groups.add(Group.objects.get(name='gym_trainer'))
            if 'admin' in form.cleaned_data['role']:
                member.groups.add(Group.objects.get(name='gym_manager'))
            if 'manager' in form.cleaned_data['role']:
                member.groups.add(Group.objects.get(name='general_gym_manager'))

            return HttpResponseRedirect(reverse('gym:gym:user-list',
                                                kwargs={'pk': member.userprofile.gym.pk}))
    else:
        initial_data = {}
        if member.groups.filter(name='gym_member').exists():
            initial_data['user'] = True

        if member.groups.filter(name='gym_trainer').exists():
            initial_data['trainer'] = True

        if member.groups.filter(name='gym_manager').exists():
            initial_data['admin'] = True

        if member.groups.filter(name='general_gym_manager').exists():
            initial_data['manager'] = True

        form = GymUserPermisssionForm(initial={'role': initial_data},
                                      available_roles=form_group_permission)

    context = {}
    context['title'] = member.get_full_name()
    context['form'] = form
    context['form_action'] = reverse('gym:gym:edit-user-permission', kwargs={'user_pk': member.pk})
    context['extend_template'] = 'base_empty.html' if request.is_ajax() else 'base.html'
    context['submit_text'] = 'Save'

    return render(request, 'form.html', context)


class GymAddUserView(WgerFormMixin,
                     LoginRequiredMixin,
                     WgerMultiplePermissionRequiredMixin,
                     CreateView):
    '''
    View to add a user to a new gym
    '''

    model = User
    title = ugettext_lazy('Add user to gym')
    success_url = reverse_lazy('gym:gym:new-user-data')
    permission_required = ('gym.manage_gym', 'gym.manage_gyms')
    form_class = GymUserAddForm

    def get_initial(self):
        '''
        Pre-select the 'user' role
        '''
        return {'role': ['user']}

    def dispatch(self, request, *args, **kwargs):
        '''
        Only managers for this gym can add new members
        '''
        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        if not request.user.has_perm('gym.manage_gyms') \
                and not request.user.has_perm('gym.manage_gym'):
            return HttpResponseForbidden()

        # Gym managers can edit their own gym only, general gym managers
        # can edit all gyms
        if request.user.has_perm('gym.manage_gym') \
                and not request.user.has_perm('gym.manage_gyms') \
                and request.user.userprofile.gym_id != int(self.kwargs['gym_pk']):
            return HttpResponseForbidden()

        return super(GymAddUserView, self).dispatch(request, *args, **kwargs)

    def get_form(self):
        '''
        Set available user permissions
        '''
        return self.form_class(available_roles=get_permission_list(self.request.user),
                               **self.get_form_kwargs())

    def form_valid(self, form):
        '''
        Create the user, set the user permissions and gym
        '''
        gym = Gym.objects.get(pk=self.kwargs['gym_pk'])
        password = password_generator()
        user = User.objects.create_user(form.cleaned_data['username'],
                                        form.cleaned_data['email'],
                                        password)
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        form.instance = user

        # Update profile
        user.userprofile.gym = gym
        user.userprofile.save()

        # Set appropriate permission groups
        if 'user' in form.cleaned_data['role']:
            user.groups.add(Group.objects.get(name='gym_member'))
        if 'trainer' in form.cleaned_data['role']:
            user.groups.add(Group.objects.get(name='gym_trainer'))
        if 'admin' in form.cleaned_data['role']:
            user.groups.add(Group.objects.get(name='gym_manager'))
        if 'manager' in form.cleaned_data['role']:
            user.groups.add(Group.objects.get(name='general_gym_manager'))

        self.request.session['gym.user'] = {'user_pk': user.pk,
                                            'password': password}

        # Create config
        if is_any_gym_admin(user):
            config = GymAdminConfig()
        else:
            config = GymUserConfig()

        config.user = user
        config.gym = gym
        config.save()

        return super(GymAddUserView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(GymAddUserView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('gym:gym:add-user',
                                         kwargs={'gym_pk': self.kwargs['gym_pk']})
        return context


class GymUpdateView(WgerFormMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    '''
    View to update an existing gym
    '''

    model = Gym
    fields = '__all__'
    title = ugettext_lazy('Edit gym')
    permission_required = 'gym.change_gym'

    def dispatch(self, request, *args, **kwargs):
        '''
        Only managers for this gym and general managers can edit the gym
        '''
        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        if request.user.has_perm('gym.manage_gym')\
                and not request.user.has_perm('gym.manage_gyms'):
            if request.user.userprofile.gym_id != int(self.kwargs['pk']):
                return HttpResponseForbidden()
        return super(GymUpdateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(GymUpdateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('gym:gym:edit', kwargs={'pk': self.object.id})
        context['title'] = _(u'Edit {0}').format(self.object)
        return context


class GymDeleteView(WgerDeleteMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    '''
    View to delete an existing gym
    '''

    model = Gym
    fields = ('name',
              'phone',
              'email',
              'owner',
              'zip_code',
              'city',
              'street')
    success_url = reverse_lazy('gym:gym:list')
    permission_required = 'gym.delete_gym'

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(GymDeleteView, self).get_context_data(**kwargs)
        context['title'] = _(u'Delete {0}?').format(self.object)
        context['form_action'] = reverse('gym:gym:delete', kwargs={'pk': self.kwargs['pk']})
        return context
