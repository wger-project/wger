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

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.http.response import HttpResponseForbidden, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.views.generic import ListView
from django.views.generic import DeleteView
from django.views.generic import CreateView
from django.views.generic import UpdateView

from wger.gym.forms import GymUserAddForm, GymUserPermisssionForm
from wger.gym.helpers import get_user_last_activity, is_any_gym_admin
from wger.gym.models import Gym
from wger.gym.models import GymAdminConfig
from wger.gym.models import GymUserConfig
from wger.config.models import GymConfig as GlobalGymConfig

from wger.utils.generic_views import WgerFormMixin
from wger.utils.generic_views import WgerDeleteMixin
from wger.utils.generic_views import WgerPermissionMixin
from wger.utils.helpers import password_generator


logger = logging.getLogger('wger.custom')


class GymListView(WgerPermissionMixin, ListView):
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


class GymUserListView(WgerPermissionMixin, ListView):
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
        out = []
        for u in User.objects.filter(userprofile__gym_id=self.kwargs['pk']):
            out.append({'obj': u,
                        'last_log': get_user_last_activity(u),
                        'perms': {'manage_gym': u.has_perm('gym.manage_gym'),
                                  'manage_gyms': u.has_perm('gym.manage_gyms'),
                                  'gym_trainer': u.has_perm('gym.gym_trainer'),
                                  'any_admin': is_any_gym_admin(u)}})
        return out

    def get_context_data(self, **kwargs):
        '''
        Pass other info to the template
        '''
        context = super(GymUserListView, self).get_context_data(**kwargs)
        context['gym'] = Gym.objects.get(pk=self.kwargs['pk'])
        context['admin_count'] = len([i for i in context['object_list']
                                      if i['perms']['any_admin']])
        context['user_count'] = len([i for i in context['object_list']
                                     if not i['perms']['any_admin']])
        return context


class GymAddView(WgerFormMixin, CreateView):
    '''
    View to add a new gym
    '''

    model = Gym
    success_url = reverse_lazy('gym:gym:list')
    title = ugettext_lazy('Add gym')
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
    writer.writerow([_('User name'), _('First name'), _('Last name'), _('Gym'), _('Password')])
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


def gym_permissions_user_edit(request, user_pk):
    '''
    Edits the permissions of a gym member
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

    if request.method == 'POST':
        form = GymUserPermisssionForm(request.POST)

        if form.is_valid():

            # Remove the user from all gym permission groups
            user.groups.remove(Group.objects.get(name='gym_member'))
            user.groups.remove(Group.objects.get(name='gym_trainer'))
            user.groups.remove(Group.objects.get(name='gym_manager'))
            user.groups.remove(Group.objects.get(name='general_gym_manager'))

            # Set appropriate permission groups
            if 'user' in form.cleaned_data['role']:
                user.groups.add(Group.objects.get(name='gym_member'))
            if 'trainer' in form.cleaned_data['role']:
                user.groups.add(Group.objects.get(name='gym_trainer'))
            if 'admin' in form.cleaned_data['role']:
                user.groups.add(Group.objects.get(name='gym_manager'))
            if 'manager' in form.cleaned_data['role']:
                user.groups.add(Group.objects.get(name='general_gym_manager'))

            return HttpResponseRedirect(reverse('gym:gym:user-list',
                                                kwargs={'pk': user.userprofile.gym.pk}))
    else:
        initial_data = {}
        if user.groups.filter(name='gym_member').exists():
            initial_data['user'] = True

        if user.groups.filter(name='gym_trainer').exists():
            initial_data['trainer'] = True

        if user.groups.filter(name='gym_manager').exists():
            initial_data['admin'] = True

        if user.groups.filter(name='general_gym_manager').exists():
            initial_data['manager'] = True

        form = GymUserPermisssionForm(initial={'role': initial_data})

    context = {}
    context['title'] = user.get_full_name()
    context['form'] = form
    context['form_action'] = reverse('gym:gym:edit-user-permission', kwargs={'user_pk': user.pk})
    context['extend_template'] = 'base_empty.html' if request.is_ajax() else 'base.html'

    return render(request, 'form.html', context)


class GymAddUserView(WgerFormMixin, CreateView):
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

        if request.user.has_perm('gym.manage_gym') \
                and request.user.userprofile.gym_id != int(self.kwargs['gym_pk']):
            return HttpResponseForbidden()

        return super(GymAddUserView, self).dispatch(request, *args, **kwargs)

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


class GymUpdateView(WgerFormMixin, UpdateView):
    '''
    View to update an existing license
    '''

    model = Gym
    title = ugettext_lazy('Edit gym')
    permission_required = 'gym.change_gym'

    def dispatch(self, request, *args, **kwargs):
        '''
        Only managers for this gym can add new members
        '''
        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        if request.user.has_perm('gym.manage_gym'):
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


class GymDeleteView(WgerDeleteMixin, DeleteView, WgerPermissionMixin):
    '''
    View to delete an existing gym
    '''

    model = Gym
    success_url = reverse_lazy('gym:gym:list')
    permission_required = 'gym.delete_gym'

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(GymDeleteView, self).get_context_data(**kwargs)
        context['title'] = _(u'Delete {0}?'.format(self.object))
        context['form_action'] = reverse('gym:gym:delete', kwargs={'pk': self.kwargs['pk']})
        return context
