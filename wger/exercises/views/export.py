# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import permission_required

from django.views.generic import ListView

from wger.exercises.models import Exercise

from django.contrib.auth.mixins import PermissionRequiredMixin

from django.http import HttpResponse, HttpResponseBadRequest

from wger.config.models import LanguageConfig
from wger.utils.language import load_item_languages

from wger.exercises import helpers


class ExerciseExportOverview (PermissionRequiredMixin, ListView):
    model = Exercise
    template_name = "export/overview.html"
    context_object_name = "number_exercises"
    permission_required = 'exercises.change_exercise'

    def get_context_data(self, **kwargs):
        exercise = Exercise()
        context = super(ExerciseExportOverview, self).get_context_data(**kwargs)
        context["number_exercises"] = Exercise.objects.count()
        context["number_exercices_by_language"] = exercise.get_exercises_count_by_current_language()

        return context


@permission_required('exercises.change_exercise')
def export_exercises(request, languages):
    exporter = helpers.ExcercisesExporter()

    filename = "wger_exercises.xml"

    print(languages)

    if languages == "all":
        exercises_list = Exercise.objects.all()
    elif languages == "user":
        languages = load_item_languages(LanguageConfig.SHOW_ITEM_EXERCISES)
        filename = "wger_" + languages[0].short_name + "_exercises.xml"
        exercise = Exercise()
        exercises_list = exercise.get_exercises_by_current_language()
    else:
        return HttpResponseBadRequest()

    xml_export = exporter.export_exercises(exercises_list)

    response = HttpResponse(xml_export, content_type="application/xml")
    response["Content-Disposition"] = "attachment; filename=" + filename

    return response


def _get_exercises_count_by_current_language():
    '''
    Filter to only active exercises in the configured languages
    '''
    languages = load_item_languages(LanguageConfig.SHOW_ITEM_EXERCISES)
    return Exercise.objects.accepted() \
        .filter(language__in=languages) \
        .order_by('category__id') \
        .select_related().count()


def _get_exercises_by_current_language():
    '''
    Filter to only active exercises in the configured languages
    '''
    languages = load_item_languages(LanguageConfig.SHOW_ITEM_EXERCISES)
    return Exercise.objects.accepted() \
        .filter(language__in=languages) \
        .order_by('category__id') \
        .select_related()
