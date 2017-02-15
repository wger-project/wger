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
import uuid
from django.core import mail

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.forms import (
    ModelForm,
    ModelChoiceField,
    ModelMultipleChoiceField
)
from django.core.cache import cache
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.views.generic import (
    ListView,
    DeleteView,
    CreateView,
    UpdateView
)

from wger.manager.models import WorkoutLog
from wger.exercises.models import (
    Exercise,
    Muscle,
    ExerciseCategory
)
from wger.utils.generic_views import (
    WgerFormMixin,
    WgerDeleteMixin
)
from wger.utils.language import load_language, load_item_languages
from wger.utils.cache import cache_mapper
from wger.utils.widgets import (
    TranslatedSelect,
    TranslatedSelectMultiple,
    TranslatedOriginalSelectMultiple
)
from wger.config.models import LanguageConfig
from wger.weight.helpers import process_log_entries


logger = logging.getLogger(__name__)


class ExerciseListView(ListView):
    '''
    Generic view to list all exercises
    '''

    model = Exercise
    template_name = 'exercise/overview.html'
    context_object_name = 'exercises'

    def get_queryset(self):
        '''
        Filter to only active exercises in the configured languages
        '''
        languages = load_item_languages(LanguageConfig.SHOW_ITEM_EXERCISES)
        return Exercise.objects.accepted() \
            .filter(language__in=languages) \
            .order_by('category__id') \
            .select_related()

    def get_context_data(self, **kwargs):
        '''
        Pass additional data to the template
        '''
        context = super(ExerciseListView, self).get_context_data(**kwargs)
        context['show_shariff'] = True
        return context


def view(request, id, slug=None):
    '''
    Detail view for an exercise
    '''

    template_data = {}
    template_data['comment_edit'] = False
    template_data['show_shariff'] = True

    exercise = get_object_or_404(Exercise, pk=id)

    template_data['exercise'] = exercise

    # Create the backgrounds that show what muscles the exercise works on
    backgrounds = cache.get(cache_mapper.get_exercise_muscle_bg_key(int(id)))
    if not backgrounds:
        backgrounds_back = []
        backgrounds_front = []

        for muscle in exercise.muscles.all():
            if muscle.is_front:
                backgrounds_front.append('images/muscles/main/muscle-%s.svg' % muscle.id)
            else:
                backgrounds_back.append('images/muscles/main/muscle-%s.svg' % muscle.id)

        for muscle in exercise.muscles_secondary.all():
            if muscle.is_front:
                backgrounds_front.append('images/muscles/secondary/muscle-%s.svg' % muscle.id)
            else:
                backgrounds_back.append('images/muscles/secondary/muscle-%s.svg' % muscle.id)

        # Append the "main" background, with the silhouette of the human body
        # This has to happen as the last step, so it is rendered behind the muscles.
        backgrounds_front.append('images/muscles/muscular_system_front.svg')
        backgrounds_back.append('images/muscles/muscular_system_back.svg')
        backgrounds = (backgrounds_front, backgrounds_back)

        cache.set(cache_mapper.get_exercise_muscle_bg_key(int(id)),
                  (backgrounds_front, backgrounds_back))

    template_data['muscle_backgrounds_front'] = backgrounds[0]
    template_data['muscle_backgrounds_back'] = backgrounds[1]

    # If the user is logged in, load the log and prepare the entries for
    # rendering in the D3 chart
    entry_log = []
    chart_data = []
    if request.user.is_authenticated():
        logs = WorkoutLog.objects.filter(user=request.user, exercise=exercise)
        entry_log, chart_data = process_log_entries(logs)

    template_data['logs'] = entry_log
    template_data['json'] = chart_data
    template_data['svg_uuid'] = str(uuid.uuid4())

    return render(request, 'exercise/view.html', template_data)


class ExercisesEditAddView(WgerFormMixin):
    '''
    Generic view to subclass from for exercise adding and editing, since they
    share all this settings
    '''
    model = Exercise
    sidebar = 'exercise/form.html'
    title = ugettext_lazy('Add exercise')
    custom_js = 'wgerInitTinymce();'
    clean_html = ('description', )

    def get_form_class(self):

        # Define the exercise form here because only at this point during the request
        # have we access to the currently used language. In other places Django defaults
        # to 'en-us'.
        class ExerciseForm(ModelForm):
            category = ModelChoiceField(queryset=ExerciseCategory.objects.all(),
                                        widget=TranslatedSelect())
            muscles = ModelMultipleChoiceField(queryset=Muscle.objects.all(),
                                               widget=TranslatedOriginalSelectMultiple(),
                                               required=False)

            muscles_secondary = ModelMultipleChoiceField(queryset=Muscle.objects.all(),
                                                         widget=TranslatedOriginalSelectMultiple(),
                                                         required=False)

            class Meta:
                model = Exercise
                widgets = {'equipment': TranslatedSelectMultiple()}
                fields = ['name_original',
                          'category',
                          'description',
                          'muscles',
                          'muscles_secondary',
                          'equipment',
                          'license',
                          'license_author']

            class Media:
                js = ('/static/bower_components/tinymce/tinymce.min.js',)

        return ExerciseForm


