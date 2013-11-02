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

from wger.exercises.models import Exercise
from wger.utils.constants import PAGINATION_MAX_TOTAL_PAGES
from wger.utils.constants import PAGINATION_PAGES_AROUND_CURRENT

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


@register.filter(name='get_active_exercises')
def get_active_exercises(category, languages):
    '''
    Filter out pending exercises and not in the given languages
    '''
    return category.exercise_set.filter(status__in=Exercise.EXERCISE_STATUS_OK,
                                        language__in=languages)


@register.inclusion_tag('tags/render_day.html')
def render_day(day):
    '''
    Renders a day as it will be displayed in the workout overview
    '''
    return {'day':     day,
            'workout': day.training}


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
    return {'page':       page,
            'page_range': page_range}


@register.inclusion_tag('tags/render_weight_log.html')
def render_weight_log(log, div_uuid):
    '''
    Renders a weight log series
    '''

    return {'log': log,
            'div_uuid': div_uuid}


@register.inclusion_tag('tags/yaml_form_element.html')
def yaml_form_field(field, css_class='ym-fbox-text'):
    '''
    Renders a form field in a <tr> with all necessary CSS
    '''

    return {'field':     field,
            'css_class': css_class}


@register.inclusion_tag('tags/cc-by-sa-sidebar.html')
def cc_by_sa_sidebar(language):
    '''
    Renders the Creative Commons license notice
    '''

    return {'language': language}


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
