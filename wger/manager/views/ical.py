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

import six
import logging
import datetime

from icalendar import Calendar
from icalendar import Event
from icalendar.tools import UIDGenerator

from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings
from django.contrib.sites.models import Site

from wger import get_version
from wger.manager.models import Workout, Schedule
from wger.utils.helpers import next_weekday, check_token


logger = logging.getLogger(__name__)


'''
Exports workouts and schedules as an iCal file that can be imported to a
calendaring application.

The icalendar module has atrocious documentation, to get the slightest chance
to make this work, looking at the module test files or the official RF is
*really* the only way....

* https://tools.ietf.org/html/rfc5545
* https://github.com/collective/icalendar/tree/master/src/icalendar/tests
'''


# Helper functions
def get_calendar():
    '''
    Creates and returns a calendar object

    :return: Calendar
    '''
    calendar = Calendar()
    calendar.add('prodid', '-//wger Workout Manager//wger.de//')
    calendar.add('version', get_version())
    return calendar


def get_events_workout(calendar, workout, duration, start_date=None):
    '''
    Creates all necessary events from the given workout and adds them to
    the calendar. Each event's occurrence ist set to weekly (one event for
    each training day).

    :param calendar: calendar to add events to
    :param workout: Workout
    :param duration: duration in weeks
    :param start_date: start date, default: profile default
    :return: None
    '''

    start_date = start_date if start_date else workout.creation_date
    end_date = start_date + datetime.timedelta(weeks=duration)
    generator = UIDGenerator()
    site = Site.objects.get(pk=settings.SITE_ID)

    for day in workout.canonical_representation['day_list']:

        # Make the description of the event with the day's exercises
        description_list = []
        for set in day['set_list']:
            for exercise in set['exercise_list']:
                description_list.append(six.text_type(exercise['obj']))
        description = ', '.join(description_list) if description_list else day['obj'].description

        # Make an event for each weekday
        for weekday in day['days_of_week']['day_list']:
            event = Event()
            event.add('summary', day['obj'].description)
            event.add('description', description)
            event.add('dtstart', next_weekday(start_date, weekday.id - 1))
            event.add('dtend', next_weekday(start_date, weekday.id - 1))
            event.add('rrule', {'freq': 'weekly', 'until': end_date})
            event['uid'] = generator.uid(host_name=site.domain)
            event.add('priority', 5)
            calendar.add_component(event)


# Views
def export(request, pk, uidb64=None, token=None):
    '''
    Export the current workout as an iCal file
    '''

    # Load the workout
    if uidb64 is not None and token is not None:
        if check_token(uidb64, token):
            workout = get_object_or_404(Workout, pk=pk)
        else:
            return HttpResponseForbidden()
    else:
        if request.user.is_anonymous():
            return HttpResponseForbidden()
        workout = get_object_or_404(Workout, pk=pk, user=request.user)

    # Create the calendar
    calendar = get_calendar()

    # Create the events and add them to the calendar
    get_events_workout(calendar, workout, workout.user.userprofile.workout_duration)

    # Send the file to the user
    response = HttpResponse(content_type='text/calendar')
    response['Content-Disposition'] = \
        'attachment; filename=Calendar-workout-{0}.ics'.format(workout.pk)
    response.write(calendar.to_ical())
    response['Content-Length'] = len(response.content)
    return response


def export_schedule(request, pk, uidb64=None, token=None):
    '''
    Export the current schedule as an iCal file
    '''

    # Load the schedule
    if uidb64 is not None and token is not None:
        if check_token(uidb64, token):
            schedule = get_object_or_404(Schedule, pk=pk)
        else:
            return HttpResponseForbidden()
    else:
        if request.user.is_anonymous():
            return HttpResponseForbidden()
        schedule = get_object_or_404(Schedule, pk=pk, user=request.user)

    # Create the calendar
    calendar = get_calendar()

    # Create the events and add them to the calendar
    start_date = datetime.date.today()
    for step in schedule.schedulestep_set.all():
        get_events_workout(calendar, step.workout, step.duration, start_date)
        start_date = start_date + datetime.timedelta(weeks=step.duration)

    # Send the file to the user
    response = HttpResponse(content_type='text/calendar')
    response['Content-Disposition'] = \
        'attachment; filename=Calendar-schedule-{0}.ics'.format(schedule.pk)
    response.write(calendar.to_ical())
    response['Content-Length'] = len(response.content)
    return response
