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
import logging

# Django
from django.contrib.sites.models import Site
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
)
from django.shortcuts import get_object_or_404

# Third Party
from icalendar import (
    Calendar,
    Event,
)
from icalendar.tools import UIDGenerator

# wger
from wger.manager.models import Routine
from wger.version import get_version


logger = logging.getLogger(__name__)
"""
Exports workouts and schedules as an iCal file that can be imported to a
calendaring application.

The icalendar module has atrocious documentation, to get the slightest chance
to make this work, looking at the module test files or the official RF is
*really* the only way....

* https://tools.ietf.org/html/rfc5545
* https://github.com/collective/icalendar/tree/master/src/icalendar/tests
"""


# Helper functions
def get_calendar():
    """
    Creates and returns a calendar object

    :return: Calendar
    """
    calendar = Calendar()
    calendar.add('prodid', '-//wger Workout Manager//wger.de//')
    calendar.add('version', get_version())
    return calendar


def get_events_workout(calendar, routine: Routine):
    """
    Creates all necessary events from the given workout and adds them to
    the calendar.
    """

    generator = UIDGenerator()
    site = Site.objects.get_current()

    for day_data in routine.date_sequence:
        if day_data.day is None or day_data.day.is_rest:
            continue

        event = Event()
        event.add('summary', day_data.day.name)
        event.add('description', day_data.day.description)
        event.add('dtstart', day_data.date)
        event.add('dtend', day_data.date)
        event['uid'] = generator.uid(host_name=site.domain)
        event.add('priority', 5)
        calendar.add_component(event)


# Views
def export(request, pk):
    """
    Export the current workout as an iCal file
    """

    if request.user.is_anonymous:
        return HttpResponseForbidden()

    routine = get_object_or_404(Routine, pk=pk, user=request.user)

    # Create the calendar
    calendar = get_calendar()

    # Create the events and add them to the calendar
    get_events_workout(calendar, routine)

    # Send the file to the user
    response = HttpResponse(content_type='text/calendar')
    response.write(calendar.to_ical())
    response['Content-Length'] = len(response.content)
    return response
