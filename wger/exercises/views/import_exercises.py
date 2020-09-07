# -*- coding: utf-8 -*-

import os
import datetime

import xml.etree.cElementTree as ET
import base64
import io

from xml.dom import minidom

from wger.exercises.forms import ImportExercisesForm
from wger.core.models import License, Language
from django.conf import settings
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.core.files import File

from django.utils.translation import (
    ugettext as _,
    ugettext_lazy
)

from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView
)

from wger.exercises.models import (
    Exercise,
    ExerciseCategory,
    ExerciseImage,
    Muscle,
    Equipment
)

from django.http import HttpResponse, HttpResponseRedirect

from wger.config.models import LanguageConfig
from wger.utils.language import (
    load_item_languages,
    load_language
)

class ExerciseImportOverview (ListView):
    model = Exercise
    template_name = "import/overview.html"
    context_object_name="number_exercises"

def import_overview(request):
    if request.method == 'POST':
        form = ImportExercisesForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                do_import(request.FILES['file'])
            except ET.ParseError:
                messages.warning(request, _("Cannot import file as it doesn't seems to be a valid XML"))
            else:
                messages.success(request, _("Successfully imported file!"))

            return HttpResponseRedirect(reverse("exercise:import:overview"))
    else:
        form = ImportExercisesForm()
    return render(request, 'import/overview.html', {'form': form})

def do_import(uploaded_file):
    file_content = bytes()
    file_name = uploaded_file.name

    file_content = _get_file_content(uploaded_file)

    root = ET.fromstring(file_content.decode("utf-8"))
    
    # Let's go!
    _parse_exercises(root)

    #print(file_content.decode("utf-8"))

def _get_file_content(file):
    content = bytes()

    for _data in file.chunks():
        content += _data

    return content

def _parse_exercises(xml_data):
    """
    Importer les exos puis les images car il faut l'id de l'exercice pour correctement positionner l'image dans le
    systeme de fichiers
    cf: models.py:351
    """
    for _exercise in xml_data:
        identity = _get_exercise_identity(_exercise)

        # Checking exercise existence based on the name
        # if exists skipping this iteration
        if _exercise_exists(identity["name"], identity["language"]):
            continue

        description = base64.b64decode(_exercise.text)
        muscles_list = _get_muscles(_exercise)
        equipment_list = _get_equipment(_exercise)

        print("Inserting exercise \"" + identity["name"] + "\" into database")

        exercise = Exercise()
        exercise.name = identity["name"]
        exercise.name_original = identity["name"]
        exercise.author = identity["author"]
        exercise.creation_date = identity["creation_date"]
        exercise.category = identity["category"]
        exercise.language = identity["language"]
        exercise.license = identity["license"]
        exercise.status = identity["status"]
        exercise.description = description

        exercise.save()

        for _muscle in muscles_list["main"]:
            exercise.muscles.add(_muscle)

        for _muscle in muscles_list["secondary"]:
            exercise.muscles_secondary.add(_muscle)

        for _equipment in equipment_list:
            exercise.equipment.add(_equipment)
        
        print("Exercise (" + str(exercise.id) + ")successfully inserted")

        images_xml = _get_images(_exercise)

        if images_xml:
            for _image in images_xml:
                exercise_image = ExerciseImage()
                exercise_image.exercise = exercise

                exercise_image.is_main = _image[2]

                # Decoding base64 image
                _byte_image = _image[0].text.encode("utf-8")
                raw_image_data = base64.b64decode(_byte_image)
                image_buffer = io.BytesIO(raw_image_data)

                exercise_image.image.save(
                    _image[1],
                    image_buffer
                )

                exercise_image.status = exercise_image.STATUS_ACCEPTED

                exercise_image.save()
        
        

def _get_exercise_identity(exercise_node):
    """
        Returns the attributes of the exercise in a dictionnary
        name,author,creation_date,category,language,status,licence
    """
    exercise_identity = dict()

    name = exercise_node.get("name")
    author = exercise_node.get("author")
    creation_date = exercise_node.get("creation_date")
    category = exercise_node.get("category")
    language = exercise_node.get("language")
    license = exercise_node.get("license")
    status = exercise_node.get("status")

    creation_date = datetime.datetime.strptime(creation_date, "%Y-%m-%dT%H:%M:%S")

    exercise_identity["name"] = name
    exercise_identity["author"] = author
    exercise_identity["creation_date"] = creation_date
    exercise_identity["status"] = status

    try:
        _db_category = ExerciseCategory.objects.get(name=category)
    except ObjectDoesNotExist:
        _db_category = ExerciseCategory(name=category)
    finally:
        exercise_identity["category"] = _db_category

    try:
        _db_language = Language.objects.get(short_name=language)
    except ObjectDoesNotExist:
        print("[WARNING]: Exercise " + name + " has no language!")
    else:
        exercise_identity["language"] = _db_language

    try:
        _db_license = License.objects.get(short_name=license)
    except ObjectDoesNotExist:
        print("[Warning]: " + license + " no such license")
    else:
        exercise_identity["license"] = _db_license


    return exercise_identity

def _get_muscles(exercise_node):
    """
    Returns a list of Muscle objects
    If the given muscle exists, it gets this one otherwise muscle is created
    """
    muscles_node = exercise_node.find("muscles")
    muscles_list = {"main": [], "secondary": []}

    if muscles_node is None:
        return False

    for _muscle in muscles_node:
        muscle_type = _muscle.get("type")
        muscle_name = _muscle.text

        try:
            _db_muscle = Muscle.objects.get(name=muscle_name)
        except ObjectDoesNotExist:
            print(muscle_name + " does not exists, creating it")
            _db_muscle = Muscle(name=muscle_name)
            _db_muscle.save()
            print(muscle_name + " successfully created(" + str(_db_muscle) + ")")
        finally:
            muscles_list[muscle_type].append(_db_muscle)

    return muscles_list

def _get_equipment(exercise_node):
    equipment_node = exercise_node.find("equipments")
    equipment_list = list()

    if equipment_node is None:
        return False

    for _equipment in equipment_node:
        equipment_name = _equipment.text

        try:
            _db_equipment = Equipment.objects.get(name=equipment_name)
        except ObjectDoesNotExist:
            print(equipment_name + " does not exists, creating")
            _db_equipment = Equipment(name=equipment_name)
            _db_equipment.save()
            print(equipment_name + " successfully created")
        finally:
            equipment_list.append(_db_equipment)

    return equipment_list

def _exercise_exists(exercise_name, language):
    _db_exercise = Exercise.objects.filter(name=exercise_name, language=language)
    
    if _db_exercise:
        for i in _db_exercise:
            print("Found exercise: " + i.name)
        return True

    return False

def _get_images(exercise_node):
    """
    Gets images of a given exercise from images node
    Returns a list of tuple (image_node, is_main_image)
    :param exercise_node:
    :return:
    """
    images_list = list()

    images_node = exercise_node.find("images")

    if images_node is None:
        return False

    for _image in images_node:
        _is_main = bool(_image.get("is_main"))
        _name = _image.get("name")

        _image_tuple = (_image, _name, _is_main)
        images_list.append(_image_tuple)

    return images_list
