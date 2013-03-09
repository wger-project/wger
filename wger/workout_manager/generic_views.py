# -*- coding: utf-8 -*-

# This file is part of Workout Manager.
#
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

import logging
import bleach

from django.forms import models
from django.http import HttpResponseForbidden
from django.utils.translation import ugettext_lazy

from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from django.views.generic.edit import ModelFormMixin

from wger.workout_manager.constants import HTML_TAG_WHITELIST
from wger.workout_manager.constants import HTML_ATTRIBUTES_WHITELIST
from wger.workout_manager.constants import HTML_STYLES_WHITELIST

logger = logging.getLogger('workout_manager.custom')


class YamlFormMixin(ModelFormMixin):
    template_name = 'form.html'

    form_fields = []
    custom_js = ''
    form_action = ''
    form_action_urlname = ''
    title = ''
    owner_object = False
    submit_text = ugettext_lazy('Save')
    clean_html = ()

    def get_context_data(self, **kwargs):
        '''
        Set necessary template data to correctly render the form
        '''

        # Call the base implementation first to get a context
        context = super(YamlFormMixin, self).get_context_data(**kwargs)

        # CSRF token
        context.update(csrf(self.request))

        # Custom order for form fields. The list comprehension is to avoid
        # weird problems with django's template when accessing the fields with "form.fieldname"
        if self.form_fields:
            context['form_fields'] = [kwargs['form'][i] for i in self.form_fields]

        # Use the the order as defined in the model
        else:
            context['form_fields'] = kwargs['form']

        # Drop down lists get a special CSS class
        select_list = []
        for i in self.form_fields:
            if isinstance(kwargs['form'][i].field, models.ModelChoiceField):
                select_list.append(i)
        context['select_lists'] = select_list

        # Custom JS code on form (autocompleter, editor, etc.)
        context['custom_js'] = self.custom_js

        # When viewing the page on it's own, this is not necessary, but when
        # opening it on a modal dialog, we need to make sure the POST request
        # reaches the correct controller
        if self.form_action_urlname:
            context['form_action'] = reverse(self.form_action_urlname,
                                             kwargs={'pk': self.object.id})
        elif self.form_action:
            context['form_action'] = self.form_action

        # Set the title
        context['title'] = self.title

        # Text used in the submit button
        context['submit_text'] = self.submit_text

        return context

    def dispatch(self, request, *args, **kwargs):
        '''
        Custom dispatch method.

        This basically only checks for ownerships of editable/deletable
        objects and return a HttpResponseForbidden response if the user
        is not the owner.
        '''

        # These seem to be necessary for calling get_object
        self.kwargs = kwargs
        self.request = request

        # For new objects, we have to manually load the owner object
        if self.owner_object:
            owner_object = self.owner_object['class'].objects.get(
                pk=kwargs[self.owner_object['pk']])
        else:
            # On CreateViews we don't have an object, so just ignore it
            try:
                owner_object = self.get_object().get_owner_object()
            except AttributeError:
                owner_object = False

        # Nothing to see, please move along
        if owner_object and owner_object.user != self.request.user:
            return HttpResponseForbidden()

        # Dispatch normally
        return super(YamlFormMixin, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        '''
        Pre-process the form, cleaning up the HTML code found in the fields
        given in clean_html. All HTML tags, attributes and styles not in the
        whitelists are stripped from the output, leaving only the text content:

        <table><tr><td>foo</td></tr></table> simply becomes 'foo'
        '''

        for field in self.clean_html:
            setattr(form.instance, field, bleach.clean(getattr(form.instance, field),
                                                       tags=HTML_TAG_WHITELIST,
                                                       attributes=HTML_ATTRIBUTES_WHITELIST,
                                                       styles=HTML_STYLES_WHITELIST,
                                                       strip=True))

        return super(YamlFormMixin, self).form_valid(form)


class YamlDeleteMixin(ModelFormMixin):
    template_name = 'delete.html'

    form_action = ''
    form_action_urlname = ''
    title = ''
    delete_message = ''
    template_name = 'delete.html'

    def get_context_data(self, **kwargs):
        '''
        Set necessary template data to correctly render the form
        '''

        # Call the base implementation first to get a context
        context = super(YamlDeleteMixin, self).get_context_data(**kwargs)

        # CSRF token
        context.update(csrf(self.request))

        # When viewing the page on it's own, this is not necessary, but when
        # opening it on a modal dialog, we need to make sure the POST request
        # reaches the correct controller
        if self.form_action_urlname:
            context['form_action'] = reverse(self.form_action_urlname,
                                             kwargs={'pk': self.object.id})
        elif self.form_action:
            context['form_action'] = self.form_action

        # Set the title
        context['title'] = self.title

        # Additional delete message
        context['delete_message'] = self.delete_message

        return context

    def dispatch(self, request, *args, **kwargs):
        '''
        Custom dispatch method.

        This basically only checks for ownerships of editable/deletable
        objects and return a HttpResponseForbidden response if the user
        is not the owner.
        '''

        # These seem to be necessary if for calling get_object
        self.kwargs = kwargs
        self.request = request
        owner_object = self.get_object().get_owner_object()

        # Nothing to see, please move along
        if owner_object and owner_object.user != self.request.user:
            return HttpResponseForbidden()

        # Dispatch normally
        return super(YamlDeleteMixin, self).dispatch(request, *args, **kwargs)
