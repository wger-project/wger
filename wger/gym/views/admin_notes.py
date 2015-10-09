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

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.http.response import HttpResponseForbidden
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.views.generic import (
    ListView,
    DeleteView,
    CreateView,
    UpdateView
)

from wger.gym.models import AdminUserNote
from wger.utils.generic_views import (
    WgerFormMixin,
    WgerDeleteMixin,
    WgerPermissionMixin
)


logger = logging.getLogger(__name__)


class ListView(WgerPermissionMixin, ListView):
    '''
    Overview of all available admin notes
    '''
    model = AdminUserNote
    permission_required = 'gym.add_adminusernote'
    template_name = 'admin_notes/list.html'
    member = None

    def get_queryset(self):
        '''
        Only notes for current user
        '''
        return AdminUserNote.objects.filter(member_id=self.kwargs['user_pk'])

    def dispatch(self, request, *args, **kwargs):
        '''
        Can only add notes to users in own gym
        '''
        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        user = User.objects.get(pk=self.kwargs['user_pk'])
        self.member = user
        if user.userprofile.gym_id != request.user.userprofile.gym_id:
            return HttpResponseForbidden()
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(ListView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('gym:admin_note:add',
                                         kwargs={'user_pk': self.kwargs['user_pk']})
        context['member'] = self.member
        return context


class AddView(WgerFormMixin, CreateView):
    '''
    View to add a new admin note
    '''

    model = AdminUserNote
    fields = '__all__'
    title = ugettext_lazy('Add note')
    permission_required = 'gym.add_adminusernote'
    member = None

    def get_success_url(self):
        '''
        Redirect back to user page
        '''
        return reverse('gym:admin_note:list', kwargs={'user_pk': self.member.pk})

    def dispatch(self, request, *args, **kwargs):
        '''
        Can only add notes to users in own gym
        '''
        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        user = User.objects.get(pk=self.kwargs['user_pk'])
        self.member = user
        gym_id = user.userprofile.gym_id
        if gym_id != request.user.userprofile.gym_id:
            return HttpResponseForbidden()
        return super(AddView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        '''
        Set user instances
        '''
        form.instance.member = self.member
        form.instance.user = self.request.user
        return super(AddView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(AddView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('gym:admin_note:add',
                                         kwargs={'user_pk': self.kwargs['user_pk']})
        return context


class UpdateView(WgerFormMixin, UpdateView):
    '''
    View to update an existing admin note
    '''

    model = AdminUserNote
    fields = '__all__'
    permission_required = 'gym.change_adminusernote'

    def get_success_url(self):
        '''
        Redirect back to user page
        '''
        return reverse('gym:admin_note:list', kwargs={'user_pk':
                                                      self.object.member.pk})

    def dispatch(self, request, *args, **kwargs):
        '''
        Only trainers for this gym can edit user notes
        '''

        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        note = self.get_object()
        if note.member.userprofile.gym_id != request.user.userprofile.gym_id:
            return HttpResponseForbidden()
        return super(UpdateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('gym:admin_note:edit', kwargs={'pk': self.object.id})
        context['title'] = _(u'Edit {0}').format(self.object)
        return context


class DeleteView(WgerDeleteMixin, DeleteView, WgerPermissionMixin):
    '''
    View to delete an existing admin note
    '''

    model = AdminUserNote
    permission_required = 'gym.delete_adminusernote'

    def get_success_url(self):
        '''
        Redirect back to user page
        '''
        return reverse('gym:admin_note:list', kwargs={'user_pk': self.object.member.pk})

    def dispatch(self, request, *args, **kwargs):
        '''
        Only trainers for this gym can delete user notes
        '''
        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        note = self.get_object()
        if note.member.userprofile.gym_id != request.user.userprofile.gym_id:
            return HttpResponseForbidden()
        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(DeleteView, self).get_context_data(**kwargs)
        context['title'] = _(u'Delete {0}?').format(self.object)
        context['form_action'] = reverse('gym:admin_note:delete', kwargs={'pk': self.kwargs['pk']})
        return context
