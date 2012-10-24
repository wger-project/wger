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

from django.core.context_processors import csrf
from django.views.generic.edit import ModelFormMixin

class YamlFormMixin(ModelFormMixin):
    template_name = 'form.html'
    
    active_tab = ''
    form_fields = []
    active_tab = ''
    select_lists = []
    static_files = []
    custom_js = ''
    form_action = ''
    title = ''
    
    def get_context_data(self, **kwargs):
        '''
        Set necessary template data to correctly render the form
        '''
        
        # Call the base implementation first to get a context
        context = super(YamlFormMixin, self).get_context_data(**kwargs)
        
        # CSRF token
        context.update(csrf(self.request))
        
        # Active tab, on top navigation
        context['active_tab'] = self.active_tab
    
        # Custom order for form fields. The list comprehension is to avoid
        # weird problems with django's template when accessing the fields with "form.fieldname"
        if self.form_fields:
            context['form_fields'] = [kwargs['form'][i] for i in self.form_fields]
        
        # Use the the order as defined in the model
        else:
            context['form_fields'] = kwargs['form']
        
        # Drop down lists get a special CSS class, there doesn't seem to be
        # another way of detecting them
        context['select_lists'] = self.select_lists
    
        # List of additional JS static files, will be passed to {% static %}
        context['static_files'] = self.static_files
       
        # Custom JS code on form (autocompleter, editor, etc.)
        context['custom_js'] = self.custom_js
        
        # When viewing the page on it's own, this is not necessary, but when
        # opening it on a modal dialog, we need to make sure the POST request
        # reaches the correct controller
        context['form_action'] = self.form_action
        
        # Set the title
        context['title'] = self.title
        
        return context
        
class YamlDeleteMixin(ModelFormMixin):
    template_name = 'delete.html'
    
    active_tab = ''
    form_action = ''
    title = ''
    
    def get_context_data(self, **kwargs):
        '''
        Set necessary template data to correctly render the form
        '''
        
        # Call the base implementation first to get a context
        context = super(YamlDeleteMixin, self).get_context_data(**kwargs)
        
        # CSRF token
        context.update(csrf(self.request))
        
        # Active tab, on top navigation
        context['active_tab'] = self.active_tab
    
        # When viewing the page on it's own, this is not necessary, but when
        # opening it on a modal dialog, we need to make sure the POST request
        # reaches the correct controller
        context['form_action'] = self.form_action
        
        # Set the title
        context['title'] = self.title
        
        return context
