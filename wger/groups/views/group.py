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
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseForbidden
from django.utils.translation import ugettext_lazy
from django.utils.translation import ugettext as _
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView
)
from django.db.models import Q

from wger.groups.models import (
    Group,
    Membership
)
from wger.utils.generic_views import (
    WgerPermissionMixin,
    WgerFormMixin
)


class ListView(WgerPermissionMixin, ListView):
    '''
    Overview of all available groups
    '''
    model = Group
    login_required = True
    template_name = 'group/list.html'

    def get_queryset(self):
        '''
        List only public groups and groups the user is already a member of
        '''
        return Group.objects.filter(Q(public=True) | Q(members=self.request.user)).distinct()


class DetailView(WgerPermissionMixin, DetailView):
    '''
    Detail view for a group
    '''

    model = Group
    login_required = True
    template_name = 'group/view.html'

    def dispatch(self, request, *args, **kwargs):
        '''
        Check for membership
        '''
        group = self.get_object()
        if not group.public\
                and request.user.is_authenticated()\
                and not group.membership_set.filter(user=request.user):
            return HttpResponseForbidden()

        return super(DetailView, self).dispatch(request, *args, **kwargs)


class AddView(WgerFormMixin, CreateView):
    '''
    View to add a new group
    '''

    model = Group
    fields = ('name',
              'description',
              'image',
              'public')
    title = ugettext_lazy('Create new group')
    form_action = reverse_lazy('groups:group:add')

    def form_valid(self, form):
        '''
        Add the user to list of members and make him admin
        '''

        # First save the form so the group gets saved to the database
        out = super(AddView, self).form_valid(form)

        membership = Membership()
        membership.admin = True
        membership.group = form.instance
        membership.user = self.request.user
        membership.save()

        return out

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(AddView, self).get_context_data(**kwargs)
        context['enctype'] = 'multipart/form-data'
        return context


class UpdateView(WgerFormMixin, UpdateView):
    '''
    View to update an existing Group
    '''

    model = Group
    fields = ('name', 'description', 'image', 'public')
    login_required = True

    def dispatch(self, request, *args, **kwargs):
        '''
        Only administrators for the group can edit it
        '''
        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        group = self.get_object()
        if group.membership_set.filter(user=request.user).exists() \
                and group.membership_set.get(user=request.user).admin:
            return super(UpdateView, self).dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('groups:group:edit', kwargs={'pk': self.object.id})
        context['title'] = _(u'Edit {0}').format(self.object)
        context['enctype'] = 'multipart/form-data'
        return context
