#!/usr/bin/env python3

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

"""
Simple script that filters the output of django's dumpdata command into more
manageable chunks.

After dumping the database (or parts of it), just copy the file and filter it:
    python ./manage.py dumpdata --indent 4 --natural-foreign exercises > extras/scripts/data.json
    cd extras/scripts
    python3 filter-fixtures.py
    mv categories.json muscles.json equipment.json translations.json exercise-base-data.json ../../wger/exercises/fixtures
    ...
    rm *.json
"""

import json
import sys


def filter_dump(data, model_list, filename):
    """
    Helper function
    """
    model_set = set(model_list)
    filter_data = [i for i in data if i['model'] in model_set]
    if not filter_data:
        # print(f'Warning: no data found for {model_list}')
        return

    with open(filename, 'w') as outfile:
        json.dump(filter_data, outfile, indent=4)


def main():
    # This is a full dump of the DB
    try:
        with open('data.json') as fixture:
            data = json.load(fixture)
    except FileNotFoundError:
        sys.exit('Error: data.json not found. Please run dumpdata first (see docstring for usage).')
    except json.JSONDecodeError as e:
        sys.exit(f'Error: data.json contains invalid JSON: {e}')

    #
    # Ingredients
    #
    filter_dump(data, ('nutrition.ingredient',), 'ingredients.json')
    filter_dump(data, ('nutrition.weightunit',), 'weight_units.json')
    filter_dump(data, ('nutrition.ingredientweightunit',), 'ingredient_units.json')
    filter_dump(data, ('nutrition.logitem',), 'nutrition_diary.json')

    #
    # Exercises
    #
    filter_dump(data, ('exercises.muscle',), 'muscles.json')
    filter_dump(data, ('exercises.exercisecategory',), 'categories.json')
    filter_dump(data, ('exercises.exerciseimage',), 'exercise-images.json')
    filter_dump(
        data,
        (
            'exercises.exercise',
            'exercises.variation',
        ),
        'exercise-base-data.json',
    )
    filter_dump(
        data,
        ('exercises.translation', 'exercises.exercisecomment', 'exercises.alias'),
        'translations.json',
    )
    filter_dump(data, ('exercises.equipment',), 'equipment.json')

    #
    # Gym
    #
    filter_dump(data, ('gym.gym',), 'gyms.json')
    filter_dump(data, ('gym.gymconfig',), 'gym_config.json')
    filter_dump(data, ('gym.gymadminconfig',), 'gym_adminconfig.json')
    filter_dump(data, ('gym.gymuserconfig',), 'gym_userconfig.json')
    filter_dump(data, ('gym.adminusernote',), 'gym_admin_user_notes.json')
    filter_dump(data, ('gym.userdocument',), 'gym_user_documents.json')
    filter_dump(data, ('gym.contract',), 'gym_contracts.json')

    #
    # Core
    #
    filter_dump(data, ('core.gym',), 'gyms.json')
    filter_dump(data, ('core.language',), 'languages.json')
    filter_dump(data, ('core.license',), 'licenses.json')
    filter_dump(data, ('core.repetitionunit',), 'repetition_units.json')

    #
    # Configurations
    #
    filter_dump(data, ('config.gymconfig',), 'gym_config.json')

    #
    # Other
    #
    filter_dump(data, ('auth.group',), 'groups.json')
    filter_dump(data, ('auth.user',), 'users.json')


if __name__ == '__main__':
    main()
