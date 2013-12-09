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
import uuid
import pytz
import datetime

from icalendar import Calendar
from icalendar import Alarm
from icalendar import Event
from icalendar.tools import UIDGenerator

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.sites.models import Site

from wger import get_version
from wger.manager.models import Workout
from wger.utils.helpers import next_weekday

logger = logging.getLogger('wger.custom')


'''
Exports workouts and schedules as an iCal file that can be imported to a
calendaring application.

The icalendar module has atrocious documentation, to get the slightest chance
to make this work, looking at the module test files or the official RF is
*really* the only way....

* https://tools.ietf.org/html/rfc5545
* https://github.com/collective/icalendar/tree/master/src/icalendar/tests
'''


@login_required
def export(request, pk):
    '''
    Export the current workout as iCal file
    '''

    # Load objects
    workout = Workout.objects.get(pk=pk)
    site = Site.objects.get(pk=settings.SITE_ID)
    generator = UIDGenerator()

    # Create the calendar
    calendar = Calendar()
    calendar.add('prodid', '-//wger Workout Manager//wger.de//')
    calendar.add('version', get_version())

    # Create the events and set the occurrence for each as weekly
    start_date = workout.creation_date
    end_date = start_date + datetime.timedelta(weeks=request.user.userprofile.workout_duration)
    for day in workout.day_set.all():

        # Make the description of the event with the day's exercises
        description_list = []
        for set in day.set_set.select_related():
            for exercise in set.exercises.select_related():
                description_list.append(unicode(exercise))
        description = ', '.join(description_list) if description_list else day.description

        # Make an event for each weekday
        for weekday in day.day.all():
            event = Event()
            event.add('summary', day.description)
            event.add('description', description)
            event.add('dtstart', next_weekday(start_date, weekday.id - 1))
            event.add('dtend', next_weekday(start_date, weekday.id - 1))
            event.add('rrule', {'freq': 'weekly', 'until': end_date})
            event['uid'] = generator.uid(host_name=site.domain)
            event.add('priority', 5)
            calendar.add_component(event)

    # Create an alarm for the end of the workout
    #alarm = Alarm()
    #alarm.
    #calendar.add_component(alarm)

    # Send the file to the user
    response = HttpResponse(mimetype='text/calendar')
    response['Content-Disposition'] = 'attachment; filename=calendar-{0}.ics'.format(workout.pk)
    response.write(calendar.to_ical())
    return response
