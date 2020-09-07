# -*- coding: utf-8 -*-

import os
import xml.etree.cElementTree as ET
import base64

from xml.dom import minidom

from django.conf import settings
from django.shortcuts import render

from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView
)

from wger.exercises.models import (
    Exercise,
    ExerciseCategory,
    Muscle
)

from django.http import HttpResponse

from wger.config.models import LanguageConfig
from wger.utils.language import (
    load_item_languages,
    load_language
)

class ExerciseExportOverview (ListView):
    model = Exercise
    template_name = "export/overview.html"
    context_object_name="number_exercises"
    
    def get_context_data(self, **kwargs):
        exercise = Exercise()
        context = super(ExerciseExportOverview, self).get_context_data(**kwargs)
        context["number_exercises"] = Exercise.objects.count()
        context["number_exercices_by_language"] = exercise.get_exercises_count_by_current_language()

        return context

class ExcercisesExporter:
    def export_exercises(self, exercises_list):
        root = ET.Element("exercises")

        for _exercise in exercises_list:
            _muscles = _exercise.muscles.all()
            _muscles_secondary = _exercise.muscles_secondary.all()
            _equipments = _exercise.equipment.all()
            _category = _exercise.category
            _language = _exercise.language
            _str_date = _exercise.creation_date.strftime("%Y-%m-%dT%H:%M:%S") if _exercise.creation_date else ""
            _images_list = _exercise.exerciseimage_set   

            _item_exercise = ET.SubElement(
                root,
                "exercice",
                name=_exercise.name,
                author=_exercise.license_author,
                status=_exercise.status,
                creation_date=_str_date,
                category=_category.name,
                license=_exercise.license.short_name,
                language=_language.short_name
            )
            _item_exercise.text = base64.b64encode(bytes(_exercise.description, "utf-8")).decode("utf-8")
            
            _item_muscles = ET.SubElement(
                _item_exercise,
                "muscles",
                main_muscles_count=str(_muscles.count()),
                secondary_muscles_count=str(_muscles_secondary.count())
            )

            _item_equipments = ET.SubElement(
                _item_exercise,
                "equipments"
            )

            _item_images = False

            if _images_list.count() > 0:
                _item_images = ET.SubElement(
                    _item_exercise,
                    "images"
                )

            for _muscle in _muscles:
                _muscle_name = _muscle.name
                _item_muscle = ET.SubElement(
                    _item_muscles,
                    "muscle",
                    type="main"
                )
                _item_muscle.text = _muscle_name

            for _muscle in _muscles_secondary:
                _muscle_name = _muscle.name
                _item_muscle = ET.SubElement(
                    _item_muscles,
                    "muscle",
                    type="secondary"
                )
                _item_muscle.text = _muscle_name
            
            for _equipment in _equipments:
                _item_equipment = ET.SubElement(
                    _item_equipments,
                    "equipment"
                )
                _item_equipment.text = _equipment.name

            if _item_images is not False:
                print("blep")
                for _image in _images_list.all():
                    # Extracting filename from path
                    _image_name = os.path.basename(_image.image.path)
                    _is_main = _image.is_main
                    _item_image = ET.SubElement(
                        _item_images,
                        "image",
                        name=_image_name,
                        is_main=str(_is_main)
                    )

                    # Opening image
                    with open(_image.image.path, 'rb') as _image_file:
                        _raw_image = _image_file.read()
                        _b64_image = base64.b64encode(_raw_image)

                        _item_image.text = _b64_image.decode("utf-8")


        raw_string = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(raw_string)
        return reparsed.toprettyxml(indent="\t")

def export_all_exercices(request):
    exporter = ExcercisesExporter()

    exercices_list = Exercise.objects.all()

    xml_export = exporter.export_exercises(exercices_list)

    response = HttpResponse(xml_export, content_type="application/xml")
    response["Content-Disposition"] = "attachment; filename=wger_exercices.xml"

    return response

def export_exercises_for_current_language(request):
    languages = load_item_languages(LanguageConfig.SHOW_ITEM_EXERCISES)

    # Assuming there is only one language...
    filename = "wger_" + languages[0].short_name + "_exercises.xml"
    exercise = Exercise()
    exercises_list = exercise.get_exercises_by_current_language()

    exporter = ExcercisesExporter()
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