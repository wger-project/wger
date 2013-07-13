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

'''
Simple script that filters the output of django's dumpdata command into more
manageable chunks.

Create the data.json e.g. with:
    python ../../manage.py dumpdata --indent=4 > data.json
'''

import json


def filter_dump(data, model_list, filename):
    '''
    Helper function
    '''
    filter_data = [i for i in data if i['model'] in model_list]
    with open(filename, 'w') as outfile:
        json.dump(filter_data, outfile, indent=4)

# This is a full dump of the DB
fixture = open('data.json')
data = json.load(fixture)
fixture.close()

#
# Ingredients
#
filter_dump(data, ('nutrition.ingredient',), 'ingredients.json')
filter_dump(data, ('nutrition.weightunit',), 'weight_units.json')
filter_dump(data, ('nutrition.ingredientweightunit',), 'ingredient_units.json')

#
# Exercises
#
filter_dump(data, ('exercises.muscle',), 'muscles.json')
filter_dump(data, ('exercises.exercisecategory',), 'categories.json')
filter_dump(data, ('exercises.exercise', 'exercises.exercisecomment',), 'exercises.json')

#
# Other
#
filter_dump(data, ('exercises.language',), 'languages.json')
filter_dump(data, ('config.languageconfig',), 'language_config.json')
