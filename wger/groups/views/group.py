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

from actstream import action
from actstream.models import target_stream

from django.http import HttpResponseForbidden
from django.core.urlresolvers import (
    reverse_lazy,
    reverse
)
from django.utils.translation import (
    ugettext_lazy,
    ugettext as _
)
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView
)

from wger.groups.models import (
    Group,
    Membership
)
from wger.utils.generic_views import (
    WgerPermissionMixin,
    WgerFormMixin,
    WgerDeleteMixin
)


class ListView(WgerPermissionMixin, ListView):
    '''
    Overview of all available groups
    '''
    model = Group
    login_required = True
    template_name = 'group/list.html'


class DetailView(WgerPermissionMixin, DetailView):
    '''
    Detail view for a group
    '''

    model = Group
    login_required = True

    def get_template_names(self):
        '''
        Return the correct template based on membership status:

        * members see the regular group detail page
        * non-members reach a different page where they can apply for membership
        '''
        group = self.get_object()
        if not group.public\
                and not group.membership_set.filter(user=self.request.user).exists():
            return 'group/view_application.html'
        return 'group/view.html'

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(DetailView, self).get_context_data(**kwargs)
        application = self.object.application_set.filter(user=self.request.user).exists()
        group = self.get_object()
        member_list = group.get_member_list()
        admin_list = group.get_admins_list()

        context['last_activity'] = target_stream(self.object)[:20]
        context['application'] = application

        # Get the structure for the different option menus here
        #
        # This makes it easier to perform some of the comparisons and permission checks
        # and keeps the template clearer, since then we can just iterate over the resulting
        # option lists
        context['group_dropdown'] = []
        if self.request.user in member_list:
            context['group_dropdown'].append([_("Leave group"),
                                              reverse('groups:member:leave',
                                                      kwargs={'group_pk': group.pk})])
        else:
            context['group_dropdown'].append([_("Join group"),
                                              reverse('groups:member:join-public',
                                                      kwargs={'group_pk': group.pk})])
        if self.request.user in admin_list:
            context['group_dropdown'].append([_("Edit"),
                                              reverse('groups:group:edit',
                                                      kwargs={'pk': group.pk})])
            context['group_dropdown'].append([_("Delete"),
                                              reverse('groups:group:delete',
                                                      kwargs={'pk': group.pk})])

        context['memberships_list'] = []
        for membership in group.membership_set.all():
            out = {'user': membership.user,
                   'is_admin': membership.admin,
                   'dropdowns': []}

            if self.request.user in admin_list:
                out['dropdowns'].append([_('Kick out'),
                                         reverse('groups:member:leave',
                                                 kwargs={'group_pk': group.pk,
                                                         'user_pk': membership.user_id})])

            if self.request.user in admin_list and membership.user not in admin_list:
                out['dropdowns'].append([_('Promote to administrator'),
                                        reverse('groups:member:promote',
                                                kwargs={'group_pk': group.pk,
                                                        'user_pk': membership.user_id})])

            if self.request.user in admin_list and membership.user in admin_list:
                out['dropdowns'].append([_('Demote administrator'),
                                        reverse('groups:member:demote',
                                                kwargs={'group_pk': group.pk,
                                                        'user_pk': membership.user_id})])

            context['memberships_list'].append(out)

        return context


class AddView(WgerFormMixin, CreateView):
    '''
    View to add a new group
    '''

    model = Group
    fields = ('name',
              'description',
              'public')
    title = ugettext_lazy('Create new group')
    form_action = reverse_lazy('groups:group:add')

    def form_valid(self, form):
        '''
        Add the user to list of members and make him admin
        '''

        # First save the form so the group gets saved to the database
        out = super(AddView, self).form_valid(form)

        # If the user is member of a gym, set the appropriate foreign keys
        if self.request.user.userprofile.gym:
            form.instance.gym_id = self.request.user.userprofile.gym_id
            form.instance.save()

        membership = Membership()
        membership.admin = True
        membership.group = form.instance
        membership.user = self.request.user
        membership.save()

        # Add event to django activity stream
        action.send(self.request.user, verb='created', target=form.instance)
        return out


class UpdateView(WgerFormMixin, UpdateView):
    '''
    View to update an existing Group
    '''

    model = Group
    fields = ('name', 'description', 'image', 'public')
    form_action_urlname = 'groups:group:edit'
    login_required = True

    def form_valid(self, form):
        '''
        Add event to django activity stream
        '''
        action.send(self.request.user, verb='edited', target=form.instance)
        return super(UpdateView, self).form_valid(form)

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
        context['title'] = _(u'Edit {0}').format(self.object)
        context['enctype'] = 'multipart/form-data'
        return context


class DeleteView(WgerDeleteMixin, DeleteView):
    '''
    View to delete an existing Group
    '''

    model = Group
    login_required = True
    form_action_urlname = 'groups:group:delete'

    def dispatch(self, request, *args, **kwargs):
        '''
        Only administrators for the group can delete it
        '''
        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        group = self.get_object()
        if group.membership_set.filter(user=request.user).exists() \
                and group.membership_set.get(user=request.user).admin:
            return super(DeleteView, self).dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(DeleteView, self).get_context_data(**kwargs)
        context['title'] = _(u'Delete {0}?').format(self.object)
        return context

    def get_success_url(self):
        '''
        Redirect back to user page
        '''
        return reverse('groups:group:list')
