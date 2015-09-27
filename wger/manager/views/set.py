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

from django.forms.models import modelformset_factory, inlineformset_factory
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.auth.decorators import login_required

from wger.manager.models import (
    Day,
    Set,
    Setting
)
from wger.exercises.models import Exercise
from wger.manager.forms import (
    SetForm,
    SetFormMobile,
    SettingForm
)
from wger.utils.language import load_item_languages
from wger.config.models import LanguageConfig

logger = logging.getLogger(__name__)


# ************************
# Set functions
# ************************
SETTING_FORMSET_FIELDS = ('reps', 'weight')

SettingFormset = modelformset_factory(Setting,
                                      form=SettingForm,
                                      fields=SETTING_FORMSET_FIELDS,
                                      can_delete=False,
                                      can_order=False,
                                      extra=1)


@login_required
def create(request, day_pk):
    '''
    Creates a new set. This view handles both the set form and the corresponding
    settings formsets
    '''
    day = get_object_or_404(Day, pk=day_pk)
    if day.get_owner_object().user != request.user:
        return HttpResponseForbidden()

    # Select the correct form depending on the flavour of the request
    if request.flavour == 'mobile':
        form_class = SetFormMobile
    else:
        form_class = SetForm

    context = {}
    formsets = []
    form = form_class(initial={'sets': Set.DEFAULT_SETS})

    # For the mobile dropdown list we need to manually filter the exercises
    # by language and status
    if request.flavour == 'mobile':
        languages = load_item_languages(LanguageConfig.SHOW_ITEM_EXERCISES)
        form.fields['exercise_list'].queryset = Exercise.objects.accepted() \
                                                        .filter(language__in=languages)

    # If the form and all formsets validate, save them
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            for exercise in form.cleaned_data['exercises']:
                formset = SettingFormset(request.POST,
                                         queryset=Setting.objects.none(),
                                         prefix='exercise{0}'.format(exercise.id))
                formsets.append({'exercise': exercise, 'formset': formset})
        all_valid = True

        for formset in formsets:
            if not formset['formset'].is_valid():
                all_valid = False

        if form.is_valid() and all_valid:
            # Manually take care of the order, TODO: better move this to the model
            max_order = day.set_set.select_related().aggregate(models.Max('order'))
            form.instance.order = (max_order['order__max'] or 0) + 1
            form.instance.exerciseday = day
            set_obj = form.save()

            for formset in formsets:
                instances = formset['formset'].save(commit=False)
                for instance in instances:
                    instance.set = set_obj
                    instance.order = 1
                    instance.exercise = formset['exercise']
                    instance.save()

            return HttpResponseRedirect(reverse('manager:workout:view',
                                        kwargs={'pk': day.get_owner_object().id}))
        else:
            logger.debug(form.errors)

    # Other context we need
    context['form'] = form
    context['day'] = day
    context['max_sets'] = Set.MAX_SETS
    context['formsets'] = formsets
    context['form_action'] = reverse('manager:set:add', kwargs={'day_pk': day_pk})
    context['extend_template'] = 'base_empty.html' if request.is_ajax() else 'base.html'
    return render(request, 'set/add.html', context)


@login_required
def get_formset(request, exercise_pk, reps=Set.DEFAULT_SETS):
    '''
    Returns a formset. This is then rendered inside the new set template
    '''
    exercise = Exercise.objects.get(pk=exercise_pk)
    SettingFormSet = inlineformset_factory(Set,
                                           Setting,
                                           can_delete=False,
                                           extra=int(reps),
                                           fields=SETTING_FORMSET_FIELDS)
    formset = SettingFormSet(queryset=Setting.objects.none(),
                             prefix='exercise{0}'.format(exercise_pk))

    return render(request,
                  "set/formset.html",
                  {'formset': formset,
                   'exercise': exercise})


@login_required
def delete(request, pk):
    '''
    Deletes the given set
    '''

    # Load the set
    set_obj = get_object_or_404(Set, pk=pk)

    # Check if the user is the owner of the object
    if set_obj.get_owner_object().user == request.user:
        set_obj.delete()
        return HttpResponseRedirect(reverse('manager:workout:view',
                                            kwargs={'pk': set_obj.get_owner_object().id}))
    else:
        return HttpResponseForbidden()


@login_required
def edit(request, pk):
    '''
    Edit a set (its settings actually)
    '''
    set_obj = get_object_or_404(Set, pk=pk)
    if set_obj.get_owner_object().user != request.user:
        return HttpResponseForbidden()

    formsets = []
    for exercise in set_obj.exercises.all():
        queryset = Setting.objects.filter(set=set_obj, exercise=exercise)
        formset = SettingFormset(queryset=queryset, prefix='exercise{0}'.format(exercise.id))
        formsets.append({'exercise': exercise, 'formset': formset})

    if request.method == "POST":
        formsets = []
        for exercise in set_obj.exercises.all():
            formset = SettingFormset(request.POST,
                                     prefix='exercise{0}'.format(exercise.id))
            formsets.append({'exercise': exercise, 'formset': formset})

        # If all formsets validate, save them
        all_valid = True
        for formset in formsets:
            if not formset['formset'].is_valid():
                all_valid = False

        if all_valid:
            for formset in formsets:
                instances = formset['formset'].save(commit=False)
                for instance in instances:
                    # If the setting has already a set, we are editing...
                    try:
                        instance.set

                        # Check that we are allowed to do this
                        if instance.get_owner_object().user != request.user:
                            return HttpResponseForbidden()

                        instance.save()

                    # ...if not, create a new setting
                    except ObjectDoesNotExist:
                        instance.set = set_obj
                        instance.order = 1
                        instance.exercise = formset['exercise']
                        instance.save()

            return HttpResponseRedirect(reverse('manager:workout:view',
                                        kwargs={'pk': set_obj.get_owner_object().id}))

    # Other context we need
    context = {}
    context['formsets'] = formsets
    context['form_action'] = reverse('manager:set:edit', kwargs={'pk': pk})
    return render(request, 'set/edit.html', context)
