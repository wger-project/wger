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
import json
import uuid

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.forms import ModelForm
from django.forms import ModelChoiceField
from django.core import mail
from django.core.cache import cache
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from django.views.generic import ListView
from django.views.generic import DeleteView
from django.views.generic import CreateView
from django.views.generic import UpdateView

from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.alias import aliases

from wger.manager.models import WorkoutLog

from wger.exercises.models import Exercise
from wger.exercises.models import ExerciseCategory

from wger.utils.generic_views import WgerFormMixin
from wger.utils.generic_views import WgerDeleteMixin
from wger.utils.generic_views import WgerPermissionMixin
from wger.utils.language import load_language
from wger.utils.language import load_item_languages
from wger.utils.cache import cache_mapper
from wger.utils.widgets import TranslatedSelect
from wger.utils.widgets import TranslatedSelectMultiple
from wger.config.models import LanguageConfig


logger = logging.getLogger('wger.custom')


def overview(request):
    '''
    Overview with all exercises
    '''
    languages = load_item_languages(LanguageConfig.SHOW_ITEM_EXERCISES)

    template_data = {}
    template_data.update(csrf(request))

    #logger.debug(languages)
    categories = ExerciseCategory.objects.all()

    template_data['categories'] = categories
    template_data['active_languages'] = languages

    return render_to_response('overview.html',
                              template_data,
                              context_instance=RequestContext(request))


def view(request, id, slug=None):
    '''
    Detail view for an exercise
    '''

    template_data = {}
    template_data['comment_edit'] = False

    # Load the exercise itself
    exercise = cache.get(cache_mapper.get_exercise_key(int(id)))
    if not exercise:
        exercise = get_object_or_404(Exercise, pk=id)
        cache.set(cache_mapper.get_exercise_key(exercise), exercise)

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
        entry = WorkoutLog()
        logs = WorkoutLog.objects.filter(user=request.user, exercise=exercise)
        entry_log, chart_data = entry.process_log_entries(logs)

    template_data['logs'] = entry_log
    template_data['json'] = chart_data
    template_data['svg_uuid'] = str(uuid.uuid4())
    template_data['reps'] = _("Reps")

    # Render
    return render_to_response('view.html',
                              template_data,
                              context_instance=RequestContext(request))


class ExercisesEditAddView(WgerFormMixin):
    '''
    Generic view to subclass from for exercise adding and editing, since they
    share all this settings
    '''
    model = Exercise
    sidebar = 'exercise/form.html'

    form_fields = ['name',
                   'category',
                   'muscles',
                   'muscles_secondary',
                   'description',
                   'equipment']

    title = ugettext_lazy('Add exercise')
    custom_js = 'init_tinymce();'
    clean_html = ('description', )

    def get_form_class(self):

        # Define the exercise form here because only at this point during the request
        # have we access to the currently used language. In other places Django defaults
        # to 'en-us'.
        class ExerciseForm(ModelForm):
            #language = load_language()
            category = ModelChoiceField(queryset=ExerciseCategory.objects.all(),
                                        widget=TranslatedSelect())

            class Meta:
                model = Exercise
                widgets = {'equipment': TranslatedSelectMultiple()}

            class Media:
                js = ('js/tinymce/tinymce.min.js',)

        return ExerciseForm


