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
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.models import User
from django.http.response import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.views.generic import (
    DetailView,
    ListView,
    CreateView,
    UpdateView
)

from wger.utils.generic_views import WgerFormMixin
from wger.gym.models import Contract, Gym

logger = logging.getLogger(__name__)


class AddView(WgerFormMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    '''
    View to add a new contract
    '''

    model = Contract
    fields = '__all__'
    title = ugettext_lazy('Add contract')
    permission_required = 'gym.add_contract'
    member = None

    def get_initial(self):
        '''
        Get the initial data for new contracts

        Since the user's data probably didn't change between one contract and the
        next, try to fill in as much data as possible from previous ones or the
        user's profile
        '''
        out = {}
        if Contract.objects.filter(member=self.member).exists():
            last_contract = Contract.objects.filter(member=self.member).first()
            for key in ('amount',
                        'payment',
                        'email',
                        'zip_code',
                        'city',
                        'street',
                        'phone',
                        'profession'):
                out[key] = getattr(last_contract, key)
        elif self.member.email:
            out['email'] = self.member.email

        return out

    def dispatch(self, request, *args, **kwargs):
        '''
        Can only add documents to users in own gym
        '''
        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        user = get_object_or_404(User, pk=self.kwargs['user_pk'])
        self.member = user
        if user.userprofile.gym_id != request.user.userprofile.gym_id:
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
        context['form_action'] = reverse('gym:contract:add',
                                         kwargs={'user_pk': self.kwargs['user_pk']})
        return context


class DetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    '''
    Detail view of a member's contract
    '''

    model = Contract
    template_name = 'contract/view.html'
    permission_required = 'gym.add_contract'

    def dispatch(self, request, *args, **kwargs):
        '''
        Can only see contracts for own gym
        '''
        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        contract = self.get_object()
        if contract.member.userprofile.gym_id != request.user.userprofile.gym_id:
            return HttpResponseForbidden()
        return super(DetailView, self).dispatch(request, *args, **kwargs)


class UpdateView(WgerFormMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    '''
    View to update an existing contract
    '''

    model = Contract
    fields = '__all__'
    permission_required = 'gym.change_contract'
    form_action_urlname = 'gym:contract:edit'

    def dispatch(self, request, *args, **kwargs):
        '''
        Only trainers for this gym can edit user notes
        '''

        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        contract = self.get_object()
        if contract.member.userprofile.gym_id != request.user.userprofile.gym_id:
            return HttpResponseForbidden()
        return super(UpdateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Edit {0}').format(self.object)
        return context


class ListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    '''
    Overview of all available admin notes
    '''
    model = Contract
    permission_required = 'gym.add_contract'
    template_name = 'contract/list.html'
    member = None

    def get_queryset(self):
        '''
        Only documents for current user
        '''
        return Contract.objects.filter(member=self.member)

    def dispatch(self, request, *args, **kwargs):
        '''
        Can only list contract types in own gym
        '''
        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        self.member = get_object_or_404(User, id=self.kwargs['user_pk'])
        if request.user.userprofile.gym_id != self.member.userprofile.gym_id:
            return HttpResponseForbidden()

        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(ListView, self).get_context_data(**kwargs)
        context['member'] = self.member
        return context
