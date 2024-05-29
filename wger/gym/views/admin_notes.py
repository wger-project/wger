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
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.contrib.auth.models import User
from django.http.response import HttpResponseForbidden
from django.urls import reverse
from django.utils.translation import (
    gettext as _,
    gettext_lazy,
)
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
)

# wger
from wger.gym.models import AdminUserNote
from wger.utils.generic_views import (
    WgerDeleteMixin,
    WgerFormMixin,
)


logger = logging.getLogger(__name__)


class ListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    Overview of all available admin notes
    """

    model = AdminUserNote
    permission_required = 'gym.add_adminusernote'
    template_name = 'admin_notes/list.html'
    member = None

    def get_queryset(self):
        """
        Only notes for current user
        """
        return AdminUserNote.objects.filter(member_id=self.kwargs['user_pk'])

    def dispatch(self, request, *args, **kwargs):
        """
        Can only add notes to users in own gym
        """
        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        user = User.objects.get(pk=self.kwargs['user_pk'])
        self.member = user
        if user.userprofile.gym_id != request.user.userprofile.gym_id:
            return HttpResponseForbidden()
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        context = super(ListView, self).get_context_data(**kwargs)
        context['member'] = self.member
        return context


class AddView(WgerFormMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    View to add a new admin note
    """

    model = AdminUserNote
    fields = ['note']
    title = gettext_lazy('Add note')
    permission_required = 'gym.add_adminusernote'
    member = None

    def get_success_url(self):
        """
        Redirect back to user page
        """
        return reverse('gym:admin_note:list', kwargs={'user_pk': self.member.pk})

    def dispatch(self, request, *args, **kwargs):
        """
        Can only add notes to users in own gym
        """
        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        user = User.objects.get(pk=self.kwargs['user_pk'])
        self.member = user
        gym_id = user.userprofile.gym_id
        if gym_id != request.user.userprofile.gym_id:
            return HttpResponseForbidden()
        return super(AddView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Set user instances
        """
        form.instance.member = self.member
        form.instance.user = self.request.user
        return super(AddView, self).form_valid(form)


class UpdateView(WgerFormMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    View to update an existing admin note
    """

    model = AdminUserNote
    fields = ['note']
    permission_required = 'gym.change_adminusernote'

    def get_success_url(self):
        """
        Redirect back to user page
        """
        return reverse('gym:admin_note:list', kwargs={'user_pk': self.object.member.pk})

    def dispatch(self, request, *args, **kwargs):
        """
        Only trainers for this gym can edit user notes
        """

        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        note = self.get_object()
        if note.member.userprofile.gym_id != request.user.userprofile.gym_id:
            return HttpResponseForbidden()
        return super(UpdateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['title'] = _('Edit {0}').format(self.object)
        return context


class DeleteView(WgerDeleteMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    View to delete an existing admin note
    """

    model = AdminUserNote
    permission_required = 'gym.delete_adminusernote'

    def get_success_url(self):
        """
        Redirect back to user page
        """
        return reverse('gym:admin_note:list', kwargs={'user_pk': self.object.member.pk})

    def dispatch(self, request, *args, **kwargs):
        """
        Only trainers for this gym can delete user notes
        """
        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        note = self.get_object()
        if note.member.userprofile.gym_id != request.user.userprofile.gym_id:
            return HttpResponseForbidden()
        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        context = super(DeleteView, self).get_context_data(**kwargs)
        context['title'] = _('Delete {0}?').format(self.object)
        return context