class ExerciseUpdateView(ExercisesEditAddView,
                         LoginRequiredMixin,
                         PermissionRequiredMixin,
                         UpdateView):
    '''
    Generic view to update an existing exercise
    '''
    permission_required = 'exercises.change_exercise'

    def get_context_data(self, **kwargs):
        context = super(ExerciseUpdateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('exercise:exercise:edit', kwargs={'pk': self.object.id})
        context['title'] = _(u'Edit {0}').format(self.object.name)

        return context


class ExerciseAddView(ExercisesEditAddView, LoginRequiredMixin, CreateView):
    '''
    Generic view to add a new exercise
    '''

    form_action = reverse_lazy('exercise:exercise:add')

    def form_valid(self, form):
        '''
        Set language, author and status
        '''
        form.instance.language = load_language()
        form.instance.set_author(self.request)
        return super(ExerciseAddView, self).form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        '''
        Demo users can't submit exercises
        '''
        if request.user.userprofile.is_temporary:
            return HttpResponseForbidden()

        return super(ExerciseAddView, self).dispatch(request, *args, **kwargs)


class ExerciseCorrectView(ExercisesEditAddView, LoginRequiredMixin, UpdateView):
    '''
    Generic view to update an existing exercise
    '''
    sidebar = 'exercise/form_correct.html'
    messages = _('Thank you. Once the changes are reviewed the exercise will be updated.')

    def dispatch(self, request, *args, **kwargs):
        '''
        Only registered users can correct exercises
        '''
        if not request.user.is_authenticated() or request.user.userprofile.is_temporary:
            return HttpResponseForbidden()

        return super(ExerciseCorrectView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ExerciseCorrectView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('exercise:exercise:correct', kwargs={'pk': self.object.id})
        context['title'] = _(u'Correct {0}').format(self.object.name)
        return context

    def form_valid(self, form):
        '''
        If the form is valid send email notifications to the site administrators.

        We don't return the super().form_valid because we don't want the data
        to be saved.
        '''
        subject = 'Correction submitted for exercise #{0}'.format(self.get_object().pk)
        context = {
            'exercise': self.get_object(),
            'form_data': form.cleaned_data,
            'user': self.request.user
        }
        message = render_to_string('exercise/email_correction.tpl', context)
        mail.mail_admins(six.text_type(subject),
                         six.text_type(message),
                         fail_silently=True)

        messages.success(self.request, self.messages)
        return HttpResponseRedirect(reverse('exercise:exercise:view',
                                            kwargs={'id': self.object.id}))


class ExerciseDeleteView(WgerDeleteMixin,
                         LoginRequiredMixin,
                         PermissionRequiredMixin,
                         DeleteView):
    '''
    Generic view to delete an existing exercise
    '''

    model = Exercise
    fields = ('category',
              'description',
              'name_original',
              'muscles',
              'muscles_secondary',
              'equipment')
    success_url = reverse_lazy('exercise:exercise:overview')
    delete_message = ugettext_lazy('This will delete the exercise from all workouts.')
    messages = ugettext_lazy('Successfully deleted')
    permission_required = 'exercises.delete_exercise'

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(ExerciseDeleteView, self).get_context_data(**kwargs)
        context['title'] = _(u'Delete {0}?').format(self.object.name)
        context['form_action'] = reverse('exercise:exercise:delete',
                                         kwargs={'pk': self.kwargs['pk']})

        return context


class PendingExerciseListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    '''
    Generic view to list all weight units
    '''

    model = Exercise
    template_name = 'exercise/pending.html'
    context_object_name = 'exercise_list'
    permission_required = 'exercises.change_exercise'

    def get_queryset(self):
        '''
        Only show pending exercises
        '''
        return Exercise.objects.pending().order_by('-creation_date')


@permission_required('exercises.add_exercise')
def accept(request, pk):
    '''
    Accepts a pending user submitted exercise and emails the user, if possible
    '''
    exercise = get_object_or_404(Exercise, pk=pk)
    exercise.status = Exercise.STATUS_ACCEPTED
    exercise.save()
    exercise.send_email(request)
    messages.success(request, _('Exercise was successfully added to the general database'))

    return HttpResponseRedirect(exercise.get_absolute_url())


@permission_required('exercises.add_exercise')
def decline(request, pk):
    '''
    Declines and deletes a pending user submitted exercise
    '''
    exercise = get_object_or_404(Exercise, pk=pk)
    exercise.status = Exercise.STATUS_DECLINED
    exercise.save()
    messages.success(request, _('Exercise was successfully marked as rejected'))
    return HttpResponseRedirect(exercise.get_absolute_url())
