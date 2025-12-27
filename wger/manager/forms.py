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
from django import forms
from django.utils.translation import gettext_lazy as _

# wger
from wger.core.models import RepetitionUnit
from wger.exercises.models import Translation
from wger.manager.models import (
    Day,
    Routine,
    Slot,
    SlotEntry,
)


class TimedExerciseForm(forms.Form):
    """
    Form for creating a timed exercise (e.g., 60 seconds plank)
    """

    routine = forms.ModelChoiceField(
        queryset=Routine.objects.none(),
        label=_('Routine'),
        help_text=_('Select the routine to add this exercise to'),
    )

    day = forms.ModelChoiceField(
        queryset=Day.objects.none(),
        label=_('Day'),
        help_text=_('Select the day within the routine'),
        required=False,
    )

    exercise = forms.ModelChoiceField(
        queryset=Translation.objects.none(),
        label=_('Exercise'),
        help_text=_('Select the exercise (e.g., Plank, Wall Sit)'),
    )

    duration = forms.IntegerField(
        min_value=1,
        max_value=3600,
        label=_('Duration'),
        help_text=_('How long should the exercise last?'),
    )

    unit = forms.ModelChoiceField(
        queryset=RepetitionUnit.objects.filter(unit_type='TIME'),
        label=_('Time Unit'),
        help_text=_('Seconds or Minutes'),
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter routines to only show user's routines
        self.fields['routine'].queryset = Routine.objects.filter(user=user)

        # Get exercises that are in the user's routines
        from wger.manager.models import SlotEntry
        user_exercise_ids = SlotEntry.objects.filter(
            slot__day__routine__user=user
        ).values_list('exercise_id', flat=True).distinct()

        # Show only exercises from user's routines (English translations)
        self.fields['exercise'].queryset = Translation.objects.filter(
            language_id=2,
            exercise_id__in=user_exercise_ids
        ).select_related('exercise').order_by('name')

    def clean(self):
        cleaned_data = super().clean()
        routine = cleaned_data.get('routine')
        day = cleaned_data.get('day')

        # If day is provided, make sure it belongs to the selected routine
        if day and routine and day.routine != routine:
            raise forms.ValidationError(_('The selected day does not belong to the selected routine.'))

        return cleaned_data
