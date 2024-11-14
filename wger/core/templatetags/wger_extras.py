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
from collections.abc import Iterable

# Django
from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.utils.translation import (
    gettext_lazy as _,
    pgettext,
)

# wger
from wger.core.tests.base_testcase import get_reverse
from wger.manager.models import Day
from wger.utils.constants import (
    PAGINATION_MAX_TOTAL_PAGES,
    PAGINATION_PAGES_AROUND_CURRENT,
)
from wger.utils.language import get_language_data


register = template.Library()


@register.filter(name='get_current_settings')
def get_current_settings(exercise, set_id):
    """
    Does a filter on the sets

    We need to do this here because it's not possible to pass arguments to function in
    the template, and we are only interested on the settings that belong to the current
    set
    """
    return exercise.exercise_base.setting_set.filter(set_id=set_id)


@register.inclusion_tag('tags/render_day.html')
def render_day(day: Day, editable=True):
    """
    Renders a day as it will be displayed in the workout overview
    """
    return {
        'day': day,
        'workout': day.training,
        'editable': editable,
    }


@register.inclusion_tag('tags/pagination.html')
def pagination(paginator, page):
    """
    Renders the necessary links to paginating a long list
    """

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
    return {'page': page, 'page_range': page_range}


@register.inclusion_tag('tags/muscles.html')
def render_muscles(muscles=None, muscles_sec=None):
    """
    Renders the given muscles
    """
    out = {'backgrounds': []}
    if not muscles and not muscles_sec:
        return out

    out_main = []
    if muscles:
        out_main = muscles if isinstance(muscles, Iterable) else [muscles]

    out_secondary = []
    if muscles_sec:
        out_secondary = muscles_sec if isinstance(muscles_sec, Iterable) else [muscles_sec]

    if out_main:
        front_back = 'front' if out_main[0].is_front else 'back'
    else:
        front_back = 'front' if out_secondary[0].is_front else 'back'

    out['backgrounds'] = (
        [i.image_url_main for i in out_main]
        + [i.image_url_secondary for i in out_secondary]
        + [static(f'images/muscles/muscular_system_{front_back}.svg')]
    )

    return out


@register.inclusion_tag('tags/language_select.html', takes_context=True)
def language_select(context, language):
    """
    Renders a link to change the current language.
    """

    return {**get_language_data(language), 'i18n_path': context['i18n_path'][language[0]]}


@register.filter
def get_item(dictionary, key):
    """
    Allows to access a specific key in a dictionary in a template
    """
    return dictionary.get(key)


@register.filter
def minus(a, b):
    """
    Simple function that subtracts two values in a template
    """
    return a - b


@register.filter
def is_positive(a):
    """
    Simple function that checks whether one value is bigger than the other
    """
    return a > 0


@register.simple_tag
def fa_class(class_name='', icon_type='fas', fixed_width=True):
    """
    Helper function to help add font awesome classes to elements

    :param class_name: the CSS class name, without the "fa-" prefix
    :param fixed_width: toggle for fixed icon width
    :param icon_type; icon type (
    :return: the complete CSS classes
    """
    css = ''
    if not class_name:
        return css

    css += f'{icon_type} fa-{class_name}'

    if fixed_width:
        css += ' fa-fw'
    return mark_safe(css)


@register.inclusion_tag('tags/modal_link.html')
def modal_link(url: str, text: str, css_class='btn btn-success btn-sm'):
    return {'url': get_reverse(url), 'text': text, 'css_class': css_class}


@register.simple_tag
def trans_weight_unit(unit, user=None):
    """
    Returns the correct (translated) weight unit

    :param unit: the weight unit. Allowed values are 'kg' and 'g'
    :param user: the user object, needed to access the profile. If this evaluates
                 to False, metric is used
    :return: translated unit
    """
    if not user or user.userprofile.use_metric:
        if unit == 'kg':
            return _('kg')
        if unit == 'g':
            return pgettext('weight unit, i.e. grams', 'g')
    else:
        if unit == 'kg':
            return _('lb')
        if unit == 'g':
            return pgettext('weight unit, i.e. ounces', 'oz')


@register.filter
def format_username(user):
    """
    Formats the username according to the information available
    """
    if user.get_full_name():
        return user.get_full_name()
    elif user.email:
        return user.email
    else:
        return user.username
