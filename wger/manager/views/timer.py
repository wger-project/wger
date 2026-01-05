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
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import (
    redirect,
    render,
)
from django.utils.translation import gettext as _

# wger
from wger.manager.forms import TimedExerciseForm
from wger.manager.models import (
    Day,
    RepetitionsConfig,
    Slot,
    SlotEntry,
)


def timer_demo(request):
    """
    Demo page for the countdown timer component.
    This page showcases the timer functionality for timed exercises.
    """
    return render(request, 'timer_demo.html')


@login_required
def add_timed_exercise(request):
    """
    Form page for adding a timed exercise to a routine.
    Allows users to select an exercise and set a duration in seconds or minutes.
    """
    if request.method == 'POST':
        form = TimedExerciseForm(request.user, request.POST)
        if form.is_valid():
            routine = form.cleaned_data['routine']
            day = form.cleaned_data['day']
            exercise = form.cleaned_data['exercise']
            duration = form.cleaned_data['duration']
            unit = form.cleaned_data['unit']

            # If no day selected, create one or use the first day
            if not day:
                day = routine.days.first()
                if not day:
                    # Create a new day
                    day = Day.objects.create(
                        routine=routine,
                        name=_('Timed Exercises'),
                        order=1,
                    )

            # Get or create a slot for this day
            slot = day.slots.first()
            if not slot:
                slot = Slot.objects.create(
                    day=day,
                    order=1,
                )

            # Create the slot entry with the time-based unit
            # exercise is a Translation object, we need the actual Exercise
            slot_entry = SlotEntry.objects.create(
                slot=slot,
                exercise=exercise.exercise,  # Get the Exercise from Translation
                repetition_unit=unit,
                order=slot.entries.count() + 1,
            )

            # Create the repetitions config with the duration
            RepetitionsConfig.objects.create(
                slot_entry=slot_entry,
                iteration=1,
                value=duration,
            )

            messages.success(
                request,
                _('Timed exercise added: %(exercise)s for %(duration)s %(unit)s') % {
                    'exercise': exercise.name,
                    'duration': duration,
                    'unit': unit.name,
                }
            )

            return redirect('manager:routine:view', pk=routine.pk)
    else:
        form = TimedExerciseForm(request.user)

    return render(request, 'add_timed_exercise.html', {'form': form})


@login_required
def get_days_for_routine(request, routine_id):
    """
    AJAX endpoint to get days for a specific routine.
    Used to dynamically populate the day dropdown when routine changes.
    """
    days = Day.objects.filter(routine_id=routine_id, routine__user=request.user)
    data = [{'id': day.id, 'name': day.name or f'Day {day.order}'} for day in days]
    return JsonResponse(data, safe=False)
