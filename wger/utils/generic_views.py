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
import bleach

from django.utils.translation import ugettext_lazy
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.context_processors import csrf
from django.views.generic.edit import ModelFormMixin
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponseForbidden

from wger.utils.constants import (
    HTML_TAG_WHITELIST,
    HTML_ATTRIBUTES_WHITELIST,
    HTML_STYLES_WHITELIST
)


logger = logging.getLogger(__name__)


class WgerPermissionMixin(object):
    '''
    Custom permission mixim

    This simply checks that the user has the given permissions to access a
    resource and makes writing customized generic views easier.
    '''

    permission_required = False
    '''
    The name of the permission required to access this class.

    This can be a string or a tuple, in the latter case having any of the permissions
    listed is enough to access the resource
    '''

    login_required = False
    '''
    Set to True to restrict view to logged in users
    '''

    def dispatch(self, request, *args, **kwargs):
        '''
        Check permissions and dispatch
        '''

        if self.login_required or self.permission_required:
            if not request.user.is_authenticated():
                return HttpResponseRedirect(reverse_lazy('core:user:login')
                                            + '?next={0}'.format(request.path))

            if self.permission_required:
                has_permission = False
                if isinstance(self.permission_required, tuple):
                    for permission in self.permission_required:
                        if request.user.has_perm(permission):
                            has_permission = True
                elif request.user.has_perm(self.permission_required):
                    has_permission = True

                if not has_permission:
                    return HttpResponseForbidden('You are not allowed to access this object')

        # Dispatch normally
        return super(WgerPermissionMixin, self).dispatch(request, *args, **kwargs)


class WgerFormMixin(ModelFormMixin, WgerPermissionMixin):
    template_name = 'form.html'

    custom_js = ''
    '''
    Custom javascript to be executed.
    '''

    form_action = ''
    form_action_urlname = ''
    sidebar = ''
    '''
    Name of a template that will be included in the sidebar
    '''

    title = ''
    '''
    Title used in the form
    '''

    owner_object = False
    '''
    The object that holds the owner information. This only needs to be set if
    the model doesn't provide a get_owner_object() method
    '''

    submit_text = ugettext_lazy('Save')
    '''
    Text used in the submit button, default _('save')
    '''

    clean_html = ()
    '''
    List of form fields that should be passed to bleach to clean the html
    '''

    messages = ''
    '''
    A message to display on sucess
    '''

    def get_context_data(self, **kwargs):
        '''
        Set necessary template data to correctly render the form
        '''

        # Call the base implementation first to get a context
        context = super(WgerFormMixin, self).get_context_data(**kwargs)

        # CSRF token
        context.update(csrf(self.request))

        context['sidebar'] = self.sidebar
        context['form_fields'] = kwargs['form']

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

        # Template to extend. For AJAX requests we don't need the rest of the
        # template, only the form
        context['extend_template'] = 'base_empty.html' if self.request.is_ajax() else 'base.html'

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
            return HttpResponseForbidden('You are not allowed to access this object')

        # Dispatch normally
        return super(WgerFormMixin, self).dispatch(request, *args, **kwargs)

    def get_messages(self):
        '''
        Getter for success message. Can be overwritten to e.g. to provide the
        name of the object.
        '''
        return self.messages

    def form_invalid(self, form):
        '''
        Log form errors to the console
        '''
        logger.debug(form.errors)
        return super(WgerFormMixin, self).form_invalid(form)

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

        if self.get_messages():
            messages.success(self.request, self.get_messages())

        return super(WgerFormMixin, self).form_valid(form)


class WgerDeleteMixin(ModelFormMixin, WgerPermissionMixin):
    form_action = ''
    form_action_urlname = ''
    title = ''
    delete_message = ''
    template_name = 'delete.html'
    messages = ''

    def get_context_data(self, **kwargs):
        '''
        Set necessary template data to correctly render the form
        '''

        # Call the base implementation first to get a context
        context = super(WgerDeleteMixin, self).get_context_data(**kwargs)

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

        # Template to extend. For AJAX requests we don't need the rest of the
        # template, only the form
        context['extend_template'] = 'base_empty.html' if self.request.is_ajax() else 'base.html'

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
        return super(WgerDeleteMixin, self).dispatch(request, *args, **kwargs)

    def get_messages(self):
        '''
        Getter for success message. Can be overwritten to e.g. to provide the
        name of the object.
        '''
        return self.messages

    def delete(self, request, *args, **kwargs):
        '''
        Show a message on successful delete
        '''
        if self.get_messages():
            messages.success(request, self.get_messages())
        return super(WgerDeleteMixin, self).delete(request, *args, **kwargs)


class TextTemplateView(TemplateView):
    '''
    A regular templateView that sets the mime type as text/plain
    '''
    def render_to_response(self, context, **response_kwargs):
        response_kwargs['content_type'] = 'text/plain'
        return super(TextTemplateView, self).render_to_response(context, **response_kwargs)


class WebappManifestView(TemplateView):
    '''
    A regular templateView that sets the mime type as application/x-web-app-manifest+json

    This is used in the mozilla market place
    '''
    template_name = 'manifest.webapp'

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['content_type'] = 'application/x-web-app-manifest+json'
        return super(WebappManifestView, self).render_to_response(context, **response_kwargs)
