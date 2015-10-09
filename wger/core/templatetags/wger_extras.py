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

from django import template
from django.forms.widgets import CheckboxInput, ClearableFileInput
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext
from django.conf import settings

from wger.utils.constants import PAGINATION_MAX_TOTAL_PAGES, PAGINATION_PAGES_AROUND_CURRENT

register = template.Library()


@register.filter(name='get_current_settings')
def get_current_settings(exercise, set_id):
    '''
    Does a filter on the sets

    We need to do this here because it's not possible to pass arguments to function in
    the template, and we are only interested on the settings that belong to the current
    set
    '''
    return exercise.setting_set.filter(set_id=set_id)


@register.inclusion_tag('tags/render_day.html')
def render_day(day, editable=True):
    '''
    Renders a day as it will be displayed in the workout overview
    '''
    return {'day': day.canonical_representation,
            'workout': day.training,
            'editable': editable}


@register.inclusion_tag('tags/pagination.html')
def pagination(paginator, page):
    '''
    Renders the necessary links to paginating a long list
    '''

    # For very long lists (e.g. the English ingredient with more than 8000 items)
    # we muck around here to remove the pages not inmediately 'around' the current
    # one, otherwise we end up with a useless block with 300 pages.
    if paginator.num_pages > PAGINATION_MAX_TOTAL_PAGES:

        start_page = page.number - PAGINATION_PAGES_AROUND_CURRENT
        for i in range(page.number - PAGINATION_PAGES_AROUND_CURRENT, page.number + 1):
            if i > 0:
                start_page = i
                break

        end_page = page.number + PAGINATION_PAGES_AROUND_CURRENT
        for i in range(page.number, page.number + PAGINATION_PAGES_AROUND_CURRENT):
            if i > paginator.num_pages:
                end_page = i
                break

        page_range = range(start_page, end_page)
    else:
        page_range = paginator.page_range

    # Set the template variables
    return {'page': page,
            'page_range': page_range}


@register.inclusion_tag('tags/render_weight_log.html')
def render_weight_log(log, div_uuid, user=None):
    '''
    Renders a weight log series
    '''

    return {'log': log,
            'div_uuid': div_uuid,
            'user': user}


@register.inclusion_tag('tags/license-sidebar.html')
def license_sidebar(license, author=None):
    '''
    Renders the license notice for exercises
    '''

    return {'license': license,
            'author': author}


@register.inclusion_tag('tags/language_select.html', takes_context=True)
def language_select(context, language):
    '''
    Renders a link to change the current language.
    '''

    return {'language_name': language[1],
            'path': 'images/icons/flag-{0}.svg'.format(language[0]),
            'i18n_path': context['i18n_path'][language[0]]}


@register.filter
def get_item(dictionary, key):
    '''
    Allows to access a specific key in a dictionary in a template
    '''
    return dictionary.get(key)


@register.simple_tag
def auto_link_css(flavour='full', css=''):
    '''
    Adds the appropriate classes to a sidebar link depending on the site version

    :param flavour: flavour of the site: 'mobile' or 'full'
    :param css: the CSS class, if any, of the link
    :return: the complete CSS classes, wrapped in class="foo"
    '''
    css = css + ' btn btn-default btn-block' if flavour == 'mobile' else css
    return 'class="{0}"'.format(css)


@register.simple_tag
def trans_weight_unit(unit, user=None):
    '''
    Returns the correct (translated) weight unit

    :param unit: the weight unit. Allowed values are 'kg' and 'g'
    :param user: the user object, needed to access the profile. If this evaluates
                 to False, metric is used
    :return: translated unit
    '''
    if not user or user.userprofile.use_metric:
        if unit == 'kg':
            return _('kg')
        if unit == 'g':
            return pgettext("weight unit, i.e. grams", "g")
    else:
        if unit == 'kg':
            return _('lb')
        if unit == 'g':
            return pgettext("weight unit, i.e. ounces", "oz")


@register.filter
def format_username(user):
    '''
    Formats the username according to the information available
    '''
    if user.get_full_name():
        return user.get_full_name()
    elif user.email:
        return user.email
    else:
        return user.username


class SpacelessNode(template.base.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        if settings.WGER_SETTINGS['REMOVE_WHITESPACE']:
            from django.utils.html import strip_spaces_between_tags
            return strip_spaces_between_tags(self.nodelist.render(context).strip())
        else:
            return self.nodelist.render(context)


@register.tag
def spaceless_config(parser, token):
    '''
    This is django's spaceless tag, copied here to use our configurable
    SpacelessNode
    '''
    nodelist = parser.parse(('endspaceless_config',))
    parser.delete_first_token()
    return SpacelessNode(nodelist)


#
# Form utils
#
@register.filter(name='form_field_add_css')
def form_field_add_css(field, css):
    '''
    Adds a CSS class to a form field. This is needed among other places for
    bootstrap 3, which needs a 'form-control' class in the field itself
    '''
    return field.as_widget(attrs={"class": css})


@register.filter(name='is_checkbox')
def is_checkbox(field):
    '''
    Tests if a field element is a checkbox, as it needs to be handled slightly different

    :param field: a form field
    :return: boolen
    '''
    return field.field.widget.__class__.__name__ == CheckboxInput().__class__.__name__


@register.filter(name='is_fileupload')
def is_fileupload(field):
    '''
    Tests if a field element is a file upload, as it needs to be handled slightly different

    :param field: a form field
    :return: boolen
    '''
    return field.field.widget.__class__.__name__ == ClearableFileInput().__class__.__name__


@register.inclusion_tag('tags/render_form_element.html')
def render_form_field(field):
    '''
    Renders a form field with all necessary labels, help texts and labels
    within 'form-group'.

    See bootstrap documentation for details: http://getbootstrap.com/css/#forms
    '''

    return {'field': field}


@register.inclusion_tag('tags/render_form_submit.html')
def render_form_submit(save_text='Save', button_class='default'):
    """
    Comfort function that renders a submit button with all necessary HTML
    and CSS

    :param save_text: the text to use on the submit button
    :param button_class: CSS class to apply to the button, default 'default'
    """
    if button_class in ('default',
                        'primary',
                        'success',
                        'info',
                        'warning',
                        'danger',
                        'link'):
        button_class = button_class
    else:
        button_class = 'default'

    return {'save_text': save_text,
            'button_class': button_class}


@register.inclusion_tag('tags/render_form_errors.html')
def render_form_errors(form):
    """
    Renders the non-field errors of a form with all necessary HTML and CSS
    (non-field errors refer to errors that can't be associated to any single
    field)

    :param form: the form object
    """
    return {'form': form}


@register.inclusion_tag('tags/render_form_fields.html')
def render_form_fields(form, submit_text='Save', show_save=True):
    '''
    Comfort function that renders all fields in a form, as well as the submit
    button

    Internally it simply calls the other table_form_* functions and will render
    the fields in the order they were defined. If you want to change this, you
    need to call table_form_field for each field yourself. This function will
    also render a hidden field with a CSRF token, so be sure to pass it to the
    template.

    It is still necessary to enclose its output in <form> tags!

    :param form: the form to be rendered
    :param save_text: the text to use on the submit button
    '''

    return {'form': form,
            'show_save': show_save,
            'submit_text': submit_text}
