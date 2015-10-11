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

import datetime

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core import mail
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views import generic

from formtools.preview import FormPreview

from wger.gym.models import Gym
from wger.email.models import CronEntry, Log
from wger.utils.generic_views import WgerFormMixin


class EmailLogListView(WgerFormMixin, generic.ListView):
    '''
    Shows a list with all sent emails
    '''

    model = Log
    context_object_name = "email_list"
    template_name = 'email/overview.html'
    permission_required = 'email.add_emaillog'
    login_required = True

    def get_queryset(self):
        '''
        Can only view emails for own gym
        '''
        return Log.objects.filter(gym_id=self.kwargs['gym_pk'])

    def dispatch(self, request, *args, **kwargs):
        '''
        Can only add contract types in own gym
        '''
        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        if request.user.userprofile.gym_id != int(self.kwargs['gym_pk']):
            return HttpResponseForbidden()

        return super(EmailLogListView, self).dispatch(request, *args, **kwargs)


class EmailListFormPreview(FormPreview):
    preview_template = 'email/preview.html'
    form_template = 'email/form.html'
    list_type = None
    gym = None

    def parse_params(self, *args, **kwargs):
        '''
        Save the current recipient type
        '''
        self.gym = get_object_or_404(Gym, pk=int(kwargs['gym_pk']))

    def get_context(self, request, form):
        '''
        Context for template rendering

        Also, check for permissions here. While it is ugly and doesn't really
        belong here, it seems it's the best way to do it in a FormPreview
        '''
        if not request.user.is_authenticated() or\
                request.user.userprofile.gym_id != self.gym.id or \
                not request.user.has_perms('core.change_emailcron'):
            return HttpResponseForbidden()

        context = super(EmailListFormPreview, self).get_context(request, form)
        context['gym'] = self.gym
        context['form_action'] = reverse('email:email:add',
                                         kwargs={'gym_pk': self.gym.pk})

        return context

    def process_preview(self, request, form, context):
        '''
        Send an email to the managers with the current content
        '''
        # for email in User.objects.filter(**managers of gym**):
        #     mail.send_mail(form.cleaned_data['subject'],
        #                    form.cleaned_data['body'],
        #                    settings.DEFAULT_FROM_EMAIL,
        #                    [email.email],
        #                    fail_silently=False)
        return context

    def done(self, request, cleaned_data):
        '''
        Collect appropriate emails and save to database to send for later
        '''
        emails = []

        # Select all users in the gym
        # TODO: select only members
        for member in self.gym.userprofile_set.all():
            if member.user.email:
                emails.append(member.user.email)

        # Make list unique, so people don't get duplicate emails
        emails = list(set(emails))

        # Save an email log...
        email_log = Log()
        email_log.gym = self.gym
        email_log.user = request.user
        email_log.body = cleaned_data['body']
        email_log.subject = cleaned_data['subject']
        email_log.save()

        # ...and bulk create cron entries
        CronEntry.objects.bulk_create([CronEntry(log=email_log, email=email) for email in emails])

        return HttpResponseRedirect(reverse('gym:gym:user-list', kwargs={'pk': self.gym.pk}))
