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

"""
Simple script that filters the output of django's dumpdata command into more
manageable chunks.

After dumping the database (or parts of it), just copy the file and filter it:
    python ./manage.py dumpdata --indent 4 --natural-foreign > extras/scripts/data.json
    cd extras/scripts
    python3 filter-fixtures.py
    mv exercises.json ../../wger/exercises/fixtures/
    ...
    rm *.json
"""

import json

# This is a full dump of the DB
fixture = open('data.json')
data = json.load(fixture)
fixture.close()


def filter_dump(model_list, filename):
    """
    Helper function
    """
    filter_data = [i for i in data if i['model'] in model_list]
    if filter_data:
        with open(filename, 'w') as outfile:
            # Filter out submission models that are not accepted, if an entry
            # has no 'status' field, add them all
            out_data = [entry for entry in filter_data if entry['fields'].get('status', '2') == '2']
            json.dump(out_data, outfile, indent=4)


#
# Ingredients
#
filter_dump(('nutrition.ingredient',), 'ingredients.json')
filter_dump(('nutrition.weightunit',), 'weight_units.json')
filter_dump(('nutrition.ingredientweightunit',), 'ingredient_units.json')
filter_dump(('nutrition.logitem',), 'nutrition_diary.json')

#
# Exercises
#
filter_dump(('exercises.muscle',), 'muscles.json')
filter_dump(('exercises.exercisecategory',), 'categories.json')
filter_dump(('exercises.exerciseimage',), 'exercise-images.json')
filter_dump(
    (
        'exercises.exercisebase',
        'exercises.variation',
    ),
    'exercise-base-data.json',
)
filter_dump(
    ('exercises.exercise', 'exercises.exercisecomment', 'exercises.alias'), 'translations.json'
)
filter_dump(
    (
        'exercises.equipment',
        'exercises.equipment',
    ),
    'equipment.json',
)

#
# Gym
#
filter_dump(('gym.gym',), 'gyms.json')
filter_dump(('gym.gymconfig',), 'gym_config.json')
filter_dump(('gym.gymadminconfig',), 'gym_adminconfig.json')
filter_dump(('gym.gymuserconfig',), 'gym_userconfig.json')
filter_dump(('gym.adminusernote',), 'gym_admin_user_notes.json')
filter_dump(('gym.userdocument',), 'gym_user_documents.json')
filter_dump(('gym.contract',), 'gym_contracts.json')

#
# Core
#
filter_dump(('core.gym',), 'gyms.json')
filter_dump(('core.language',), 'languages.json')
filter_dump(('core.license',), 'licenses.json')
filter_dump(('core.repetitionunit',), 'repetition_units.json')

#
# Configurations
#
filter_dump(('config.gymconfig',), 'gym_config.json')

#
# Other
#
filter_dump(('auth.group',), 'groups.json')
filter_dump(('auth.user',), 'users.json')
