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
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import models
from django.forms import (
    ModelChoiceField,
    ModelForm,
)
from django.urls import reverse
from django.utils.translation import (
    gettext as _,
    gettext_lazy,
)
from django.views.generic import (
    CreateView,
    DeleteView,
    UpdateView,
)

# wger
from wger.manager.models import (
    Schedule,
    ScheduleStep,
    Workout,
)
from wger.utils.generic_views import (
    WgerDeleteMixin,
    WgerFormMixin,
)


logger = logging.getLogger(__name__)


class StepCreateView(WgerFormMixin, CreateView, PermissionRequiredMixin):
    """
    Creates a new workout schedule
    """

    model = ScheduleStep
    fields = ('schedule', 'workout', 'duration', 'order')
    title = gettext_lazy('Add workout')

    def get_form_class(self):
        """
        The form can only show the workouts belonging to the user.

        This is defined here because only at this point during the request
        have we access to the current user
        """

        class StepForm(ModelForm):
            workout = ModelChoiceField(queryset=Workout.objects.filter(user=self.request.user))

            class Meta:
                model = ScheduleStep
                exclude = ('order', 'schedule')

        return StepForm

    def get_success_url(self):
        return reverse('manager:schedule:view', kwargs={'pk': self.kwargs['schedule_pk']})

    def form_valid(self, form):
        """Set the schedule and the order"""

        schedule = Schedule.objects.get(pk=self.kwargs['schedule_pk'])

        max_order = schedule.schedulestep_set.all().aggregate(models.Max('order'))
        form.instance.schedule = schedule
        form.instance.order = (max_order['order__max'] or 0) + 1
        return super(StepCreateView, self).form_valid(form)


class StepEditView(WgerFormMixin, UpdateView, PermissionRequiredMixin):
    """
    Generic view to update an existing schedule step
    """

    model = ScheduleStep
    title = gettext_lazy('Edit workout')

    def get_form_class(self):
        """
        The form can only show the workouts belonging to the user.

        This is defined here because only at this point during the request
        have we access to the current user
        """

        class StepForm(ModelForm):
            workout = ModelChoiceField(queryset=Workout.objects.filter(user=self.request.user))

            class Meta:
                model = ScheduleStep
                exclude = ('order', 'schedule')

        return StepForm

    def get_success_url(self):
        return reverse('manager:schedule:view', kwargs={'pk': self.object.schedule_id})


class StepDeleteView(WgerDeleteMixin, DeleteView, PermissionRequiredMixin):
    """
    Generic view to delete a schedule step
    """

    model = ScheduleStep
    messages = gettext_lazy('Successfully deleted')

    def get_success_url(self):
        return reverse('manager:schedule:view', kwargs={'pk': self.object.schedule.id})

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        context = super(StepDeleteView, self).get_context_data(**kwargs)
        context['title'] = _('Delete {0}?').format(self.object)
        return context