class ExerciseUpdateView(ExercisesEditAddView, UpdateView, WgerPermissionMixin):
    '''
    Generic view to update an existing exercise
    '''

    permission_required = 'exercises.change_exercise'

    def form_valid(self, form):
        '''
        Set the user field, otherwise it will get reset to Null
        '''

        form.instance.user = Exercise.objects.get(pk=self.object.id).user
        return super(ExerciseUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ExerciseUpdateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('exercise-edit', kwargs={'pk': self.object.id})
        context['title'] = _('Edit %s') % self.object.name

        return context


class ExerciseAddView(ExercisesEditAddView, CreateView, WgerPermissionMixin):
    '''
    Generic view to add a new exercise
    '''

    login_required = True
    form_action = reverse_lazy('exercise-add')

    def form_valid(self, form):
        '''
        Set the user that submitted the exercise
        '''

        # set the submitter, if admin, set approrpiate status
        form.instance.user = self.request.user.username
        form.instance.language = load_language()
        if self.request.user.has_perm('exercises.add_exercise'):
            form.instance.status = Exercise.EXERCISE_STATUS_ADMIN
        else:
            subject = _('New user submitted exercise')
            message = _('''The user {0} submitted a new exercise "{1}".'''.format(
                        self.request.user.username, form.instance.name))
            mail.mail_admins(subject,
                             message,
                             fail_silently=True)

        return super(ExerciseAddView, self).form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        '''
        Demo users can't submit exercises
        '''
        if request.user.userprofile.is_temporary:
            return HttpResponseForbidden()

        return super(ExerciseAddView, self).dispatch(request, *args, **kwargs)


class ExerciseDeleteView(WgerDeleteMixin, DeleteView):
    '''
    Generic view to delete an existing exercise
    '''

    model = Exercise
    success_url = reverse_lazy('wger.exercises.views.exercises.overview')
    delete_message = ugettext_lazy('This will delete the exercise from all workouts.')
    messages = ugettext_lazy('Exercise successfully deleted')
    permission_required = 'exercises.delete_exercise'

    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(ExerciseDeleteView, self).get_context_data(**kwargs)

        context['title'] = _('Delete exercise %s?') % self.object.name
        context['form_action'] = reverse('exercise-delete', kwargs={'pk': self.kwargs['pk']})

        return context


class PendingExerciseListView(WgerPermissionMixin, ListView):
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
        return Exercise.objects.filter(status=Exercise.EXERCISE_STATUS_PENDING)


@permission_required('exercises.add_exercise')
def accept(request, pk):
    '''
    Accepts a pending user submitted exercise and emails the user, if possible
    '''
    exercise = get_object_or_404(Exercise, pk=pk)
    exercise.status = Exercise.EXERCISE_STATUS_ACCEPTED
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
    exercise.status = Exercise.EXERCISE_STATUS_DECLINED
    exercise.save()
    messages.success(request, _('Exercise was successfully marked as rejected'))
    return HttpResponseRedirect(exercise.get_absolute_url())


def search(request):
    '''
    Search an exercise, return the result as a JSON list
    '''

    # Perform the search
    q = request.GET.get('term', '')

    languages = load_item_languages(LanguageConfig.SHOW_ITEM_EXERCISES)
    exercises = (Exercise.objects.filter(name__icontains=q)
                                 .filter(language__in=languages)
                                 .filter(status__in=Exercise.EXERCISE_STATUS_OK)
                                 .order_by('category__name', 'name')
                                 .distinct())

    # AJAX-request, this comes from the autocompleter. Create a list and send
    # it back as JSON
    if request.is_ajax():

        results = []
        for exercise in exercises:
            if exercise.exerciseimage_set.exists():
                image_obj = exercise.exerciseimage_set.filter(is_main=True)[0]
                image = image_obj.image.url
                t = get_thumbnailer(image_obj.image)
                thumbnail = t.get_thumbnail(aliases.get('micro_cropped')).url
            else:
                image = None
                thumbnail = None

            exercise_json = {}
            exercise_json['id'] = exercise.id
            exercise_json['name'] = exercise.name
            exercise_json['value'] = exercise.name
            exercise_json['category'] = exercise.category.name
            exercise_json['image'] = image
            exercise_json['image_thumbnail'] = thumbnail

            results.append(exercise_json)
        data = json.dumps(results)

        # Return the results to the server
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)

    # Usual search (perhaps JS disabled), present the results as normal HTML page
    else:
        template_data = {}
        template_data.update(csrf(request))
        template_data['exercises'] = exercises
        template_data['search_term'] = q
        return render_to_response('exercise_search.html',
                                  template_data,
                                  context_instance=RequestContext(request))
