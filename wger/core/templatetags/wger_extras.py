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

# Django
from django import template
from django.conf import settings
from django.db.models import QuerySet
from django.templatetags.static import static
from django.utils.html import strip_spaces_between_tags
from django.utils.safestring import mark_safe
from django.utils.translation import (
    pgettext,
    gettext_lazy as _
)

# wger
from wger.utils.constants import (
    PAGINATION_MAX_TOTAL_PAGES,
    PAGINATION_PAGES_AROUND_CURRENT
)


register = template.Library()


@register.filter(name='get_current_settings')
def get_current_settings(exercise, set_id):
    """
    Does a filter on the sets

    We need to do this here because it's not possible to pass arguments to function in
    the template, and we are only interested on the settings that belong to the current
    set
    """
    return exercise.setting_set.filter(set_id=set_id)


@register.inclusion_tag('tags/render_day.html')
def render_day(day, editable=True):
    """
    Renders a day as it will be displayed in the workout overview
    """
    return {'day': day.canonical_representation,
            'workout': day.training,
            'editable': editable}


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
    return {'page': page,
            'page_range': page_range}


@register.inclusion_tag('tags/render_weight_log.html')
def render_weight_log(log, div_uuid, user=None):
    """
    Renders a weight log series
    """

    return {'log': log,
            'div_uuid': div_uuid,
            'user': user}


@register.inclusion_tag('tags/license-sidebar.html')
def license_sidebar(license, author=None):
    """
    Renders the license notice for exercises
    """

    return {'license': license,
            'author': author}


@register.inclusion_tag('tags/muscles.html')
def render_muscles(muscles=None, muscles_sec=None):
    """
    Renders the given muscles
    """
    if not muscles and not muscles_sec:
        return {"empty": True}

    out_main = []
    if muscles:
        out_main = muscles if isinstance(muscles, (list, tuple, QuerySet)) else [muscles]

    out_sec = []
    if muscles_sec:
        out_sec = muscles_sec if isinstance(muscles_sec, (list, tuple, QuerySet)) else [muscles_sec]

    try:
        front_back = "front" if out_main[0].is_front else "back"
    except IndexError:
        front_back = "front" if out_sec[0].is_front else "back"

    backgrounds = [i.image_url_main for i in out_main] \
        + [i.image_url_secondary for i in out_sec] \
        + [static(f"images/muscles/muscular_system_{front_back}.svg")]

    return {"backgrounds": backgrounds,
            "empty": False}


@register.inclusion_tag('tags/language_select.html', takes_context=True)
def language_select(context, language):
    """
    Renders a link to change the current language.
    """

    return {'language_name': language[1],
            'path': f'images/icons/flag-{language[0]}.svg',
            'i18n_path': context['i18n_path'][language[0]]}


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
    :return: the complete CSS classes
    """
    css = ''
    if not class_name:
        return css

    css += f'{icon_type} fa-{class_name}'

    if fixed_width:
        css += ' fa-fw'
    return mark_safe(css)


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
            return pgettext("weight unit, i.e. grams", "g")
    else:
        if unit == 'kg':
            return _('lb')
        if unit == 'g':
            return pgettext("weight unit, i.e. ounces", "oz")


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


class SpacelessNode(template.base.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        if settings.WGER_SETTINGS['REMOVE_WHITESPACE']:
            return strip_spaces_between_tags(self.nodelist.render(context).strip())
        else:
            return self.nodelist.render(context)


@register.tag
def spaceless_config(parser, token):
    """
    This is django's spaceless tag, copied here to use our configurable
    SpacelessNode
    """
    nodelist = parser.parse(('endspaceless_config',))
    parser.delete_first_token()
    return SpacelessNode(nodelist)
