# -*- coding: utf-8 -*-

# This file is part of Workout Manager.
#
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Workout Manager is distributed in the hope that it will be useful,
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
from django.forms import ModelForm
from django.forms import ModelChoiceField
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import permission_required
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.utils.datastructures import SortedDict

from django.views.generic import DeleteView
from django.views.generic import CreateView
from django.views.generic import UpdateView

from manager.utils import load_language

from manager.models import WorkoutLog

from exercises.models import Exercise
from exercises.models import ExerciseComment
from exercises.models import ExerciseCategory
from exercises.models import Muscle

from workout_manager.generic_views import YamlFormMixin
from workout_manager.generic_views import YamlDeleteMixin
from workout_manager.constants import EXERCISE_TAB


logger = logging.getLogger('workout_manager.custom')


# ************************
#    Exercise comments
# ************************
class ExerciseCommentForm(ModelForm):
    class Meta:
        model = ExerciseComment
        exclude = ('exercise',)


class ExerciseCommentEditView(YamlFormMixin, UpdateView):
    """
    Generic view to update an existing exercise comment
    """

    active_tab = EXERCISE_TAB
    model = ExerciseComment
    form_class = ExerciseCommentForm
    title = ugettext_lazy('Edit exercise comment')

    def get_success_url(self):
        return reverse('exercises.views.exercise_view', kwargs={'id': self.object.exercise.id})

    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(ExerciseCommentEditView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('exercisecomment-edit',
                                         kwargs={'pk': self.object.id})

        return context


class ExerciseCommentAddView(YamlFormMixin, CreateView):
    """
    Generic view to add a new exercise comment
    """

    active_tab = EXERCISE_TAB
    model = ExerciseComment
    form_class = ExerciseCommentForm
    title = ugettext_lazy('Add exercise comment')

    def form_valid(self, form):
        form.instance.exercise = Exercise.objects.get(pk=self.kwargs['exercise_pk'])

        return super(ExerciseCommentAddView, self).form_valid(form)

    def get_success_url(self):
        return reverse('exercises.views.exercise_view', kwargs={'id': self.object.exercise.id})

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(ExerciseCommentAddView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('exercisecomment-add',
                                         kwargs={'exercise_pk': self.kwargs['exercise_pk']})

        return context


@permission_required('manager.add_exercisecomment')
def exercisecomment_delete(request, id):
    # Load the comment
    comment = get_object_or_404(ExerciseComment, pk=id)
    exercise_id = comment.exercise.id
    comment.delete()

    return HttpResponseRedirect(reverse('exercises.views.exercise_view', kwargs={'id': exercise_id}))


# ************************
#         Exercises
# ************************
def exercise_overview(request):
    """Overview with all exercises
    """
    language = load_language()

    template_data = {}
    template_data.update(csrf(request))

    template_data['categories'] = ExerciseCategory.objects.filter(language=language.id)
    template_data['active_tab'] = EXERCISE_TAB

    return render_to_response('overview.html',
                              template_data,
                              context_instance=RequestContext(request))


from django.views.generic import ListView

class MuscleListView(ListView):
    '''
    Overview of all muscles and their exercises
    '''
    model = Muscle
    queryset = Muscle.objects.all().order_by('-is_front', 'name'),
    context_object_name = 'muscle_list'
    template_name = 'muscle_overview.html'

    def get_context_data(self, **kwargs):
        '''
        Set the language and navigation tab
        '''
        context = super(MuscleListView, self).get_context_data(**kwargs)
        context['language'] = load_language()
        context['active_tab'] = EXERCISE_TAB
        
        return context

def exercise_view(request, id, comment_id=None):
    """ Detail view for an exercise
    """

    template_data = {}
    template_data['comment_edit'] = False

    # Load the exercise itself
    exercise = get_object_or_404(Exercise, pk=id)
    template_data['exercise'] = exercise
    template_data['active_tab'] = EXERCISE_TAB

    # Create the backgrounds that show what muscles the exercise works on
    backgrounds_back = []
    backgrounds_front = []

    for muscle in exercise.muscles.all():
        if muscle.is_front:
            backgrounds_front.append('images/muscles/main/muscle-%s.svg' % muscle.id)
        else:
            backgrounds_back.append('images/muscles/main/muscle-%s.svg' % muscle.id)

    # Append the "main" background, with the silhouette of the human body
    # This has to happen as the last step, so it is rendered behind the muscles.
    if backgrounds_front:
        backgrounds_front.append('images/muscles/muscular_system_front.svg')

    if backgrounds_back:
        backgrounds_back.append('images/muscles/muscular_system_back.svg')

    template_data['muscle_backgrounds_front'] = backgrounds_front
    template_data['muscle_backgrounds_back'] = backgrounds_back

    # Load log and prepare the entries for rendering and the D3 chart
    entry = WorkoutLog()
    logs = WorkoutLog.objects.filter(user=request.user,
                                     exercise=exercise)

    entry_log, chart_data = entry.process_log_entries(logs)

    template_data['logs'] = entry_log
    template_data['json'] = chart_data
    template_data['svg_uuid'] = str(uuid.uuid4())
    template_data['reps'] = _("Reps")

    # Render
    return render_to_response('view.html',
                              template_data,
                              context_instance=RequestContext(request))


class ExercisesEditAddView(YamlFormMixin):
    """
    Generic view to subclass from for exercise adding and editing, since they
    share all this settings
    """
    active_tab = EXERCISE_TAB
    model = Exercise

    form_fields = ['name',
                   'category',
                   'muscles',
                   'description']

    select_lists = ['category']
    title = ugettext_lazy('Add exercise')
    custom_js = 'init_tinymce();'

    def get_form_class(self):

        # Define the exercise form here because only at this point during the request
        # have we access to the currently used language. In other places Django defaults
        # to 'en-us'.
        class ExerciseForm(ModelForm):
            language = load_language()
            category = ModelChoiceField(queryset=ExerciseCategory.objects.filter(language=language.id))

            class Meta:
                model = Exercise

            class Media:
                js = ('js/tinymce/tiny_mce.js',)

        return ExerciseForm


class ExerciseUpdateView(ExercisesEditAddView, UpdateView):
    """
    Generic view to update an existing exercise
    """

    def get_context_data(self, **kwargs):
        context = super(ExerciseUpdateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('exercise-edit', kwargs={'pk': self.object.id})
        context['title'] = _('Edit %s') % self.object.name

        return context


class ExerciseAddView(ExercisesEditAddView, CreateView):
    """
    Generic view to add a new exercise
    """

    form_action = reverse_lazy('exercise-add')


class ExerciseDeleteView(YamlDeleteMixin, DeleteView):
    """
    Generic view to delete an existing exercise
    """

    model = Exercise
    active_tab = EXERCISE_TAB
    success_url = reverse_lazy('exercises.views.exercise_overview')
    delete_message = ugettext_lazy('This will delete the exercise from all workouts.')

    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(ExerciseDeleteView, self).get_context_data(**kwargs)

        context['title'] = _('Delete exercise %s?') % self.object.name
        context['form_action'] = reverse('exercise-delete', kwargs={'pk': self.kwargs['pk']})

        return context


def exercise_search(request):
    """Search an exercise, return the result as a JSON list
    """

    # Perform the search
    q = request.GET.get('term', '')
    user_language = load_language()
    exercises = Exercise.objects.filter(name__icontains=q, category__language_id=user_language)\
                                .order_by('category__name', 'name')

    # AJAX-request, this comes from the autocompleter. Create a list and send
    # it back as JSON
    if request.is_ajax():

        results = []
        for exercise in exercises:
            exercise_json = {}
            exercise_json['id'] = exercise.id
            exercise_json['name'] = exercise.name
            exercise_json['value'] = exercise.name
            exercise_json['category'] = exercise.category.name

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


# ************************
#   Exercise categories
# ************************
class ExerciseCategoryForm(ModelForm):
    class Meta:
        model = ExerciseCategory
        exclude = ('language',)


class ExerciseCategoryAddView(YamlFormMixin, CreateView):
    """
    Generic view to add a new exercise category
    """

    active_tab = EXERCISE_TAB
    model = ExerciseCategory
    form_class = ExerciseCategoryForm
    success_url = reverse_lazy('exercises.views.exercise_overview')
    title = ugettext_lazy('Add category')
    form_action = reverse_lazy('exercisecategory-add')

    def form_valid(self, form):
        form.instance.language = load_language()

        return super(ExerciseCategoryAddView, self).form_valid(form)


class ExerciseCategoryUpdateView(YamlFormMixin, UpdateView):
    """
    Generic view to update an existing exercise category
    """

    active_tab = EXERCISE_TAB
    model = ExerciseCategory
    form_class = ExerciseCategoryForm
    success_url = reverse_lazy('exercises.views.exercise_overview')

    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(ExerciseCategoryUpdateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('exercisecategory-edit', kwargs={'pk': self.object.id})
        context['title'] = _('Edit %s') % self.object.name

        return context

    def form_valid(self, form):
        form.instance.language = load_language()

        return super(ExerciseCategoryUpdateView, self).form_valid(form)


class ExerciseCategoryDeleteView(YamlDeleteMixin, DeleteView):
    """
    Generic view to delete an existing exercise category
    """

    model = ExerciseCategory
    success_url = reverse_lazy('exercises.views.exercise_overview')
    delete_message = ugettext_lazy('This will also delete all exercises in this category.')

    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(ExerciseCategoryDeleteView, self).get_context_data(**kwargs)

        context['title'] = _('Delete category %s?') % self.object.name
        context['form_action'] = reverse('exercise-delete', kwargs={'pk': self.kwargs['pk']})

        return context
